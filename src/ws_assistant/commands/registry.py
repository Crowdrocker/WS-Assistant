from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Action:
    name: str
    description: str
    handler: Callable[[], str]
    sensitive: bool = False


class ActionRegistry:
    """Explicit allow-list of actions; never executes arbitrary shell text."""

    def __init__(self) -> None:
        self._actions: dict[str, Action] = {}

    def register(self, action: Action) -> None:
        if action.name in self._actions:
            raise ValueError(f"Action already registered: {action.name}")
        self._actions[action.name] = action

    def get(self, name: str) -> Action | None:
        return self._actions.get(name)

    def list_actions(self) -> list[Action]:
        return sorted(self._actions.values(), key=lambda item: item.name)
