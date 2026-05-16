import wx
from src.canvas.diagram_model import NODE_TYPES


NODE_TYPE_NAMES = {
    "start": "Inicio",
    "process": "Proceso",
    "decision": "Decisión",
    "input_output": "Entrada/Salida",
    "end": "Fin",
}


class ToolPalette(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(180, -1))
        self._parent_frame = parent

        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, label="Paleta de nodos")
        title_font = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        vbox.Add(title, 0, wx.ALL, 8)

        self._list = wx.ListCtrl(
            self,
            style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL,
            size=(164, -1),
        )
        self._list.AppendColumn("Tipo", width=140)
        self._list.AppendColumn("Desc", width=0)

        type_order = ["start", "process", "decision", "input_output", "end"]
        for i, t in enumerate(type_order):
            info = NODE_TYPES.get(t, {})
            label = NODE_TYPE_NAMES.get(t, t)
            desc = info.get("label", "")
            idx = self._list.InsertItem(i, label)
            self._list.SetItem(idx, 1, desc)
            self._list.SetItemData(idx, i)

        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_add)
        vbox.Add(self._list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        self._btn_add = wx.Button(self, label="&Añadir nodo")
        self._btn_add.SetToolTip("Ctrl+Shift+N: Añadir un nuevo nodo al diagrama")
        self._btn_add.Bind(wx.EVT_BUTTON, self._on_add)
        vbox.Add(self._btn_add, 0, wx.EXPAND | wx.ALL, 8)

        self.SetSizer(vbox)

    def focus_widget(self):
        if self._list.GetItemCount() > 0:
            self._list.SetFocus()
        else:
            self._list.SetFocus()

    def _on_add(self, event):
        sel = self._list.GetFirstSelected()
        if sel < 0:
            wx.MessageBox("Seleccione un tipo de nodo de la lista.", "Añadir nodo", wx.OK | wx.ICON_INFORMATION)
            return
        data = self._list.GetItemData(sel)
        type_order = ["start", "process", "decision", "input_output", "end"]
        if 0 <= data < len(type_order):
            node_type = type_order[data]
            self._parent_frame._open_create_node_dialog(node_type)
