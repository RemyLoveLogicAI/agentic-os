"""Deterministic tool registry — maps tool names to handlers."""

from __future__ import annotations

from typing import Any, Callable, Awaitable

ToolHandler = Callable[[dict[str, Any]], Awaitable[Any]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolHandler] = {}

    def register(self, name: str, handler: ToolHandler) -> None:
        self._tools[name] = handler

    def get(self, name: str) -> ToolHandler | None:
        return self._tools.get(name)

    def available(self) -> list[str]:
        return list(self._tools.keys())

    async def invoke(self, name: str, args: dict[str, Any]) -> Any:
        handler = self._tools.get(name)
        if handler is None:
            raise KeyError(f"Tool '{name}' not registered")
        return await handler(args)


# --- Built-in tools ----------------------------------------------------------

async def _echo(args: dict[str, Any]) -> Any:
    return {"echo": args.get("message", "")}


async def _status(args: dict[str, Any]) -> Any:
    return {"status": "ok", "service": "agentic-ide"}


registry = ToolRegistry()
registry.register("echo", _echo)
registry.register("status", _status)
