from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import wx

if TYPE_CHECKING:
    from src.canvas.diagram_canvas import DiagramCanvas

from src.canvas.diagram_model import DiagramModel, NodeModel, EdgeModel
from src.canvas.undo_manager import UndoManager
from src.accessibility.focus_manager import FocusManager


_a11y_output = None

def _speak(text: str):
    global _a11y_output
    try:
        if _a11y_output is None:
            from accessible_output2.outputs.auto import Auto
            _a11y_output = Auto()
        _a11y_output.speak(text, interrupt=True)
    except Exception:
        pass


MOVE_STEP = 8
MOVE_STEP_FAST = 40


class DiagramController:
    def __init__(self, model: DiagramModel, canvas: DiagramCanvas):
        self.model = model
        self.canvas = canvas
        self.focus_manager = FocusManager(model)

        self.undo_manager = UndoManager(model)

        self._dragging: bool = False
        self._drag_node: Optional[NodeModel] = None
        self._drag_offset_x: float = 0.0
        self._drag_offset_y: float = 0.0
        self._connecting: bool = False
        self._connect_source: Optional[NodeModel] = None
        self._selection_callback = None
        self._connect_mode_callback = None

    def set_connect_mode_callback(self, callback):
        self._connect_mode_callback = callback

    def is_connecting(self) -> bool:
        return self._connecting

    def set_connecting(self, active: bool):
        self._connecting = active
        if not active:
            self._connect_source = None
            self.canvas.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        else:
            self.canvas.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        self._update_status_bar()
        if self._connect_mode_callback:
            self._connect_mode_callback()

    def undo(self):
        if not self.undo_manager.undo():
            _speak("Nada que deshacer")
            return
        self.focus_manager.clear()
        self.canvas.refresh()
        self._notify_selection()
        self._update_status_bar()
        _speak("Cambio deshecho")

    def redo(self):
        if not self.undo_manager.redo():
            _speak("Nada que rehacer")
            return
        self.focus_manager.clear()
        self.canvas.refresh()
        self._notify_selection()
        self._update_status_bar()
        _speak("Cambio rehecho")

    def _perform_connect(self, source: NodeModel, target: NodeModel):
        self.undo_manager.snapshot()
        self.model.deselect_all()
        edge = EdgeModel(source.id, target.id)
        self.model.add_edge(edge)
        self._connecting = False
        self._connect_source = None
        self.canvas.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self._notify_selection()
        self.canvas.refresh()
        self._update_status_bar()
        text = f"Conexion creada de {source.label} a {target.label}"
        _speak(text)
        frame = self.canvas.GetParent()
        if hasattr(frame, "SetStatusText"):
            frame.SetStatusText(text)
        if self._connect_mode_callback:
            self._connect_mode_callback()

    def set_selection_callback(self, callback):
        self._selection_callback = callback

    def _notify_selection(self):
        if self._selection_callback:
            self._selection_callback()

    def on_mouse_down(self, event: wx.MouseEvent):
        self.canvas.SetFocus()
        mx, my = self.canvas.get_model_coords(event.GetX(), event.GetY())

        clicked = self._hit_node(mx, my)

        if self._connecting:
            if clicked:
                if self._connect_source is None:
                    self._connect_source = clicked
                    text = f"Origen: {clicked.label}. Seleccione el nodo destino."
                    frame = self.canvas.GetParent()
                    if hasattr(frame, "SetStatusText"):
                        frame.SetStatusText(text)
                    _speak(text)
                elif clicked is not self._connect_source:
                    self._perform_connect(self._connect_source, clicked)
                else:
                    _speak("Mismo nodo. Seleccione otro como destino.")
            else:
                self.set_connecting(False)
                _speak("Modo conexion cancelado")
            return

        if clicked:
            if not event.ControlDown():
                self.model.deselect_all()
            clicked.selected = True
            self.undo_manager.snapshot()
            self._dragging = True
            self._drag_node = clicked
            self._drag_offset_x = mx - clicked.x
            self._drag_offset_y = my - clicked.y

            self.focus_manager.focus_node(clicked)
            self._notify_focus()
        else:
            self.model.deselect_all()
            self.focus_manager.clear()
            self._notify_focus()

        self._notify_selection()
        self.canvas.refresh()
        self._update_status_bar()

    def on_mouse_move(self, event: wx.MouseEvent):
        if self._dragging and self._drag_node:
            mx, my = self.canvas.get_model_coords(event.GetX(), event.GetY())
            self._drag_node.x = mx - self._drag_offset_x
            self._drag_node.y = my - self._drag_offset_y
            self.canvas.refresh()
        else:
            mx, my = self.canvas.get_model_coords(event.GetX(), event.GetY())
            over = self._hit_node(mx, my)
            if over:
                self.canvas.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            else:
                self.canvas.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

    def on_mouse_up(self, event: wx.MouseEvent):
        if self._dragging:
            self._dragging = False
            self._drag_node = None
            self._update_status_bar()

    def on_key_down(self, event: wx.KeyEvent):
        key = event.GetKeyCode()

        if key == wx.WXK_TAB:
            if event.ShiftDown():
                idx, can_exit = self.focus_manager.focus_previous_can_exit()
            else:
                idx, can_exit = self.focus_manager.focus_next_can_exit()
            if can_exit:
                frame = self.canvas.GetParent()
                if hasattr(frame, "cycle_area"):
                    wx.CallAfter(frame.cycle_area, forward=not event.ShiftDown())
                return
            if idx >= 0:
                self._notify_focus()
            self.canvas.refresh()
            self._update_status_bar()

        elif key == wx.WXK_RETURN or key == wx.WXK_NUMPAD_ENTER:
            fn = self.focus_manager.focused_node
            if fn:
                if self._connecting:
                    if self._connect_source is None:
                        self._connect_source = fn
                        text = f"Origen: {fn.label}. Seleccione el nodo destino."
                        frame = self.canvas.GetParent()
                        if hasattr(frame, "SetStatusText"):
                            frame.SetStatusText(text)
                        _speak(text)
                    elif fn is not self._connect_source:
                        self._perform_connect(self._connect_source, fn)
                    else:
                        _speak("Mismo nodo. Seleccione otro como destino.")
                else:
                    fn.selected = not fn.selected
                    self._notify_state_change()
                    self._notify_selection()
                self.canvas.refresh()
                self._update_status_bar()

        elif key == wx.WXK_ESCAPE:
            if self._connecting:
                self.set_connecting(False)
                text = "Modo conexion cancelado"
                frame = self.canvas.GetParent()
                if hasattr(frame, "SetStatusText"):
                    frame.SetStatusText(text)
                _speak(text)
                self.canvas.refresh()
                self._update_status_bar()
                return
            self.model.deselect_all()
            self.focus_manager.clear()
            self._notify_focus()
            self._notify_selection()
            self.canvas.refresh()
            self._update_status_bar()

        elif key == wx.WXK_DELETE or key == wx.WXK_BACK:
            self.delete_selected()

        elif key == wx.WXK_UP or key == wx.WXK_DOWN or key == wx.WXK_LEFT or key == wx.WXK_RIGHT:
            fn = self.focus_manager.focused_node
            if fn:
                self.undo_manager.snapshot()
                step = MOVE_STEP_FAST if event.ShiftDown() else MOVE_STEP
                dx = step if key == wx.WXK_RIGHT else (-step if key == wx.WXK_LEFT else 0)
                dy = step if key == wx.WXK_DOWN else (-step if key == wx.WXK_UP else 0)
                fn.x += dx
                fn.y += dy
                self.canvas.refresh()
                self._notify_move(key, step, fn)
            else:
                event.Skip()

        elif key == ord('P') and event.ControlDown():
            self._announce_position()

        elif key == wx.WXK_F2:
            fn = self.focus_manager.focused_node
            if fn:
                self._begin_edit_label(fn)
            else:
                event.Skip()

        else:
            event.Skip()

    def delete_selected(self):
        self.undo_manager.snapshot()
        to_delete = [n for n in self.model.nodes if n.selected]
        for node in to_delete:
            nid = node.id
            idx = self.focus_manager.focused_index
            self.model.remove_node(nid)
            if idx >= len(self.model.nodes):
                self.focus_manager.focus_index(len(self.model.nodes) - 1)
        self._notify_selection()
        self.canvas.refresh()
        self._update_status_bar()
        if to_delete:
            try:
                wx.Accessible.NotifyEvent(
                    wx.ACC_EVENT_OBJECT_DESTROY, self.canvas, wx.OBJID_CLIENT, wx.ACC_SELF
                )
            except Exception:
                pass

    def select_all(self):
        for node in self.model.nodes:
            node.selected = True
        if self.model.nodes:
            self.focus_manager.focus_index(len(self.model.nodes) - 1)
            self._notify_focus()
        self._notify_selection()
        self.canvas.refresh()
        self._update_status_bar()

    def add_node_at(self, node_type: str, label: str, description: str, x: float, y: float) -> NodeModel:
        self.undo_manager.snapshot()
        node = NodeModel(node_type, label, x, y, description)
        self.model.add_node(node)
        self.model.deselect_all()
        node.selected = True
        self.focus_manager.focus_node(node)
        self._notify_focus()
        self._notify_selection()
        self.canvas.refresh()
        self._update_status_bar()
        return node

    def get_center_position(self) -> tuple[float, float]:
        w, h = self.canvas.GetClientSize()
        cx = (w / 2 - self.canvas._scroll_x) / self.canvas._zoom
        cy = (h / 2 - self.canvas._scroll_y) / self.canvas._zoom
        return (cx - 70, cy - 30)

    def on_zoom_in(self):
        self.canvas.zoom_in()

    def on_zoom_out(self):
        self.canvas.zoom_out()

    def on_zoom_reset(self):
        self.canvas.zoom_reset()

    def on_zoom_fit(self):
        self.canvas.zoom_fit()

    def _begin_edit_label(self, node: NodeModel):
        old_label = node.label
        dlg = wx.TextEntryDialog(
            self.canvas, "Editar etiqueta del nodo:", "Editar etiqueta", node.label
        )
        if dlg.ShowModal() == wx.ID_OK:
            new_label = dlg.GetValue().strip()
            if new_label and new_label != old_label:
                self.undo_manager.snapshot()
                node.label = new_label
                self.canvas.refresh()
                try:
                    wx.Accessible.NotifyEvent(
                        wx.ACC_EVENT_OBJECT_NAMECHANGE, self.canvas, wx.OBJID_CLIENT, wx.ACC_SELF
                    )
                except Exception:
                    pass
        dlg.Destroy()

    def _hit_node(self, mx: float, my: float) -> Optional[NodeModel]:
        for node in reversed(self.model.nodes):
            if node.hit_test(mx, my):
                return node
        return None

    def _notify_focus(self):
        fm = self.focus_manager
        child_id = fm.focused_index + 1 if fm.focused_index >= 0 else wx.ACC_SELF
        try:
            wx.Accessible.NotifyEvent(
                wx.ACC_EVENT_OBJECT_FOCUS, self.canvas, wx.OBJID_CLIENT, child_id
            )
        except Exception:
            pass

    def _notify_move(self, key: int, step: int, node: NodeModel):
        dirs = {
            wx.WXK_UP: "arriba",
            wx.WXK_DOWN: "abajo",
            wx.WXK_LEFT: "izquierda",
            wx.WXK_RIGHT: "derecha",
        }
        direction = dirs.get(key, "")
        text = f"{node.label} movido {step}px a la {direction}"
        frame = self.canvas.GetParent()
        if hasattr(frame, "SetStatusText"):
            frame.SetStatusText(text)
        _speak(text)
        try:
            wx.Accessible.NotifyEvent(
                wx.ACC_EVENT_OBJECT_LOCATIONCHANGE, self.canvas, wx.OBJID_CLIENT, wx.ACC_SELF
            )
        except Exception:
            pass

    def _announce_position(self):
        fn = self.focus_manager.focused_node
        if fn:
            text = f"Posicion de {fn.label}: X={int(fn.x)}, Y={int(fn.y)}"
        else:
            text = "No hay nodo enfocado"
        frame = self.canvas.GetParent()
        if hasattr(frame, "SetStatusText"):
            frame.SetStatusText(text)
        _speak(text)

    def _notify_state_change(self):
        fm = self.focus_manager
        child_id = fm.focused_index + 1 if fm.focused_index >= 0 else wx.ACC_SELF
        try:
            wx.Accessible.NotifyEvent(
                wx.ACC_EVENT_OBJECT_STATECHANGE, self.canvas, wx.OBJID_CLIENT, child_id
            )
        except Exception:
            pass

    def _update_status_bar(self):
        frame = self.canvas.GetParent()
        if hasattr(frame, "SetStatusText"):
            if self._connecting:
                src = self._connect_source
                if src:
                    text = f"MODO CONEXION - Origen: {src.label}. Seleccione destino con Enter o clic"
                else:
                    text = "MODO CONEXION - Seleccione el nodo origen con Enter o clic"
                frame.SetStatusText(text)
                return
            selected = sum(1 for n in self.model.nodes if n.selected)
            total = len(self.model.nodes)
            fm = self.focus_manager
            focus_info = fm.focused_index + 1 if fm.focused_index >= 0 else 0
            text = f"{total} nodos | {len(self.model.edges)} conexiones | Seleccionados: {selected}"
            if focus_info:
                text += f" | Foco: {focus_info}/{total}"
            frame.SetStatusText(text)
