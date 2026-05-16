from __future__ import annotations
from typing import TYPE_CHECKING
import math
import wx

if TYPE_CHECKING:
    from src.canvas.diagram_canvas import DiagramCanvas

from src.canvas.diagram_model import DiagramModel, NodeModel


class CanvasAccessible(wx.Accessible):
    def __init__(self, canvas: DiagramCanvas):
        super().__init__(canvas)
        self._canvas: DiagramCanvas = canvas

    @property
    def _model(self) -> DiagramModel:
        return self._canvas.model

    def GetChildCount(self):
        return len(self._model.nodes)

    def GetChild(self, childId):
        if 1 <= childId <= len(self._model.nodes):
            return (wx.ACC_OK, None)
        return (wx.ACC_NOT_IMPLEMENTED, None)

    def GetName(self, childId):
        if childId == wx.ACC_SELF:
            count = len(self._model.nodes)
            edge_count = len(self._model.edges)
            return (wx.ACC_OK, f"Lienzo de diagrama de flujo. {count} nodos, {edge_count} conexiones")
        node = self._get_node(childId)
        if node:
            conn = self._model.get_connections_for(node.id)
            name = f"{self._type_name(node.type)}: {node.label}"
            if node.selected:
                name = f"Seleccionado. {name}"
            if conn:
                name += f". {conn}"
            return (wx.ACC_OK, name)
        return (wx.ACC_NOT_IMPLEMENTED, "")

    def GetRole(self, childId):
        if childId == wx.ACC_SELF:
            return (wx.ACC_OK, wx.ROLE_SYSTEM_DIAGRAM)
        return (wx.ACC_OK, wx.ROLE_SYSTEM_GRAPHIC)

    def GetState(self, childId):
        if childId == wx.ACC_SELF:
            return (wx.ACC_OK, wx.ACC_STATE_SYSTEM_FOCUSABLE)
        node = self._get_node(childId)
        if node:
            state = wx.ACC_STATE_SYSTEM_FOCUSABLE | wx.ACC_STATE_SYSTEM_SELECTABLE
            if node.focused:
                state |= wx.ACC_STATE_SYSTEM_FOCUSED
            if node.selected:
                state |= wx.ACC_STATE_SYSTEM_SELECTED
            return (wx.ACC_OK, state)
        return (wx.ACC_NOT_IMPLEMENTED, 0)

    def GetDescription(self, childId):
        ctrl = self._canvas.controller
        pending = getattr(ctrl, '_pending_announcement', '')
        if childId == wx.ACC_SELF:
            if pending:
                return (wx.ACC_OK, pending)
            return (wx.ACC_OK, "Editor de diagramas de flujo. Use Tab para navegar entre nodos, Enter para seleccionar, F2 para editar etiqueta.")
        node = self._get_node(childId)
        if node:
            desc = node.description or f"Nodo de tipo {self._type_name(node.type)}: {node.label}"
            if pending and node.focused:
                return (wx.ACC_OK, f"{pending}. {desc}")
            return (wx.ACC_OK, desc)
        return (wx.ACC_NOT_IMPLEMENTED, "")

    def GetDefaultAction(self, childId):
        if childId != wx.ACC_SELF:
            node = self._get_node(childId)
            if node:
                return (wx.ACC_OK, "Seleccionar y editar")
        return (wx.ACC_NOT_IMPLEMENTED, "")

    def GetFocus(self):
        fm = self._canvas.controller.focus_manager
        if fm.focused_index >= 0:
            return (wx.ACC_OK, fm.focused_index + 1, None)
        return (wx.ACC_OK, wx.ACC_SELF, None)

    def Navigate(self, navDir, fromId):
        count = len(self._model.nodes)
        toId = wx.ACC_SELF

        if navDir == wx.NAVDIR_FIRSTCHILD:
            toId = 1 if count > 0 else wx.ACC_SELF
        elif navDir == wx.NAVDIR_LASTCHILD:
            toId = count if count > 0 else wx.ACC_SELF
        elif navDir == wx.NAVDIR_NEXT:
            if fromId == wx.ACC_SELF:
                toId = 1 if count > 0 else wx.ACC_SELF
            elif fromId < count:
                toId = fromId + 1
            else:
                toId = 1
        elif navDir == wx.NAVDIR_PREVIOUS:
            if fromId == wx.ACC_SELF:
                toId = count if count > 0 else wx.ACC_SELF
            elif fromId > 1:
                toId = fromId - 1
            else:
                toId = count
        elif navDir == wx.NAVDIR_UP:
            toId = wx.ACC_SELF
        elif navDir == wx.NAVDIR_DOWN:
            toId = 1 if count > 0 else wx.ACC_SELF
        else:
            return (wx.ACC_NOT_IMPLEMENTED, 0, None)

        return (wx.ACC_OK, toId, None)

    def HitTest(self, x, y):
        mx, my = self._canvas.get_model_coords(x, y)
        for i, node in enumerate(reversed(self._model.nodes)):
            if node.hit_test(mx, my):
                childId = len(self._model.nodes) - i
                return (wx.ACC_OK, childId, None)
        return (wx.ACC_OK, wx.ACC_SELF, None)

    def GetLocation(self, elementId):
        if elementId == wx.ACC_SELF:
            r = self._canvas.GetRect()
            return (wx.ACC_OK, wx.Rect(r.x, r.y, r.width, r.height))
        node = self._get_node(elementId)
        if node:
            sx, sy = self._canvas.get_render_coords(node.x, node.y)
            sw = int(node.width * self._canvas._zoom)
            sh = int(node.height * self._canvas._zoom)
            return (wx.ACC_OK, wx.Rect(int(sx), int(sy), sw, sh))
        return (wx.ACC_NOT_IMPLEMENTED, wx.Rect())

    def GetSelections(self):
        for i, node in enumerate(self._model.nodes):
            if node.selected:
                return (wx.ACC_OK, i + 1)
        return (wx.ACC_NOT_IMPLEMENTED, 0)

    def _get_node(self, childId: int) -> NodeModel | None:
        idx = childId - 1
        if 0 <= idx < len(self._model.nodes):
            return self._model.nodes[idx]
        return None

    def _type_name(self, t: str) -> str:
        names = {
            "start": "Inicio",
            "process": "Proceso",
            "decision": "Decisión",
            "input_output": "Entrada/Salida",
            "end": "Fin",
        }
        return names.get(t, t)
