import wx
from src.templates.data import TEMPLATES


class TemplateDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Plantillas", size=(500, 400))
        self._selected = None

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        instr = wx.StaticText(panel, label="Seleccione una plantilla para comenzar:")
        instr_font = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        instr.SetFont(instr_font)
        vbox.Add(instr, 0, wx.ALL, 10)

        self._list = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER,
        )
        self._list.AppendColumn("Nombre", width=200)
        self._list.AppendColumn("Descripcion", width=260)

        for i, tpl in enumerate(TEMPLATES):
            idx = self._list.InsertItem(i, tpl["name"])
            self._list.SetItem(idx, 1, tpl["description"])
            self._list.SetItemData(idx, i)

        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_activate)
        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_select)
        vbox.Add(self._list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self._desc = wx.StaticText(panel, label="")
        self._desc.SetFont(wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        vbox.Add(self._desc, 0, wx.ALL, 10)

        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(panel, wx.ID_OK)
        btn_ok.SetLabel("&Usar plantilla")
        btn_ok.SetDefault()
        btn_ok.Disable()
        self._btn_ok = btn_ok
        btn_cancel = wx.Button(panel, wx.ID_CANCEL)
        btn_cancel.SetLabel("&Cancelar")
        btn_sizer.AddButton(btn_ok)
        btn_sizer.AddButton(btn_cancel)
        btn_sizer.Realize()
        vbox.Add(btn_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)

        self.SetSize((500, 420))
        panel.SetSizer(vbox)

        self._list.SetFocus()

    def _on_select(self, event):
        idx = event.GetIndex()
        data = self._list.GetItemData(idx)
        self._selected = data
        self._btn_ok.Enable()
        self._desc.SetLabel(TEMPLATES[data]["description"])

    def _on_activate(self, event):
        self._on_select(event)
        self.EndModal(wx.ID_OK)

    def GetSelectedTemplate(self):
        if self._selected is not None:
            return TEMPLATES[self._selected]
        return None
