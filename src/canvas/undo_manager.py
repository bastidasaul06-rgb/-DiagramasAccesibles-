from __future__ import annotations
from typing import Optional
from src.canvas.diagram_model import DiagramModel, NodeModel, EdgeModel

MAX_UNDO = 50


class UndoManager:
    def __init__(self, model: DiagramModel):
        self._model = model
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []

    def snapshot(self):
        data = self._model.to_dict()
        self._undo_stack.append(data)
        if len(self._undo_stack) > MAX_UNDO:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        current = self._model.to_dict()
        self._redo_stack.append(current)
        data = self._undo_stack.pop()
        self._load(data)
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        current = self._model.to_dict()
        self._undo_stack.append(current)
        data = self._redo_stack.pop()
        self._load(data)
        return True

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()

    def _load(self, data: dict):
        self._model.nodes.clear()
        self._model.edges.clear()
        for ndata in data.get("nodes", []):
            node = NodeModel(ndata["type"], ndata["label"], ndata["x"], ndata["y"], ndata.get("description", ""))
            self._model.add_node(node)
        for edata in data.get("edges", []):
            edge = EdgeModel(edata["source_id"], edata["target_id"], edata.get("label", ""))
            self._model.add_edge(edge)
