import wx
from src.panels.new_dialog import NewDiagramDialog
from src.panels.template_dialog import TemplateDialog


class WelcomePanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._parent_frame = parent

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.AddStretchSpacer(2)

        title = wx.StaticText(self, label="Diagramas de Flujo Accesibles")
        title_font = wx.Font(22, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        vbox.Add(title, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 20)

        subtitle = wx.StaticText(self, label="Cree diagramas de flujo de forma accesible")
        subtitle_font = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        subtitle.SetFont(subtitle_font)
        vbox.Add(subtitle, 0, wx.ALIGN_CENTER | wx.BOTTOM, 30)

        btn_create = wx.Button(self, label="&Crear diagrama")
        btn_create.SetMinSize((250, 50))
        btn_create.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        btn_create.SetToolTip("Ctrl+N: Crear un nuevo diagrama de flujo desde cero")
        btn_create.Bind(wx.EVT_BUTTON, self._on_create)
        vbox.Add(btn_create, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)

        btn_templates = wx.Button(self, label="&Plantillas")
        btn_templates.SetMinSize((250, 50))
        btn_templates.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        btn_templates.SetToolTip("Seleccionar una plantilla predefinida para comenzar")
        btn_templates.Bind(wx.EVT_BUTTON, self._on_templates)
        vbox.Add(btn_templates, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)

        vbox.AddStretchSpacer(1)

        info = wx.StaticText(self, label="Atajos: Ctrl+N nuevo  |  Ctrl+O abrir  |  Ctrl+Shift+N crear nodo  |  F6 cambiar modo")
        info_font = wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        info.SetFont(info_font)
        vbox.Add(info, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        self.SetSizer(vbox)

    def _on_create(self, event):
        dlg = NewDiagramDialog(self._parent_frame)
        if dlg.ShowModal() == wx.ID_OK:
            info = dlg.GetDiagramInfo()
            self._parent_frame.create_new_diagram(info)
        dlg.Destroy()

    def _on_templates(self, event):
        dlg = TemplateDialog(self._parent_frame)
        if dlg.ShowModal() == wx.ID_OK:
            template = dlg.GetSelectedTemplate()
            if template:
                self._parent_frame.load_template(template)
        dlg.Destroy()
