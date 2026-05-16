import wx
from src.canvas.diagram_model import NODE_TYPES

NODE_TYPE_NAMES = {
    "start": "Inicio",
    "process": "Proceso",
    "decision": "Decisión",
    "input_output": "Entrada/Salida",
    "end": "Fin",
}


class NodeCreateDialog(wx.Dialog):
    def __init__(self, parent, preselected_type=None):
        wx.Dialog.__init__(self, parent, title="Crear nodo", size=(400, 320))

        self._node_type = preselected_type or "process"

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(panel, label="&Tipo de nodo:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        type_order = ["start", "process", "decision", "input_output", "end"]
        type_labels = [NODE_TYPE_NAMES[t] for t in type_order]
        self._type_choice = wx.Choice(panel, choices=type_labels)
        if preselected_type in type_order:
            self._type_choice.SetSelection(type_order.index(preselected_type))
        else:
            self._type_choice.SetSelection(0)
        hbox1.Add(self._type_choice, 1, wx.EXPAND)
        vbox.Add(hbox1, 0, wx.EXPAND | wx.ALL, 5)

        vbox.Add(self._field(panel, "&Etiqueta:", "label"), 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self._field(panel, "&Descripcion:", "description"), 0, wx.EXPAND | wx.ALL, 5)

        vbox.AddStretchSpacer()

        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(panel, wx.ID_OK)
        btn_ok.SetLabel("&Crear")
        btn_ok.SetDefault()
        btn_cancel = wx.Button(panel, wx.ID_CANCEL)
        btn_cancel.SetLabel("&Cancelar")
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()
        vbox.Add(btn_sizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

        panel.SetSizer(vbox)

        self.Bind(wx.EVT_BUTTON, self._on_ok, btn_ok)

    def _field(self, parent, label, attr):
        box = wx.BoxSizer(wx.VERTICAL)
        st = wx.StaticText(parent, label=label)
        tc = wx.TextCtrl(parent)
        setattr(self, f"_{attr}", tc)
        box.Add(st, 0, wx.BOTTOM, 2)
        box.Add(tc, 0, wx.EXPAND)
        return box

    def _on_ok(self, event):
        self.EndModal(wx.ID_OK)

    def get_node_info(self):
        type_order = ["start", "process", "decision", "input_output", "end"]
        idx = self._type_choice.GetSelection()
        node_type = type_order[idx] if 0 <= idx < len(type_order) else "process"
        label = self._label.GetValue().strip()
        if not label:
            info = NODE_TYPES.get(node_type, NODE_TYPES["process"])
            label = info["label"]
        description = self._description.GetValue().strip()
        return (node_type, label, description)
