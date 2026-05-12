"""Content-addressed DAG for pipeline task orchestration."""

from __future__ import annotations

import dataclasses
import hashlib
import pathlib
from collections.abc import Callable
from typing import Any


@dataclasses.dataclass
class Task:
    """A single pipeline task with content-addressed caching.

    Attributes:
        name: Unique task name.
        fn: Callable that performs the task.
        inputs: List of input task names that must complete before this task.
        output_path: Optional path where this task writes its output artefact.

    Examples:
        >>> def dummy() -> str:
        ...     return "ok"
        >>> t = Task(name="dummy", fn=dummy, inputs=[], output_path=None)
        >>> t.name
        'dummy'
    """

    name: str
    fn: Callable[..., Any]
    inputs: list[str]
    output_path: pathlib.Path | None = None

    def cache_key(self, input_hashes: dict[str, str]) -> str:
        """Compute a content-addressed cache key for this task.

        Args:
            input_hashes: Mapping from input task name to its output hash.

        Returns:
            Hex digest of the SHA-256 of the task name and input hashes.

        Examples:
            >>> def f() -> None: ...
            >>> t = Task("t", f, [])
            >>> key = t.cache_key({})
            >>> len(key) == 64
            True
        """
        h = hashlib.sha256()
        h.update(self.name.encode())
        for inp in sorted(self.inputs):
            h.update(inp.encode())
            h.update(input_hashes.get(inp, "").encode())
        return h.hexdigest()


class DAG:
    """Content-addressed directed acyclic graph for pipeline execution.

    Examples:
        >>> dag = DAG()
        >>> dag is not None
        True
    """

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._results: dict[str, Any] = {}
        self._hashes: dict[str, str] = {}

    def add_task(self, task: Task) -> None:
        """Register a task in the DAG.

        Args:
            task: Task instance to register.
        """
        if task.name in self._tasks:
            raise ValueError(f"Duplicate task name: {task.name}")
        self._tasks[task.name] = task

    def run(self, **kwargs: Any) -> dict[str, Any]:
        """Execute all tasks in topological order.

        Args:
            **kwargs: Keyword arguments passed to every task function.

        Returns:
            Dict mapping task name to its return value.
        """
        order = self._topological_sort()
        for name in order:
            task = self._tasks[name]
            input_results = {inp: self._results.get(inp) for inp in task.inputs}
            result = task.fn(**input_results, **kwargs)
            self._results[name] = result
            result_hash = hashlib.sha256(str(result).encode()).hexdigest()
            self._hashes[name] = result_hash

        return dict(self._results)

    def _topological_sort(self) -> list[str]:
        """Return task names in topological order.

        Returns:
            List of task names.

        Raises:
            ValueError: If the graph contains a cycle.
        """
        visited: set[str] = set()
        order: list[str] = []

        def _visit(name: str, stack: set[str]) -> None:
            if name in stack:
                raise ValueError(f"Cycle detected involving task: {name}")
            if name in visited:
                return
            stack.add(name)
            for dep in self._tasks[name].inputs:
                if dep in self._tasks:
                    _visit(dep, stack)
            stack.discard(name)
            visited.add(name)
            order.append(name)

        for name in self._tasks:
            _visit(name, set())

        return order
