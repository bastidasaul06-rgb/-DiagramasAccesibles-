import wx


class DiagramInfo:
    def __init__(self):
        self.title = ""
        self.author = ""
        self.description = ""
        self.orientation = "Vertical"
        self.theme = "Claro"
        self.show_grid = True
        self.grid_size = 20


class NewDiagramDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title="Nuevo diagrama", size=(450, 400))

        self._info = DiagramInfo()

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(self._field(panel, "&Titulo del diagrama:", "title"), 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self._field(panel, "&Autor:", "author"), 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self._field(panel, "&Descripcion:", "description"), 0, wx.EXPAND | wx.ALL, 5)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(panel, label="&Orientacion:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        self._orientation = wx.Choice(panel, choices=["Vertical", "Horizontal"])
        self._orientation.SetSelection(0)
        hbox1.Add(self._orientation, 1, wx.EXPAND)
        vbox.Add(hbox1, 0, wx.EXPAND | wx.ALL, 5)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(wx.StaticText(panel, label="&Tema de color:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        self._theme = wx.Choice(panel, choices=["Claro", "Oscuro", "Alto contraste"])
        self._theme.SetSelection(0)
        hbox2.Add(self._theme, 1, wx.EXPAND)
        vbox.Add(hbox2, 0, wx.EXPAND | wx.ALL, 5)

        self._show_grid = wx.CheckBox(panel, label="&Mostrar cuadricula")
        self._show_grid.SetValue(True)
        vbox.Add(self._show_grid, 0, wx.ALL, 5)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(wx.StaticText(panel, label="Tamano de cuadricula:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        self._grid_size = wx.Choice(panel, choices=["10", "20", "40"])
        self._grid_size.SetSelection(1)
        hbox3.Add(self._grid_size, 1, wx.EXPAND)
        vbox.Add(hbox3, 0, wx.EXPAND | wx.ALL, 5)

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
        self.SetSize((450, 420))

        self.Bind(wx.EVT_BUTTON, self._on_ok, btn_ok)

    def _field(self, parent, label: str, attr: str):
        box = wx.BoxSizer(wx.VERTICAL)
        st = wx.StaticText(parent, label=label)
        tc = wx.TextCtrl(parent)
        setattr(self, f"_{attr}", tc)
        box.Add(st, 0, wx.BOTTOM, 2)
        box.Add(tc, 0, wx.EXPAND)
        return box

    def _on_ok(self, event):
        self._info.title = self._title.GetValue().strip()
        self._info.author = self._author.GetValue().strip()
        self._info.description = self._description.GetValue().strip()
        self._info.orientation = self._orientation.GetStringSelection()
        self._info.theme = self._theme.GetStringSelection()
        self._info.show_grid = self._show_grid.GetValue()
        self._info.grid_size = int(self._grid_size.GetStringSelection())
        if not self._info.title:
            self._info.title = "Sin titulo"
        self.EndModal(wx.ID_OK)

    def GetDiagramInfo(self) -> DiagramInfo:
        return self._info
