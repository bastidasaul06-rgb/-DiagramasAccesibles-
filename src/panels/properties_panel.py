import wx
from src.canvas.diagram_model import NODE_TYPES

NODE_TYPE_NAMES = {
    "start": "Inicio",
    "process": "Proceso",
    "decision": "Decisión",
    "input_output": "Entrada/Salida",
    "end": "Fin",
}


class PropertiesPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(260, -1))
        self._parent_frame = parent
        self._node = None

        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, label="Propiedades")
        title_font = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        vbox.Add(title, 0, wx.ALL, 8)

        self._type_label = wx.StaticText(self, label="Tipo: --")
        vbox.Add(self._type_label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        vbox.Add(wx.StaticText(self, label="&Etiqueta:"), 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 2)
        self._label_ctrl = wx.TextCtrl(self)
        self._label_ctrl.Bind(wx.EVT_TEXT, self._on_label_changed)
        vbox.Add(self._label_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        vbox.Add(wx.StaticText(self, label="&Descripcion:"), 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 2)
        self._desc_ctrl = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 80))
        self._desc_ctrl.Bind(wx.EVT_TEXT, self._on_desc_changed)
        vbox.Add(self._desc_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self._pos_label = wx.StaticText(self, label="Posicion: --")
        vbox.Add(self._pos_label, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        vbox.AddStretchSpacer()

        line = wx.StaticLine(self)
        vbox.Add(line, 0, wx.EXPAND | wx.ALL, 8)

        info = wx.StaticText(self, label="Atajos:\nF2: Editar etiqueta\nFlechas: Mover\nSupr: Eliminar")
        info_font = wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        info.SetFont(info_font)
        vbox.Add(info, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.SetSizer(vbox)
        self.Hide()

    def show_node(self, node):
        self._node = node
        type_name = NODE_TYPE_NAMES.get(node.type, node.type)
        self._type_label.SetLabel(f"Tipo: {type_name}")
        self._label_ctrl.ChangeValue(node.label)
        self._desc_ctrl.ChangeValue(node.description)
        self._update_position()
        self.Show()
        self.GetParent().Layout()

    def hide_panel(self):
        self._node = None
        self.Hide()
        self.GetParent().Layout()

    def refresh_node(self, node=None):
        n = node or self._node
        if n and self.IsShown():
            self._label_ctrl.ChangeValue(n.label)
            self._desc_ctrl.ChangeValue(n.description)
            self._update_position()

    def _update_position(self):
        if self._node:
            self._pos_label.SetLabel(f"Posicion: X={int(self._node.x)}, Y={int(self._node.y)}")

    def _on_label_changed(self, event):
        if self._node:
            self._node.label = self._label_ctrl.GetValue()
            canvas = self._parent_frame.canvas
            canvas.refresh()
            wx.Accessible.NotifyEvent(
                wx.ACC_EVENT_OBJECT_NAMECHANGE, canvas, wx.OBJID_CLIENT, wx.ACC_SELF
            )

    def focus_widget(self):
        if self.IsShown():
            self._label_ctrl.SetFocus()

    def _on_desc_changed(self, event):
        if self._node:
            self._node.description = self._desc_ctrl.GetValue()
