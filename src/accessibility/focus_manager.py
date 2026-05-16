from __future__ import annotations
from typing import Optional
from src.canvas.diagram_model import DiagramModel, NodeModel


class FocusManager:
    def __init__(self, model: DiagramModel):
        self.model = model
        self.focused_index: int = -1

    @property
    def focused_node(self) -> Optional[NodeModel]:
        if 0 <= self.focused_index < len(self.model.nodes):
            return self.model.nodes[self.focused_index]
        return None

    def focus_next(self) -> int:
        if not self.model.nodes:
            self.focused_index = -1
            return -1
        if self.focused_index >= len(self.model.nodes) - 1:
            self.focused_index = 0
        else:
            self.focused_index += 1
        self._sync()
        return self.focused_index

    def focus_next_can_exit(self) -> tuple[int, bool]:
        if not self.model.nodes:
            self.focused_index = -1
            return (-1, True)
        if self.focused_index >= len(self.model.nodes) - 1:
            self.focused_index = -1
            self.model.clear_focus()
            return (-1, True)
        self.focused_index += 1
        self._sync()
        return (self.focused_index, False)

    def focus_previous(self) -> int:
        if not self.model.nodes:
            self.focused_index = -1
            return -1
        if self.focused_index <= 0:
            self.focused_index = len(self.model.nodes) - 1
        else:
            self.focused_index -= 1
        self._sync()
        return self.focused_index

    def focus_previous_can_exit(self) -> tuple[int, bool]:
        if not self.model.nodes:
            self.focused_index = -1
            return (-1, True)
        if self.focused_index <= 0:
            self.focused_index = -1
            self.model.clear_focus()
            return (-1, True)
        self.focused_index -= 1
        self._sync()
        return (self.focused_index, False)

    def focus_index(self, index: int) -> bool:
        if 0 <= index < len(self.model.nodes):
            self.focused_index = index
            self._sync()
            return True
        return False

    def focus_node(self, node: NodeModel) -> bool:
        for i, n in enumerate(self.model.nodes):
            if n is node:
                return self.focus_index(i)
        return False

    def clear(self):
        self.focused_index = -1
        self.model.clear_focus()

    def _sync(self):
        self.model.clear_focus()
        if self.focused_node:
            self.focused_node.focused = True
