import wx
from src.canvas.diagram_model import NODE_TYPES

NODE_TYPE_NAMES = {
    "start": "Inicio",
    "process": "Proceso",
    "decision": "Decisión",
    "input_output": "Entrada/Salida",
    "end": "Fin",
}


class ConnectDialog(wx.Dialog):
    def __init__(self, parent, source_node, all_nodes):
        wx.Dialog.__init__(self, parent, title="Conectar nodos", size=(450, 350))
        self._selected_node = None

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        src_type = NODE_TYPE_NAMES.get(source_node.type, source_node.type)
        info = wx.StaticText(panel, label=f"Origen: {src_type} - {source_node.label}")
        info_font = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        info.SetFont(info_font)
        vbox.Add(info, 0, wx.ALL, 10)

        instr = wx.StaticText(panel, label="Seleccione el nodo destino:")
        vbox.Add(instr, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self._list = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER,
        )
        self._list.AppendColumn("Nodo", width=200)
        self._list.AppendColumn("Tipo", width=180)

        for i, node in enumerate(all_nodes):
            if node.id == source_node.id:
                continue
            type_name = NODE_TYPE_NAMES.get(node.type, node.type)
            idx = self._list.InsertItem(i, f"{type_name}: {node.label}")
            self._list.SetItem(idx, 1, f"X={int(node.x)}, Y={int(node.y)}")
            self._list.SetItemData(idx, node.id)

        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_activate)
        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_select)
        vbox.Add(self._list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        vbox.AddSpacer(10)

        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(panel, wx.ID_OK)
        btn_ok.SetLabel("&Conectar")
        btn_ok.SetDefault()
        btn_ok.Disable()
        self._btn_ok = btn_ok
        btn_cancel = wx.Button(panel, wx.ID_CANCEL)
        btn_cancel.SetLabel("&Cancelar")
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()
        vbox.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(vbox)
        self._list.SetFocus()

    def _on_select(self, event):
        self._selected_node = event.GetItem().GetData()
        self._btn_ok.Enable()

    def _on_activate(self, event):
        self._on_select(event)
        self.EndModal(wx.ID_OK)

    def get_target_id(self):
        return self._selected_node
