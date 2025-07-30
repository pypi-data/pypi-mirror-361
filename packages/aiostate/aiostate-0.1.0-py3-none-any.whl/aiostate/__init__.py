# Copyright (c) 2025 BoChen SHEN
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================
from __future__ import annotations

import asyncio as aio
import functools as ft
import logging
import typing as t
from collections import defaultdict

_T = t.TypeVar('_T', bound=t.Hashable)

_logger = logging.getLogger(__name__)


class AsyncStateMachine(t.Generic[_T]):
    """An asynchronous state machine implementation with thread-safe operations.

    This class provides a flexible, async-friendly state machine that supports:
    - Thread-safe state transitions using asyncio locks
    - Guard conditions for conditional transitions
    - Entry and exit handlers for states
    - Decorator-based transition definitions
    - Wildcard transitions from any state

    The state machine is generic and can work with any hashable type for states
    and events.

    Example:
        ```python
        import asyncio
        from aiostate import AsyncStateMachine

        # Create a state machine for a simple traffic light
        fsm = AsyncStateMachine('red')

        @fsm.transition('red', 'timer', 'green')
        async def red_to_green():
            print("Light turns green")

        @fsm.transition('green', 'timer', 'yellow')
        async def green_to_yellow():
            print("Light turns yellow")

        @fsm.transition('yellow', 'timer', 'red')
        async def yellow_to_red():
            print("Light turns red")

        # Trigger transitions
        await fsm.trigger('timer')  # red -> green
        await fsm.trigger('timer')  # green -> yellow
        ```

    Attributes:
        state: The current state of the state machine (read-only).
        all_states: A set of all registered states (read-only).
    """

    def __init__(self, initial_state: _T):
        """Initialize the state machine with an initial state.

        Args:
            initial_state: The starting state of the state machine.
                Must be a hashable type.
        """
        self._current_state = initial_state
        self._all_states: t.Set[_T] = {initial_state}
        self._transitions: t.Dict[tuple, _T] = {}
        self._guards: t.Dict[tuple, t.Callable] = {}
        self._on_enter_handlers: t.Dict[_T, t.List[t.Callable]] = defaultdict(list)
        self._on_exit_handlers: t.Dict[_T, t.List[t.Callable]] = defaultdict(list)
        self._lock = aio.Lock()

    @property
    def state(self) -> _T:
        """Get the current state of the state machine.

        Returns:
            The current state.
        """
        return self._current_state

    @property
    def all_states(self) -> t.Set[_T]:
        """Get all registered states in the state machine.

        Returns:
            A copy of the set containing all registered states.
        """
        return self._all_states.copy()

    def is_state(self, state: _T) -> bool:
        """Check if the state machine is currently in the specified state.

        Args:
            state: The state to check against.

        Returns:
            True if the current state matches the specified state, False otherwise.
        """
        return self._current_state == state

    def can_trigger(self, evt: _T) -> bool:
        """Check if an event can be triggered from the current state.

        Args:
            evt: The event to check.

        Returns:
            True if the event can be triggered from the current state, False otherwise.
        """
        return (self._current_state, evt) in self._transitions

    def add_state(self, state: _T) -> None:
        """Add a state to the state machine without defining transitions.

        Args:
            state: The state to add to the state machine.
        """
        self._all_states.add(state)

    def transition(
        self,
        from_states: _T | t.Set[_T] | t.Literal['*'],
        evt: _T,
        to_state: _T,
        guard: t.Callable | None = None
    ):
        r"""Decorator to define a state transition with an optional action.

        This decorator registers a transition from one or more source states to a
        destination state when a specific event occurs. The decorated function
        will be executed as an action during the transition.

        Args:
            from_states: Source state(s) for the transition. Can be:
                - A single state
                - A set of states
                - '*' to apply to all current states
            evt: The event that triggers this transition.
            to_state: The destination state after the transition.
            guard: Optional guard function that must return True for the
                transition to proceed. Can be sync or async.

        Returns:
            A decorator function that wraps the transition action.

        Example:
            ```python
            @fsm.transition('idle', 'start', 'running')
            async def start_process():
                print("Process starting...")
                # Perform startup logic

            @fsm.transition({'running', 'paused'}, 'stop', 'idle')
            async def stop_process():
                print("Process stopping...")
                # Perform cleanup logic
            ```
        """

        def decorator(fn: t.Callable):
            # Add states to the registry
            self._all_states.add(to_state)

            if from_states == '*':
                # Apply to all current states
                states = self._all_states.copy()
            elif isinstance(from_states, set):
                states = from_states
                self._all_states.update(states)
            else:
                states = {from_states}
                self._all_states.add(from_states)

            # Register transitions
            for state in states:
                key = (state, evt)
                self._transitions[key] = to_state
                if guard:
                    self._guards[key] = guard

            @ft.wraps(fn)
            async def wrapper(*args, **kwargs):
                async with self._lock:
                    return await self._execute_transition(fn, evt, *args, **kwargs)

            return wrapper

        return decorator

    def on_enter(self, state: _T):
        r"""Decorator to register a handler that executes when entering a state.

        The decorated function will be called every time the state machine
        transitions into the specified state, after the transition action
        but before returning control to the caller.

        Args:
            state: The state for which to register the enter handler.

        Returns:
            A decorator function that registers the handler.

        Example:
            ```python
            @fsm.on_enter('running')
            async def log_start():
                print("Entered running state")
                # Log to database, send notifications, etc.
            ```
        """

        def decorator(func: t.Callable):
            self._all_states.add(state)
            self._on_enter_handlers[state].append(func)
            return func

        return decorator

    def on_exit(self, state: _T):
        r"""Decorator to register a handler that executes when exiting a state.

        The decorated function will be called every time the state machine
        transitions out of the specified state, before the transition action
        is executed.

        Args:
            state: The state for which to register the exit handler.

        Returns:
            A decorator function that registers the handler.

        Example:
            ```python
            @fsm.on_exit('running')
            async def cleanup():
                print("Exiting running state")
                # Cleanup resources, save state, etc.
            ```
        """

        def decorator(func: t.Callable):
            self._all_states.add(state)
            self._on_exit_handlers[state].append(func)
            return func

        return decorator

    async def trigger(self, evt: _T, **kwargs) -> bool:
        r"""Trigger an event to potentially cause a state transition.

        This method attempts to trigger the specified event from the current
        state. If a transition is defined for the current state and event,
        the transition will be executed.

        Args:
            evt: The event to trigger.
            **kwargs: Additional keyword arguments to pass to handlers and actions.

        Returns:
            True if the transition was successful, False if a guard condition
            prevented the transition.

        Raises:
            StateTransitionError: If no transition is defined for the current
                state and event, or if any handler or action fails.

        Example:
            ```python
            success = await fsm.trigger('start')
            if success:
                print("Transition successful")
            else:
                print("Transition blocked by guard condition")
            ```
        """
        async with self._lock:
            return await self._execute_transition(None, evt, **kwargs)

    async def _execute_transition(
        self,
        action: t.Callable | None,
        evt: _T,
        *args,
        **kwargs
    ) -> t.Any:
        """Execute a state transition with all associated handlers and actions.

        This internal method handles the complete transition process:
        1. Validates the transition exists
        2. Checks guard conditions
        3. Executes exit handlers
        4. Executes the transition action
        5. Updates the current state
        6. Executes enter handlers

        Args:
            action: Optional action function to execute during transition.
            evt: The event triggering the transition.
            *args: Positional arguments to pass to handlers and actions.
            **kwargs: Keyword arguments to pass to handlers and actions.

        Returns:
            The result of the action function, or None if no action.
            False if a guard condition prevented the transition.

        Raises:
            StateTransitionError: If the transition fails at any step.
        """
        key = (self._current_state, evt)

        if key not in self._transitions:
            raise StateTransitionError(
                f"No transition from {self._current_state} on event {evt}"
            )

        # Check guard condition
        if key in self._guards:
            guard = self._guards[key]
            try:
                guard_result = guard(*args, **kwargs)
                if aio.iscoroutine(guard_result):
                    guard_result = await guard_result
                if not guard_result:
                    return False
            except Exception as e:
                raise StateTransitionError(
                    f"Guard condition failed for transition from {self._current_state} on event {evt}: {e}"
                )

        old_state = self._current_state
        new_state = self._transitions[key]

        # Execute exit handlers
        if old_state in self._on_exit_handlers:
            for exit_handler in self._on_exit_handlers[old_state]:
                try:
                    if aio.iscoroutinefunction(exit_handler):
                        await exit_handler(*args, **kwargs)
                    else:
                        exit_handler(*args, **kwargs)
                except Exception as e:
                    raise StateTransitionError(
                        f"Exit handler failed for state {old_state}: {e}"
                    )

        # Execute action
        result = None
        if action:
            try:
                if aio.iscoroutinefunction(action):
                    result = await action(*args, **kwargs)
                else:
                    result = action(*args, **kwargs)
            except Exception as e:
                # Transition failed, don't change state
                raise StateTransitionError(
                    f"Action failed during transition from {old_state} to {new_state}: {e}"
                )

        # Update state only after successful action
        self._current_state = new_state

        # Execute enter handlers
        if new_state in self._on_enter_handlers:
            for enter_handler in self._on_enter_handlers[new_state]:
                try:
                    if aio.iscoroutinefunction(enter_handler):
                        await enter_handler(*args, **kwargs)
                    else:
                        enter_handler(*args, **kwargs)
                except Exception as e:
                    # State already changed, log warning but don't fail
                    _logger.warning(
                        f"Enter handler failed for state {new_state} after transition: {e}"
                    )

        return result

    def get_valid_events(self) -> t.Set[_T]:
        """Get all valid events that can be triggered from the current state.

        Returns:
            A set of events that can be triggered from the current state.
        """
        return {evt for (state, evt) in self._transitions.keys() if state == self._current_state}

    def get_transition_graph(self) -> t.Dict[_T, t.Dict[_T, _T]]:
        """Get the complete transition graph of the state machine.

        Returns:
            A dictionary mapping each state to its possible transitions.
            The format is: {from_state: {event: to_state, ...}, ...}
        """
        graph = defaultdict(dict)
        for (from_state, evt), to_state in self._transitions.items():
            graph[from_state][evt] = to_state
        return dict(graph)

    def __repr__(self) -> str:
        """Return a string representation of the state machine.

        Returns:
            A string showing the current state and all registered states.
        """
        return f"AsyncStateMachine(current_state={self._current_state}, states={self._all_states})"


class StateTransitionError(Exception):
    """Exception raised when a state transition fails.

    This exception is raised when:
    - No transition is defined for the current state and event
    - A guard condition fails
    - An exit handler fails
    - A transition action fails
    """
    pass
