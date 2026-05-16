import wx
from src.canvas.diagram_canvas import DiagramCanvas
from src.canvas.diagram_model import NodeModel, EdgeModel
from src.accessibility.canvas_accessible import CanvasAccessible
from src.panels.welcome_panel import WelcomePanel
from src.panels.tool_palette import ToolPalette
from src.panels.properties_panel import PropertiesPanel
from src.panels.node_create_dialog import NodeCreateDialog


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


ID_NEW = wx.ID_NEW
ID_OPEN = wx.ID_OPEN
ID_SAVE = wx.ID_SAVE
ID_SAVEAS = wx.ID_SAVEAS
ID_EXIT = wx.ID_EXIT
ID_UNDO = wx.ID_UNDO
ID_REDO = wx.ID_REDO
ID_DELETE = wx.ID_DELETE
ID_SELECTALL = wx.ID_SELECTALL
ID_ZOOM_IN = wx.NewIdRef()
ID_ZOOM_OUT = wx.NewIdRef()
ID_ZOOM_RESET = wx.NewIdRef()
ID_ZOOM_FIT = wx.NewIdRef()
ID_TOGGLE_GRID = wx.NewIdRef()
ID_INSERT_NODE = wx.NewIdRef()
ID_INSERT_CONNECTION = wx.NewIdRef()
ID_EXPORT_PNG = wx.NewIdRef()
ID_EXPORT_SVG = wx.NewIdRef()
ID_ABOUT = wx.ID_ABOUT
ID_SHORTCUTS = wx.NewIdRef()
ID_CHECK_UPDATES = wx.NewIdRef()


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Diagramas de Flujo Accesibles", size=(1000, 700))

        self._diagram_title = ""
        self._current_area = -1

        self._create_menu_bar()

        self.tool_palette = ToolPalette(self)
        self.properties_panel = PropertiesPanel(self)

        self.canvas = DiagramCanvas(self, skip_test_nodes=True)
        self.canvas.Hide()

        self.welcome = WelcomePanel(self)

        self._content = wx.BoxSizer(wx.HORIZONTAL)

        self._content.Add(self.tool_palette, 0, wx.EXPAND)
        self._center_sizer = wx.BoxSizer(wx.VERTICAL)
        self._center_sizer.Add(self.welcome, 1, wx.EXPAND)
        self._center_sizer.Add(self.canvas, 1, wx.EXPAND)
        self._content.Add(self._center_sizer, 1, wx.EXPAND)
        self._content.Add(self.properties_panel, 0, wx.EXPAND)

        self.SetSizer(self._content)

        self.CreateStatusBar(number=1)
        self.SetStatusText("Bienvenido. Cree un diagrama para comenzar.")

        self.tool_palette.Hide()
        self.properties_panel.Hide()

        self.canvas.controller.set_selection_callback(self._on_selection_changed)
        self.canvas.controller.set_connect_mode_callback(self._on_connect_mode_changed)

        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.Bind(wx.EVT_CLOSE, self._on_close)

        from src.updater import UpdateChecker
        wx.CallLater(3000, UpdateChecker(self).check, True)
        self.Show()

    def _create_menu_bar(self):
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        file_menu.Append(ID_NEW, "&Nuevo\tCtrl+N", "Crear un nuevo diagrama")
        file_menu.Append(ID_OPEN, "&Abrir...\tCtrl+O", "Abrir un diagrama guardado")
        file_menu.AppendSeparator()
        file_menu.Append(ID_SAVE, "&Guardar\tCtrl+S", "Guardar el diagrama actual")
        file_menu.Append(ID_SAVEAS, "Guardar &como...\tCtrl+Shift+S", "Guardar con otro nombre")
        file_menu.AppendSeparator()
        file_menu.Append(ID_EXPORT_PNG, "Exportar PNG...", "Exportar como imagen PNG")
        file_menu.Append(ID_EXPORT_SVG, "Exportar SVG...", "Exportar como SVG")
        file_menu.AppendSeparator()
        file_menu.Append(ID_EXIT, "&Salir\tAlt+F4", "Cerrar la aplicacion")
        menu_bar.Append(file_menu, "&Archivo")

        edit_menu = wx.Menu()
        edit_menu.Append(ID_UNDO, "&Deshacer\tCtrl+Z", "Deshacer la ultima accion")
        edit_menu.Append(ID_REDO, "&Rehacer\tCtrl+Y", "Rehacer la accion deshecha")
        edit_menu.AppendSeparator()
        edit_menu.Append(ID_DELETE, "&Eliminar\tSupr", "Eliminar el nodo seleccionado")
        edit_menu.Append(ID_SELECTALL, "Seleccionar &todo\tCtrl+E", "Seleccionar todos los nodos")
        menu_bar.Append(edit_menu, "&Editar")

        insert_menu = wx.Menu()
        insert_menu.Append(ID_INSERT_NODE, "&Nodo...\tCtrl+Shift+N", "Insertar un nuevo nodo")
        insert_menu.Append(ID_INSERT_CONNECTION, "&Conexion\tAlt+Shift+C", "Conectar el nodo seleccionado con otro")
        menu_bar.Append(insert_menu, "&Insertar")

        view_menu = wx.Menu()
        view_menu.Append(ID_ZOOM_IN, "Acercar\tCtrl++", "Aumentar el zoom")
        view_menu.Append(ID_ZOOM_OUT, "Alejar\tCtrl+-", "Disminuir el zoom")
        view_menu.Append(ID_ZOOM_RESET, "Zoom 100%\tCtrl+0", "Restablecer zoom al 100%")
        view_menu.Append(ID_ZOOM_FIT, "Ajustar a ventana\tCtrl+Shift+F", "Ajustar todos los nodos a la ventana")
        view_menu.AppendSeparator()
        view_menu.Append(ID_TOGGLE_GRID, "&Mostrar cuadricula", "Mostrar u ocultar la cuadricula", wx.ITEM_CHECK)
        menu_bar.Append(view_menu, "&Ver")

        help_menu = wx.Menu()
        help_menu.Append(ID_SHORTCUTS, "&Atajos de teclado...\tF1", "Ver atajos de teclado disponibles")
        help_menu.Append(ID_CHECK_UPDATES, "&Buscar actualizaciones...", "Verificar si hay una nueva version")
        help_menu.AppendSeparator()
        help_menu.Append(ID_ABOUT, "&Acerca de...", "Informacion sobre la aplicacion")
        menu_bar.Append(help_menu, "&Ayuda")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self._on_new, id=ID_NEW)
        self.Bind(wx.EVT_MENU, self._on_open, id=ID_OPEN)
        self.Bind(wx.EVT_MENU, self._on_save, id=ID_SAVE)
        self.Bind(wx.EVT_MENU, self._on_save_as, id=ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self._on_exit, id=ID_EXIT)
        self.Bind(wx.EVT_MENU, self._on_undo, id=ID_UNDO)
        self.Bind(wx.EVT_MENU, self._on_redo, id=ID_REDO)
        self.Bind(wx.EVT_MENU, self._on_delete, id=ID_DELETE)
        self.Bind(wx.EVT_MENU, self._on_select_all, id=ID_SELECTALL)
        self.Bind(wx.EVT_MENU, self._on_zoom_in, id=ID_ZOOM_IN)
        self.Bind(wx.EVT_MENU, self._on_zoom_out, id=ID_ZOOM_OUT)
        self.Bind(wx.EVT_MENU, self._on_zoom_reset, id=ID_ZOOM_RESET)
        self.Bind(wx.EVT_MENU, self._on_zoom_fit, id=ID_ZOOM_FIT)
        self.Bind(wx.EVT_MENU, self._on_toggle_grid, id=ID_TOGGLE_GRID)
        self.Bind(wx.EVT_MENU, self._on_insert_node, id=ID_INSERT_NODE)
        self.Bind(wx.EVT_MENU, self._on_insert_connection, id=ID_INSERT_CONNECTION)
        self.Bind(wx.EVT_MENU, self._on_export_png, id=ID_EXPORT_PNG)
        self.Bind(wx.EVT_MENU, self._on_export_svg, id=ID_EXPORT_SVG)
        self.Bind(wx.EVT_MENU, self._on_shortcuts, id=ID_SHORTCUTS)
        self.Bind(wx.EVT_MENU, self._on_check_updates, id=ID_CHECK_UPDATES)
        self.Bind(wx.EVT_MENU, self._on_about, id=ID_ABOUT)

    def _on_new(self, event):
        from src.panels.new_dialog import NewDiagramDialog
        if self.canvas.IsShown() and self.canvas.model.nodes:
            r = wx.MessageBox("Se perdera el diagrama actual. Continuar?", "Nuevo diagrama",
                              wx.YES_NO | wx.ICON_QUESTION)
            if r != wx.YES:
                return
        dlg = NewDiagramDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            info = dlg.GetDiagramInfo()
            self.create_new_diagram(info)
        dlg.Destroy()

    def _on_open(self, event):
        if not self.canvas.IsShown():
            return
        dlg = wx.FileDialog(self, "Abrir diagrama", wildcard="Diagrama de Flujo (*.dfd)|*.dfd",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            import json
            try:
                with open(dlg.GetPath(), "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._diagram_title = data.get("title", "Sin titulo")
                self.canvas.clear_all()
                for ndata in data.get("nodes", []):
                    node = NodeModel(ndata["type"], ndata["label"], ndata["x"], ndata["y"], ndata.get("description", ""))
                    self.canvas.model.add_node(node)
                for edata in data.get("edges", []):
                    nodes = self.canvas.model.nodes
                    sid = edata["source_id"]
                    tid = edata["target_id"]
                    src = next((n for n in nodes if n.id == sid), None)
                    tgt = next((n for n in nodes if n.id == tid), None)
                    if src and tgt:
                        edge = EdgeModel(src.id, tgt.id, edata.get("label", ""))
                        self.canvas.model.add_edge(edge)
                self.canvas.refresh()
                self._on_selection_changed()
                self.canvas.SetFocus()
            except Exception as e:
                wx.MessageBox(f"Error al abrir el archivo: {e}", "Error", wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def _on_save(self, event):
        self._do_save()

    def _on_save_as(self, event):
        self._do_save(as_new=True)

    def _do_save(self, as_new=False):
        if not self.canvas.IsShown():
            return
        import json
        data = {
            "title": self._diagram_title,
            "nodes": [
                {"type": n.type, "label": n.label, "description": n.description, "x": n.x, "y": n.y}
                for n in self.canvas.model.nodes
            ],
            "edges": [
                {"source_id": e.source_id, "target_id": e.target_id, "label": e.label}
                for e in self.canvas.model.edges
            ],
        }
        dlg = wx.FileDialog(self, "Guardar diagrama", wildcard="Diagrama de Flujo (*.dfd)|*.dfd",
                            defaultFile=f"{self._diagram_title}.dfd", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                with open(dlg.GetPath(), "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.SetStatusText(f"Guardado: {dlg.GetPath()}")
            except Exception as e:
                wx.MessageBox(f"Error al guardar: {e}", "Error", wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def _on_exit(self, event):
        self.Close()

    def _on_undo(self, event):
        if self.canvas.IsShown():
            self.canvas.controller.undo()

    def _on_redo(self, event):
        if self.canvas.IsShown():
            self.canvas.controller.redo()

    def _on_delete(self, event):
        if self.canvas.IsShown():
            self.canvas.controller.delete_selected()

    def _on_select_all(self, event):
        if self.canvas.IsShown():
            self.canvas.controller.select_all()

    def _on_export_png(self, event):
        if not self.canvas.IsShown() or not self.canvas.model.nodes:
            return
        dlg = wx.FileDialog(self, "Exportar PNG", wildcard="PNG (*.png)|*.png",
                            defaultFile=f"{self._diagram_title}.png", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            self.canvas.export_png(dlg.GetPath())
            self.SetStatusText(f"Exportado: {dlg.GetPath()}")
        dlg.Destroy()

    def _on_export_svg(self, event):
        if not self.canvas.IsShown() or not self.canvas.model.nodes:
            return
        dlg = wx.FileDialog(self, "Exportar SVG", wildcard="SVG (*.svg)|*.svg",
                            defaultFile=f"{self._diagram_title}.svg", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            self.canvas.export_svg(dlg.GetPath())
            self.SetStatusText(f"Exportado: {dlg.GetPath()}")
        dlg.Destroy()

    def _on_zoom_in(self, event):
        if self.canvas.IsShown():
            self.canvas.controller.on_zoom_in()

    def _on_zoom_out(self, event):
        if self.canvas.IsShown():
            self.canvas.controller.on_zoom_out()

    def _on_zoom_reset(self, event):
        if self.canvas.IsShown():
            self.canvas.controller.on_zoom_reset()

    def _on_zoom_fit(self, event):
        if self.canvas.IsShown():
            self.canvas.controller.on_zoom_fit()

    def _on_toggle_grid(self, event):
        if self.canvas.IsShown():
            self.canvas.toggle_grid()
            item = self.GetMenuBar().FindItemById(ID_TOGGLE_GRID)
            if item:
                item.Check(self.canvas._show_grid)

    def _on_insert_node(self, event):
        self._open_create_node_dialog()

    def _on_insert_connection(self, event):
        if not self.canvas.IsShown():
            return
        ctrl = self.canvas.controller
        nodes = ctrl.model.nodes
        if len(nodes) < 2:
            wx.MessageBox("Se necesitan al menos 2 nodos.", "Conectar", wx.OK | wx.ICON_INFORMATION)
            return
        fn = ctrl.focus_manager.focused_node
        selected = [n for n in nodes if n.selected]
        source = (selected or [fn])[0] if (selected or fn) else None
        if source is None:
            wx.MessageBox("Seleccione o enfoque el nodo de origen primero.", "Conectar", wx.OK | wx.ICON_INFORMATION)
            return
        from src.panels.connect_dialog import ConnectDialog
        dlg = ConnectDialog(self, source, nodes)
        if dlg.ShowModal() == wx.ID_OK:
            target_id = dlg.get_target_id()
            if target_id:
                target = ctrl.model.get_node_by_id(target_id)
                if target:
                    ctrl._perform_connect(source, target)
        dlg.Destroy()

    def _on_connect_mode_changed(self):
        pass

    def _on_shortcuts(self, event):
        msg = (
            "Atajos de teclado:\n\n"
            "Tab / Shift+Tab    - Navegar entre nodos\n"
            "Enter              - Seleccionar/deseleccionar nodo\n"
            "Flechas            - Mover nodo (8px)\n"
            "Shift+Flechas      - Mover nodo (40px)\n"
            "Ctrl+P             - Anunciar posicion\n"
            "F2                 - Editar etiqueta\n"
            "Supr               - Eliminar nodo\n"
            "Escape             - Deseleccionar todo\n"
            "Ctrl+N             - Nuevo diagrama\n"
            "Ctrl+Shift+N       - Crear nodo\n"
            "Alt+Shift+C        - Conectar nodos\n"
            "Ctrl+E             - Seleccionar todo\n"
            "Ctrl++ / Ctrl+-    - Acercar/Alejar\n"
            "Ctrl+0             - Zoom 100%%\n"
            "Ctrl+Shift+F       - Ajustar a ventana\n"
            "F6 / Shift+F6      - Cambiar de area (paleta/lienzo/propiedades)\n"
            "F1                 - Esta ayuda"
        )
        dlg = wx.Dialog(self, title="Atajos de teclado", size=(500, 420))
        panel = wx.Panel(dlg)
        vbox = wx.BoxSizer(wx.VERTICAL)

        tc = wx.TextCtrl(panel, value=msg, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
                         size=(460, 280))
        font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        tc.SetFont(font)
        vbox.Add(tc, 1, wx.EXPAND | wx.ALL, 10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_copiar = wx.Button(panel, wx.ID_ANY, label="&Copiar")
        btn_copiar.Bind(wx.EVT_BUTTON, lambda e: self._copy_to_clipboard(msg))
        btn_sizer.Add(btn_copiar, 0, wx.RIGHT, 10)
        btn_aceptar = wx.Button(panel, wx.ID_OK, label="&Aceptar")
        btn_aceptar.SetDefault()
        btn_sizer.Add(btn_aceptar, 0)
        vbox.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(vbox)
        dlg.ShowModal()
        dlg.Destroy()

    def _copy_to_clipboard(self, text):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()

    def _on_check_updates(self, event):
        from src.updater import UpdateChecker
        UpdateChecker(self).check(silent=False)

    def _on_about(self, event):
        dlg = wx.Dialog(self, title="Acerca de...", size=(500, 380))
        panel = wx.Panel(dlg)
        vbox = wx.BoxSizer(wx.VERTICAL)

        texto = (
            "Diagramas de Flujo Accesibles - Versión 1.0\n\n"
            "Esta aplicación de diagramas de flujo fue desarrollada en Python "
            "con la necesidad de satisfacer la creación de diagramas de flujo "
            "de forma accesible para personas ciegas o con baja visión. "
            "Ha sido creada con cariño para la comunidad ciega.\n\n"
            "Colaboradores:\n"
            "  - Estefanía: desarrollo principal, programación e implementación general.\n"
            "  - Saúl: pruebas exhaustivas, implementación de toda la accesibilidad "
            "y contribución en múltiples áreas del desarrollo del software.\n\n"
            "Nota de la desarrolladora:\n"
            "Soy una persona que sí puede ver, por lo que la aplicación puede "
            "tener algunos errores de accesibilidad que no haya detectado. "
            "Si encuentra alguno, se agradecería reportarlo en el Foro de la "
            "Sala de Juegos para poder corregirlo y mejorar la herramienta "
            "para todos."
        )

        tc = wx.TextCtrl(panel, value=texto, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
                         size=(460, 250))
        font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        tc.SetFont(font)

        vbox.Add(tc, 1, wx.EXPAND | wx.ALL, 10)

        btn_aceptar = wx.Button(panel, wx.ID_OK, label="&Aceptar")
        btn_aceptar.SetDefault()
        vbox.Add(btn_aceptar, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(vbox)
        dlg.ShowModal()
        dlg.Destroy()

    def _on_char_hook(self, event):
        key = event.GetKeyCode()

        if key == wx.WXK_F6:
            if self.canvas.IsShown():
                if event.ShiftDown():
                    self.cycle_area(forward=False)
                else:
                    self.cycle_area(forward=True)
                return

        if key == ord('C') and event.AltDown() and event.ShiftDown():
            self._on_insert_connection(None)
            return

        elif key == wx.WXK_TAB:
            if not self.canvas.IsShown():
                event.Skip()
                return

            focused = wx.Window.FindFocus()
            if focused is None:
                event.Skip()
                return

            forward = not event.ShiftDown()
            palette_controls = [self.tool_palette._list, self.tool_palette._btn_add]
            props_controls = [self.properties_panel._label_ctrl, self.properties_panel._desc_ctrl]

            if forward and focused in palette_controls and focused is palette_controls[-1]:
                self.canvas.SetFocus()
                return
            if not forward and focused in palette_controls and focused is palette_controls[0]:
                self.canvas.SetFocus()
                return

            if forward and focused in props_controls and focused is props_controls[-1]:
                self.cycle_area(forward=True)
                return
            if not forward and focused in props_controls and focused is props_controls[0]:
                self.cycle_area(forward=False)
                return

            if focused is self.canvas:
                event.Skip()
                return

        event.Skip()

    def cycle_area(self, forward=True):
        areas = []
        area_names = []
        if self.tool_palette.IsShown():
            areas.append(self.tool_palette)
            area_names.append("Paleta de nodos")
        if self.canvas.IsShown():
            areas.append(self.canvas)
            area_names.append("Lienzo de diagrama")
        if self.properties_panel.IsShown():
            areas.append(self.properties_panel)
            area_names.append("Propiedades")

        if not areas:
            return

        if forward:
            self._current_area = (self._current_area + 1) % len(areas)
        else:
            if self._current_area < 0:
                self._current_area = 0
            else:
                self._current_area = (self._current_area - 1) % len(areas)

        name = area_names[self._current_area]
        ctrl = areas[self._current_area]
        ctrl.focus_widget()
        _speak(f"Area: {name}")
        self.SetStatusText(f"Area: {name}")

    def _open_create_node_dialog(self, preselected_type=None):
        if not self.canvas.IsShown():
            return
        dlg = NodeCreateDialog(self, preselected_type)
        if dlg.ShowModal() == wx.ID_OK:
            node_type, label, description = dlg.get_node_info()
            x, y = self.canvas.controller.get_center_position()
            self.canvas.controller.add_node_at(node_type, label, description, x, y)
        dlg.Destroy()

    def _on_selection_changed(self):
        selected = [n for n in self.canvas.model.nodes if n.selected]
        if selected:
            self.properties_panel.show_node(selected[-1])
        else:
            fn = self.canvas.controller.focus_manager.focused_node
            if fn:
                self.properties_panel.show_node(fn)
            else:
                self.properties_panel.hide_panel()
        self._current_area = -1
        n = len(self.canvas.model.nodes)
        e = len(self.canvas.model.edges)
        s = sum(1 for nd in self.canvas.model.nodes if nd.selected)
        title = self._diagram_title or "Diagrama"
        self.SetStatusText(f"{title} | {n} nodos | {e} conexiones | Seleccionados: {s}")

    def create_new_diagram(self, info):
        self._diagram_title = info.title
        self.canvas.clear_all()
        self.canvas._grid_size = info.grid_size
        self.canvas._show_grid = info.show_grid
        if self.GetMenuBar().FindItemById(ID_TOGGLE_GRID):
            self.GetMenuBar().FindItemById(ID_TOGGLE_GRID).Check(info.show_grid)

        self._switch_to_canvas()
        self.canvas.SetFocus()

    def load_template(self, template):
        self._diagram_title = template["name"]
        self.canvas.clear_all()

        for ndata in template["nodes"]:
            node = NodeModel(ndata["type"], ndata["label"], ndata["x"], ndata["y"], ndata.get("description", ""))
            self.canvas.model.add_node(node)

        for edata in template["edges"]:
            nodes = self.canvas.model.nodes
            if edata["source"] < len(nodes) and edata["target"] < len(nodes):
                edge = EdgeModel(nodes[edata["source"]].id, nodes[edata["target"]].id, edata.get("label", ""))
                self.canvas.model.add_edge(edge)

        self._switch_to_canvas()
        self.canvas.refresh()
        self.canvas.SetFocus()
        self._on_selection_changed()

    def _switch_to_canvas(self):
        self.welcome.Hide()
        self.canvas.Show()
        self.tool_palette.Show()
        self._content.Layout()

        self._canvas_accessible = CanvasAccessible(self.canvas)
        self.canvas.SetAccessible(self._canvas_accessible)
        self._on_selection_changed()

    def _on_close(self, event):
        self.canvas.Destroy()
        event.Skip()

    def GetDiagramTitle(self):
        return self._diagram_title


class DiagramApp(wx.App):
    def OnInit(self):
        self.SetAppName("DiagramasAccesibles")
        import sys
        sys.excepthook = self._on_unhandled_exception
        frame = MainFrame()
        self.SetTopWindow(frame)
        return True

    def _on_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        import traceback
        msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        try:
            wx.MessageBox(
                f"Ocurrio un error inesperado:\n\n{exc_value}\n\n"
                "Detalles guardados en error.log",
                "Error", wx.OK | wx.ICON_ERROR
            )
            with open("error.log", "w", encoding="utf-8") as f:
                f.write(msg)
        except Exception:
            pass
