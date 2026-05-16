from __future__ import annotations
import json
import os
import sys
import threading
import urllib.request
import urllib.error
import wx


GITHUB_OWNER = "bastidasaul06-rgb"
GITHUB_REPO = "-DiagramasAccesibles-"
CURRENT_VERSION = "1.0"

API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


def _get_local_exe() -> str:
    if getattr(sys, 'frozen', False):
        return sys.executable
    return os.path.join(os.path.dirname(sys.executable), "DiagramasAccesibles.exe")


def _get_app_dir() -> str:
    return os.path.dirname(_get_local_exe())


class UpdateChecker:
    def __init__(self, parent: wx.Window):
        self._parent = parent

    def check(self, silent: bool = False):
        def _worker():
            try:
                req = urllib.request.Request(API_URL, headers={"User-Agent": "DiagramasAccesibles"})
                try:
                    resp = urllib.request.urlopen(req, timeout=10)
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        if not silent:
                            wx.CallAfter(wx.MessageBox,
                                "No hay actualizaciones disponibles por el momento.",
                                "Sin actualizaciones", wx.OK | wx.ICON_INFORMATION)
                    else:
                        if not silent:
                            wx.CallAfter(wx.MessageBox,
                                f"Error del servidor: {e.code}", "Error", wx.OK | wx.ICON_WARNING)
                    return
                data = json.loads(resp.read().decode("utf-8"))
                latest_tag = data.get("tag_name", "")
                if not latest_tag:
                    return
                if latest_tag == CURRENT_VERSION:
                    if not silent:
                        wx.CallAfter(wx.MessageBox, "Ya tienes la version mas reciente.", "Actualizacion", wx.OK | wx.ICON_INFORMATION)
                    return
                assets = data.get("assets", [])
                exe_asset = None
                for asset in assets:
                    name = asset.get("name", "")
                    if name.endswith(".exe"):
                        exe_asset = asset
                        break
                if not exe_asset:
                    if not silent:
                        wx.CallAfter(wx.MessageBox,
                            "El release no contiene un archivo .exe.", "Sin actualizacion",
                            wx.OK | wx.ICON_INFORMATION)
                    return
                download_url = exe_asset["browser_download_url"]
                release_notes = data.get("body", "Nueva version disponible.")
                wx.CallAfter(self._ask_update, latest_tag, download_url, release_notes)
            except urllib.error.URLError:
                if not silent:
                    wx.CallAfter(wx.MessageBox, "No se pudo conectar a GitHub. Revise su conexion.", "Error", wx.OK | wx.ICON_WARNING)
            except (json.JSONDecodeError, KeyError):
                if not silent:
                    wx.CallAfter(wx.MessageBox, "Respuesta inesperada del servidor.", "Error", wx.OK | wx.ICON_WARNING)

        threading.Thread(target=_worker, daemon=True).start()

    def _ask_update(self, tag: str, url: str, notes: str):
        dlg = UpdateDialog(self._parent, tag, notes)
        if dlg.ShowModal() == wx.ID_YES:
            self._download_and_install(tag, url)
        dlg.Destroy()

    def _download_and_install(self, tag: str, url: str):
        dlg = wx.ProgressDialog("Descargando actualizacion", "Descargando...", maximum=100, parent=self._parent,
                                style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "DiagramasAccesibles"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 8192
                temp_dir = _get_app_dir()
                temp_path = os.path.join(temp_dir, f"update_{tag}.exe")
                with open(temp_path, "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            wx.CallAfter(dlg.Update, int(downloaded * 100 / total))
            wx.CallAfter(dlg.Update, 100)
            wx.CallAfter(self._finish_update, temp_path)
        except Exception as e:
            wx.CallAfter(dlg.Destroy)
            wx.CallAfter(wx.MessageBox, f"Error al descargar: {e}", "Error", wx.OK | wx.ICON_ERROR)

    def _finish_update(self, new_exe: str):
        old_exe = _get_local_exe()
        updater_bat = os.path.join(_get_app_dir(), "_update.bat")
        bat_content = f"""@echo off
timeout /t 2 /nobreak >nul
del "{old_exe}"
ren "{new_exe}" "DiagramasAccesibles.exe"
start "" "{old_exe}"
del "%~f0"
"""
        with open(updater_bat, "w") as f:
            f.write(bat_content)
        wx.MessageBox(
            "Actualizacion descargada. La aplicacion se cerrara para aplicar los cambios.",
            "Actualizacion", wx.OK | wx.ICON_INFORMATION
        )
        os.startfile(updater_bat)
        self._parent.Close()


class UpdateDialog(wx.Dialog):
    def __init__(self, parent, tag: str, notes: str):
        wx.Dialog.__init__(self, parent, title="Actualizacion disponible", size=(450, 350))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        msg = f"Version {tag} disponible.\n\nNotas de la version:\n{notes}"
        tc = wx.TextCtrl(panel, value=msg, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
                         size=(410, 200))
        vbox.Add(tc, 1, wx.EXPAND | wx.ALL, 10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_yes = wx.Button(panel, wx.ID_YES, "&Descargar e instalar")
        btn_yes.SetDefault()
        btn_no = wx.Button(panel, wx.ID_NO, "&Cancelar")
        btn_sizer.Add(btn_yes, 0, wx.RIGHT, 10)
        btn_sizer.Add(btn_no, 0)
        vbox.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

        panel.SetSizer(vbox)
