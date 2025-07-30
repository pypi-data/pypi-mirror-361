from dataclasses import dataclass
from logging import getLogger
from typing import Any, Optional, cast

from .Command import Command, CommandArgs, ResponseType
from .CommandLifecycle import (
    CancelResponse,
    DeferResponse,
    ExecutionResponse,
    LifecycleResponse,
)
from .CommandResponse import CommandResponse, ResponseStatus
from .Dependencies import (
    DependencyAction,
    DependencyCheckResponse,
    ReasonByDependencyCheck,
)


@dataclass
class CommandLogEntry:
    """
    Represents a single command log entry.

    Contains the command and the responses from its lifecycle actions.

    Attributes:
        command (Command[Any, Any]): The command that was processed.
        responses (list[LifecycleResponse]): List of responses from the lifecycle actions of the command.
        dependency_response (DependencyCheckResponse): The response from the dependency check of the command.
    """

    command: Command[Any, Any]
    responses: list[LifecycleResponse]
    dependency_response: Optional[DependencyCheckResponse]


@dataclass
class QueueProcessResponse:
    """
    Response type of `CommandQueue.process_once()` and `CommandQueue.process_all()`.

    Contains information about the processing of commands in the queue.

    Attributes:
        command_log (list[CommandLogEntry]): List of all commands processed, along with all responses from their lifecycle actions.
        num_commands_processed (int): Total number of commands processed in this run.
        num_ingested (int): Number of commands that turned from `CREATED` to `PENDING` status.
        num_deferrals (int): Number of times a command was deferred.
        num_cancellations (int): Number of times a command was canceled.
        num_successes (int): Number of times a command executed and succeeded.
        num_failures (int): Number of times a command executed and failed.
        reached_max_iterations (bool): True if the maximum number of iterations was reached, false otherwise.
    """

    command_log: list[CommandLogEntry]
    num_commands_processed: int = 0
    num_ingested: int = 0
    num_deferrals: int = 0
    num_cancellations: int = 0
    num_successes: int = 0
    num_failures: int = 0
    reached_max_iterations: bool = False

    def __add__(self, other: "QueueProcessResponse") -> "QueueProcessResponse":
        """
        Add two QueueProcessResponse objects together.

        Args:
            other (QueueProcessResponse): The other QueueProcessResponse to add.

        Returns:
            QueueProcessResponse: A new QueueProcessResponse object with combined values.
        """
        return QueueProcessResponse(
            num_commands_processed=self.num_commands_processed + other.num_commands_processed,
            num_ingested=self.num_ingested + other.num_ingested,
            num_deferrals=self.num_deferrals + other.num_deferrals,
            num_cancellations=self.num_cancellations + other.num_cancellations,
            num_successes=self.num_successes + other.num_successes,
            num_failures=self.num_failures + other.num_failures,
            reached_max_iterations=self.reached_max_iterations or other.reached_max_iterations,
            command_log=self.command_log + other.command_log,
        )


