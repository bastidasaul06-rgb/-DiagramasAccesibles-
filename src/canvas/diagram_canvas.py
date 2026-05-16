from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import math
import wx

if TYPE_CHECKING:
    pass

from src.canvas.diagram_model import DiagramModel, NodeModel, EdgeModel
from src.canvas.diagram_controller import DiagramController


NODE_COLORS = {
    "start": "#2E86AB",
    "process": "#F5A623",
    "decision": "#7ED321",
    "input_output": "#D0021B",
    "end": "#2E86AB",
}


def _boundary_intersection(node: NodeModel, target_x: float, target_y: float) -> tuple[float, float]:
    cx = node.center_x()
    cy = node.center_y()
    dx = target_x - cx
    dy = target_y - cy

    if dx == 0 and dy == 0:
        return (cx, cy)

    hw = node.width / 2
    hh = node.height / 2

    tx = hw / abs(dx) if dx != 0 else float("inf")
    ty = hh / abs(dy) if dy != 0 else float("inf")

    t = min(tx, ty)
    return (cx + dx * t, cy + dy * t)


class DiagramCanvas(wx.Window):
    def __init__(self, parent, skip_test_nodes=False):
        super().__init__(parent, style=wx.WANTS_CHARS)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.model = DiagramModel()
        self.controller = DiagramController(self.model, self)

        self._buffer: Optional[wx.Bitmap] = None
        self._bg_color = wx.Colour(245, 245, 245)
        self._grid_color = wx.Colour(220, 220, 220)
        self._grid_size = 20
        self._show_grid = True
        self._zoom: float = 1.0
        self._scroll_x: float = 0.0
        self._scroll_y: float = 0.0
        self._has_focus: bool = False

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self.controller.on_mouse_down)
        self.Bind(wx.EVT_MOTION, self.controller.on_mouse_move)
        self.Bind(wx.EVT_LEFT_UP, self.controller.on_mouse_up)
        self.Bind(wx.EVT_KEY_DOWN, self.controller.on_key_down)
        self.Bind(wx.EVT_SET_FOCUS, self._on_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self._on_kill_focus)

        if not skip_test_nodes:
            self._add_test_nodes()

    def _on_size(self, event):
        w, h = self.GetClientSize()
        if w > 0 and h > 0:
            self._buffer = wx.Bitmap(w, h)
            self._render()
        event.Skip()

    def _on_paint(self, event):
        if self._buffer:
            dc = wx.BufferedPaintDC(self, self._buffer)
        else:
            event.Skip()

    def _on_focus(self, event):
        self._has_focus = True
        self.refresh()

    def _on_kill_focus(self, event):
        self._has_focus = False
        self.refresh()

    def refresh(self):
        self._render()
        self.Refresh()

    def clear_all(self):
        self.model.nodes.clear()
        self.model.edges.clear()
        self.controller.focus_manager.clear()
        self.controller.undo_manager.clear()
        self._render()
        self.Refresh()

    def _render(self):
        if not self._buffer:
            return
        w, h = self.GetClientSize()
        if w <= 0 or h <= 0:
            return

        dc = wx.MemoryDC()
        dc.SelectObject(self._buffer)

        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            dc.SelectObject(wx.NullBitmap)
            return

        self._draw_all(gc, w, h)

        dc.SelectObject(wx.NullBitmap)

    def _draw_all(self, gc: wx.GraphicsContext, w: int, h: int):
        gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)
        gc.SetBrush(wx.Brush(self._bg_color))
        gc.DrawRectangle(0, 0, w, h)
        self._draw_grid(gc, w, h)
        self._draw_edges(gc)
        self._draw_nodes(gc)
        if self._has_focus:
            self._draw_focus_indicator(gc, w, h)

    def _calc_bounds(self) -> tuple[float, float, float, float]:
        if not self.model.nodes:
            return (0, 0, 400, 300)
        min_x = min(n.x for n in self.model.nodes)
        min_y = min(n.y for n in self.model.nodes)
        max_x = max(n.x + n.width for n in self.model.nodes)
        max_y = max(n.y + n.height for n in self.model.nodes)
        return (min_x - 20, min_y - 20, max_x + 20, max_y + 20)

    def export_png(self, filepath: str):
        min_x, min_y, max_x, max_y = self._calc_bounds()
        w = int(max_x - min_x)
        h = int(max_y - min_y)
        old_zoom = self._zoom
        old_scroll_x = self._scroll_x
        old_scroll_y = self._scroll_y
        self._zoom = 2.0
        self._scroll_x = -min_x * self._zoom
        self._scroll_y = -min_y * self._zoom

        bmp = wx.Bitmap(w * 2, h * 2)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            had_focus = self._has_focus
            self._has_focus = False
            gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)
            gc.SetBrush(wx.Brush(self._bg_color))
            gc.DrawRectangle(0, 0, w * 2, h * 2)
            self._draw_edges(gc)
            self._draw_nodes(gc)
            self._has_focus = had_focus
        dc.SelectObject(wx.NullBitmap)
        bmp.SaveFile(filepath, wx.BITMAP_TYPE_PNG)

        self._zoom = old_zoom
        self._scroll_x = old_scroll_x
        self._scroll_y = old_scroll_y

    def export_svg(self, filepath: str):
        min_x, min_y, max_x, max_y = self._calc_bounds()
        w = max_x - min_x
        h = max_y - min_y
        lines = []
        lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(w)}" height="{int(h)}" viewBox="{min_x} {min_y} {w} {h}">')
        lines.append(f'<rect x="{min_x}" y="{min_y}" width="{w}" height="{h}" fill="#f5f5f5" stroke="none"/>')

        for edge in self.model.edges:
            source = self.model.get_node_by_id(edge.source_id)
            target = self.model.get_node_by_id(edge.target_id)
            if source and target:
                sx, sy = _boundary_intersection(source, target.center_x(), target.center_y())
                tx, ty = _boundary_intersection(target, source.center_x(), source.center_y())
                lines.append(f'<line x1="{sx}" y1="{sy}" x2="{tx}" y2="{ty}" stroke="#555" stroke-width="2"/>')
                ax = tx - sx
                ay = ty - sy
                import math
                angle = math.atan2(ay, ax)
                size = 10
                lines.append(f'<polygon points="{tx},{ty} {tx - size * math.cos(angle - 0.4)},{ty - size * math.sin(angle - 0.4)} {tx - size * math.cos(angle + 0.4)},{ty - size * math.sin(angle + 0.4)}" fill="#555"/>')

        for node in self.model.nodes:
            color = node.color
            if node.type in ("start", "end"):
                rx = node.height / 4
                lines.append(f'<rect x="{node.x}" y="{node.y}" width="{node.width}" height="{node.height}" rx="{rx}" fill="{color}" stroke="#333" stroke-width="2"/>')
            elif node.type == "decision":
                cx = node.x + node.width / 2
                cy = node.y + node.height / 2
                hw = node.width / 2
                hh = node.height / 2
                lines.append(f'<polygon points="{cx},{node.y} {node.x + node.width},{cy} {cx},{node.y + node.height} {node.x},{cy}" fill="{color}" stroke="#333" stroke-width="2"/>')
            elif node.type == "input_output":
                offset = 15
                lines.append(f'<polygon points="{node.x + offset},{node.y} {node.x + node.width},{node.y} {node.x + node.width - offset},{node.y + node.height} {node.x},{node.y + node.height}" fill="{color}" stroke="#333" stroke-width="2"/>')
            else:
                lines.append(f'<rect x="{node.x}" y="{node.y}" width="{node.width}" height="{node.height}" fill="{color}" stroke="#333" stroke-width="2"/>')

            cx = node.x + node.width / 2
            cy = node.y + node.height / 2
            lines.append(f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" fill="white" font-family="Arial" font-size="11">{self._xml_escape(node.label)}</text>')

        lines.append('</svg>')

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    @staticmethod
    def _xml_escape(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def _draw_grid(self, gc: wx.GraphicsContext, w: int, h: int):
        if not self._show_grid:
            return
        gc.SetPen(wx.Pen(self._grid_color, 1))
        gs = self._grid_size
        x_start = self._scroll_x % gs
        y_start = self._scroll_y % gs
        x = x_start
        while x < w:
            gc.StrokeLine(x, 0, x, h)
            x += gs
        y = y_start
        while y < h:
            gc.StrokeLine(0, y, w, y)
            y += gs

    def _draw_nodes(self, gc: wx.GraphicsContext):
        for node in self.model.nodes:
            self._draw_node(gc, node)

    def _draw_node(self, gc: wx.GraphicsContext, node: NodeModel):
        x, y = self.get_render_coords(node.x, node.y)
        w = node.width * self._zoom
        hh = node.height * self._zoom

        if node.selected:
            gc.SetPen(wx.Pen("#FFD700", 3))
            gc.SetBrush(wx.Brush(wx.Colour(node.color)))
        elif node.focused:
            gc.SetPen(wx.Pen("#00AAFF", 3))
            gc.SetBrush(wx.Brush(wx.Colour(node.color)))
        else:
            gc.SetPen(wx.Pen("#333333", 2))
            gc.SetBrush(wx.Brush(wx.Colour(node.color)))

        if node.type in ("start", "end"):
            radius = hh / 2
            gc.DrawRoundedRectangle(x, y, w, hh, radius)
        elif node.type == "decision":
            path = gc.CreatePath()
            path.MoveToPoint(x + w / 2, y)
            path.AddLineToPoint(x + w, y + hh / 2)
            path.AddLineToPoint(x + w / 2, y + hh)
            path.AddLineToPoint(x, y + hh / 2)
            path.CloseSubpath()
            gc.DrawPath(path)
        elif node.type == "input_output":
            offset = 15 * self._zoom
            path = gc.CreatePath()
            path.MoveToPoint(x + offset, y)
            path.AddLineToPoint(x + w, y)
            path.AddLineToPoint(x + w - offset, y + hh)
            path.AddLineToPoint(x, y + hh)
            path.CloseSubpath()
            gc.DrawPath(path)
        else:
            gc.DrawRectangle(x, y, w, hh)

        font = wx.Font(
            max(9, int(10 * self._zoom)),
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
        )
        gc.SetFont(font, wx.Colour(255, 255, 255))

        tw, th = gc.GetTextExtent(node.label)
        tx = x + (w - tw) / 2
        ty = y + (hh - th) / 2
        gc.DrawText(node.label, tx, ty)

    def _draw_edges(self, gc: wx.GraphicsContext):
        gc.SetPen(wx.Pen("#555555", 2))
        for edge in self.model.edges:
            source = self.model.get_node_by_id(edge.source_id)
            target = self.model.get_node_by_id(edge.target_id)
            if not source or not target:
                continue

            sx, sy = _boundary_intersection(source, target.center_x(), target.center_y())
            tx, ty = _boundary_intersection(target, source.center_x(), source.center_y())

            rsx, rsy = self.get_render_coords(sx, sy)
            rtx, rty = self.get_render_coords(tx, ty)

            path = gc.CreatePath()
            path.MoveToPoint(rsx, rsy)

            dx = abs(rtx - rsx) * 0.4
            if dx < 30:
                dx = 30
            path.AddCurveToPoint(rsx + dx, rsy, rtx - dx, rty, rtx, rty)
            gc.StrokePath(path)

            self._draw_arrowhead(gc, rtx, rty, rsx, rsy)

    def _draw_arrowhead(self, gc: wx.GraphicsContext, x: float, y: float, from_x: float, from_y: float):
        angle = math.atan2(y - from_y, x - from_x)
        size = 10 * self._zoom
        path = gc.CreatePath()
        path.MoveToPoint(x, y)
        path.AddLineToPoint(
            x - size * math.cos(angle - 0.4),
            y - size * math.sin(angle - 0.4),
        )
        path.AddLineToPoint(
            x - size * math.cos(angle + 0.4),
            y - size * math.sin(angle + 0.4),
        )
        path.CloseSubpath()
        gc.SetBrush(wx.Brush("#555555"))
        gc.FillPath(path)

    def _draw_focus_indicator(self, gc: wx.GraphicsContext, w: int, h: int):
        gc.SetPen(wx.Pen("#00AAFF", 1))
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        gc.DrawRectangle(2, 2, w - 4, h - 4)

    def get_render_coords(self, model_x: float, model_y: float) -> tuple[float, float]:
        return (
            model_x * self._zoom + self._scroll_x,
            model_y * self._zoom + self._scroll_y,
        )

    def get_model_coords(self, screen_x: float, screen_y: float) -> tuple[float, float]:
        return (
            (screen_x - self._scroll_x) / self._zoom,
            (screen_y - self._scroll_y) / self._zoom,
        )

    def zoom_in(self):
        self._zoom = min(5.0, self._zoom * 1.2)
        self._scroll_x *= 1.2
        self._scroll_y *= 1.2
        self.refresh()

    def zoom_out(self):
        self._zoom = max(0.2, self._zoom / 1.2)
        self._scroll_x /= 1.2
        self._scroll_y /= 1.2
        self.refresh()

    def zoom_reset(self):
        self._zoom = 1.0
        self._scroll_x = 0.0
        self._scroll_y = 0.0
        self.refresh()

    def zoom_fit(self):
        if not self.model.nodes:
            self.zoom_reset()
            return
        min_x = min(n.x for n in self.model.nodes)
        min_y = min(n.y for n in self.model.nodes)
        max_x = max(n.x + n.width for n in self.model.nodes)
        max_y = max(n.y + n.height for n in self.model.nodes)
        w, h = self.GetClientSize()
        padding = 40
        range_x = max_x - min_x
        range_y = max_y - min_y
        if range_x <= 0 or range_y <= 0:
            self.zoom_reset()
            return
        self._zoom = min((w - 2 * padding) / range_x, (h - 2 * padding) / range_y, 5.0)
        self._scroll_x = padding - min_x * self._zoom
        self._scroll_y = padding - min_y * self._zoom
        self.refresh()

    def toggle_grid(self):
        self._show_grid = not self._show_grid
        self.refresh()

    def set_show_grid(self, show: bool):
        self._show_grid = show
        self.refresh()

    def focus_widget(self):
        self.SetFocus()

    def _add_test_nodes(self):
        n1 = NodeModel("start", "Inicio", 50, 50)
        n2 = NodeModel("process", "Validar datos", 50, 150)
        n3 = NodeModel("decision", "Es valido?", 50, 270)
        n4 = NodeModel("input_output", "Mostrar error", 280, 270)
        n5 = NodeModel("end", "Fin", 50, 400)

        self.model.add_node(n1)
        self.model.add_node(n2)
        self.model.add_node(n3)
        self.model.add_node(n4)
        self.model.add_node(n5)

        self.model.add_edge(EdgeModel(n1.id, n2.id))
        self.model.add_edge(EdgeModel(n2.id, n3.id))
        self.model.add_edge(EdgeModel(n3.id, n4.id, "No"))
        self.model.add_edge(EdgeModel(n3.id, n5.id, "Si"))