class CommandQueue:
    def __init__(self):
        self._queue: list[Command[Any, Any]] = []
        self.logger = getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}@{id(self)}")

    def submit(self, command: Command[Any, ResponseType]) -> ResponseType:
        """
        Submit a command to the queue.

        Args:
            command (Command[ArgsType, ResponseType]): The command to be submitted.

        Returns:
            ResponseType: The response object associated with the command.
        """
        self._queue.append(command)
        return command.response

    def submit_many(self, *commands: Command[Any, Any]) -> list[CommandResponse]:
        """
        Submit multiple commands to the queue.

        Args:
            *commands (Command[ArgsType, ResponseType]): The commands to be submitted.

        Returns:
            list[ResponseType]: List of response objects associated with the submitted commands.
        """
        responses: list[CommandResponse] = []
        for command in commands:
            responses.append(self.submit(command))
        return responses

    def process_once(self, max_iterations: int = 1000) -> QueueProcessResponse:
        """
        Process all commands in the queue a single time.

        If a command is deferred, it will not be processed again until the next call to `process_once()`.

        Args:
            max_iterations (int, optional): Maximum number of commands to process in one call. Defaults to 1000.

        Returns:
            QueueProcessResponse: Response containing details of the processing.
        """
        response = QueueProcessResponse(command_log=[])
        to_remove: list[Command[Any, Any]] = []
        for command in self._queue:
            command_log_entry = CommandLogEntry(
                command=command, responses=[], dependency_response=None
            )
            if response.num_commands_processed >= max_iterations:
                response.reached_max_iterations = True
                break
            command = cast(Command[CommandArgs, CommandResponse], command)
            response.num_commands_processed += 1
            if command.response.status == ResponseStatus.CREATED:
                response.num_ingested += 1
                command.response.status = ResponseStatus.PENDING
            if command.response.status == ResponseStatus.PENDING:
                # check dependencies first
                dependency_response = command.check_dependencies()
                command_log_entry.dependency_response = dependency_response
                if dependency_response.status == DependencyAction.DEFER:
                    response.num_deferrals += 1
                    new_defer_response = DeferResponse(
                        should_proceed=False,
                        reason=ReasonByDependencyCheck(
                            f"Deferred due to dependency: {dependency_response.reasons}"
                        ),
                    )
                    command.call_on_defer_callbacks(new_defer_response)
                    command_log_entry.responses.append(new_defer_response)
                    response.command_log.append(command_log_entry)
                    continue
                elif dependency_response.status == DependencyAction.CANCEL:
                    response.num_cancellations += 1
                    new_cancel_response = CancelResponse(
                        should_proceed=False,
                        reason=ReasonByDependencyCheck(
                            f"Canceled due to dependency: {dependency_response.reasons}"
                        ),
                    )
                    command.call_on_cancel_callbacks(new_cancel_response)
                    command_log_entry.responses.append(new_cancel_response)
                    command.response.status = ResponseStatus.CANCELED
                    to_remove.append(command)
                    response.command_log.append(command_log_entry)
                    continue

                # check if we should defer
                defer_response = command.should_defer()
                command_log_entry.responses.append(defer_response)
                if not defer_response.should_proceed:
                    response.num_deferrals += 1
                    command.call_on_defer_callbacks(defer_response)
                    response.command_log.append(command_log_entry)
                    continue
                # now check if we should cancel
                cancel_response = command.should_cancel()
                command_log_entry.responses.append(cancel_response)
                if not cancel_response.should_proceed:
                    response.num_cancellations += 1
                    command.call_on_cancel_callbacks(cancel_response)
                    command.response.status = ResponseStatus.CANCELED
                    to_remove.append(command)
                    response.command_log.append(command_log_entry)
                    continue
                # finally, execute the command
                try:
                    execution_response = command.execute()
                except Exception as e:
                    execution_response = ExecutionResponse.failure(str(e))
                command_log_entry.responses.append(execution_response)
                command.call_on_execute_callbacks(execution_response)
                if execution_response.should_proceed:
                    command.response.status = ResponseStatus.COMPLETED
                    response.num_successes += 1
                else:
                    command.response.status = ResponseStatus.FAILED
                    response.num_failures += 1
                to_remove.append(command)
            if command.response.status in (
                ResponseStatus.CANCELED,
                ResponseStatus.COMPLETED,
                ResponseStatus.FAILED,
            ):
                # double removes it but that's fine, better than missing a removal
                to_remove.append(command)
            response.command_log.append(command_log_entry)
        # remove all processed commands
        for command in to_remove:
            if command in self._queue:
                self._queue.remove(command)
        return response

    def process_all(self, max_total_iterations: int = 1000) -> QueueProcessResponse:
        """
        Process all commands in the queue until either all commands are processed, or the maximum number of iterations is reached.

        Args:
            max_total_iterations (int, optional): Maximum number of times `process_once()` can be run. Defaults to 1000.

        Returns:
            QueueProcessResponse: Response containing details of the processing.
        """
        response = QueueProcessResponse(command_log=[])
        while len(self._queue) > 0:
            if response.num_commands_processed >= max_total_iterations:
                response.reached_max_iterations = True
                break
            response += self.process_once(max_iterations=max_total_iterations)
        return response

    # Magic methods

    def __len__(self) -> int:
        """
        Get the number of commands in the queue.

        Returns:
            int: The number of commands in the queue.
        """
        return len(self._queue)

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(queue_size={len(self._queue)})"
