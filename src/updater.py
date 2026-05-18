from __future__ import annotations
import json
import os
import re
import sys
import threading
import urllib.request
import urllib.error
import wx


GITHUB_OWNER = "bastidasaul06-rgb"
GITHUB_REPO = "-DiagramasAccesibles-"
CURRENT_VERSION = "v1.1"

API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


def _parse_version(tag: str) -> tuple[int, ...]:
    """Convierte un tag tipo v1.2.3 en una tupla comparable (1, 2, 3)."""
    nums = re.findall(r"\d+", tag)
    return tuple(int(n) for n in nums) if nums else (0,)


def _is_newer(latest_tag: str, current_tag: str) -> bool:
    """Devuelve True si latest_tag es más nuevo que current_tag."""
    return _parse_version(latest_tag) > _parse_version(current_tag)


def _get_local_exe() -> str:
    if getattr(sys, 'frozen', False):
        return sys.executable
    return os.path.join(_get_app_dir(), "DiagramasAccesibles.exe")


def _get_app_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _format_size(size_bytes: int) -> str:
    """Formatea bytes a KB/MB/GB en un texto corto para mostrar al usuario."""
    if size_bytes >= 1_000_000_000:
        return f"{size_bytes / 1_000_000_000:.2f} GB"
    elif size_bytes >= 1_000_000:
        return f"{size_bytes / 1_000_000:.2f} MB"
    elif size_bytes >= 1_000:
        return f"{size_bytes / 1_000:.2f} KB"
    return f"{size_bytes} B"


class UpdateDialog(wx.Dialog):
    def __init__(self, parent, tag: str, notes: str, size: int = 0):
        wx.Dialog.__init__(self, parent, title="Actualización disponible", size=(450, 380))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        size_text = f"Tamaño: {_format_size(size)}" if size else ""
        msg = f"Versión {tag} disponible."
        if size_text:
            msg += f"\n{size_text}"
        msg += f"\n\nNotas de la versión:\n{notes}"
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

        self.Bind(wx.EVT_BUTTON, self._on_yes, btn_yes)
        self.Bind(wx.EVT_BUTTON, self._on_no, btn_no)

        panel.SetSizer(vbox)

    def _on_yes(self, event):
        self.EndModal(wx.ID_YES)

    def _on_no(self, event):
        self.EndModal(wx.ID_NO)


class DownloadDialog(wx.Dialog):
    def __init__(self, parent, tag: str, total_size: int):
        wx.Dialog.__init__(self, parent, title="Descargando actualización", size=(450, 150))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self._label = wx.StaticText(panel, label=f"Descargando versión {tag}...")
        vbox.Add(self._label, 0, wx.ALL, 10)

        self._size_label = wx.StaticText(panel, label="0 / " + _format_size(total_size))
        vbox.Add(self._size_label, 0, wx.LEFT | wx.RIGHT, 10)

        self._gauge = wx.Gauge(panel, range=100, size=(410, 24))
        self._gauge.SetFocus()
        vbox.Add(self._gauge, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(vbox)

    def update_progress(self, downloaded: int, total: int):
        pct = int(downloaded * 100 / total) if total else 0
        self._gauge.SetValue(pct)
        self._size_label.SetLabel(f"{_format_size(downloaded)} / {_format_size(total)}")
        self._label.SetLabel(f"Descargando... {pct}%")


class UpdateChecker:
    def __init__(self, parent: wx.Window):
        self._parent = parent

    def check(self, silent: bool = False):
        """Consulta GitHub Releases en segundo plano y muestra el diálogo si hay nueva versión."""
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
                if not _is_newer(latest_tag, CURRENT_VERSION):
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
                size = exe_asset.get("size", 0)
                release_notes = data.get("body", "Nueva version disponible.")
                wx.CallAfter(self._ask_update, latest_tag, download_url, release_notes, size)
            except urllib.error.URLError:
                if not silent:
                    wx.CallAfter(wx.MessageBox, "No se pudo conectar a GitHub. Revise su conexion.", "Error", wx.OK | wx.ICON_WARNING)
            except (json.JSONDecodeError, KeyError):
                if not silent:
                    wx.CallAfter(wx.MessageBox, "Respuesta inesperada del servidor.", "Error", wx.OK | wx.ICON_WARNING)

        threading.Thread(target=_worker, daemon=True).start()

    def _ask_update(self, tag: str, url: str, notes: str, size: int = 0):
        dlg = UpdateDialog(self._parent, tag, notes, size)
        if dlg.ShowModal() == wx.ID_YES:
            self._download_and_install(tag, url, size)
        dlg.Destroy()

    def _download_and_install(self, tag: str, url: str, total_size: int):
        """Descarga el ejecutable en segundo plano y actualiza el progreso en tiempo real."""
        dlg = DownloadDialog(self._parent, tag, total_size)
        dlg.Show()

        temp_dir = _get_app_dir()
        temp_path = os.path.join(temp_dir, f"update_{tag}.exe")

        def _worker(dlg_ref):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "DiagramasAccesibles"})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    total = int(resp.headers.get("Content-Length", 0)) or total_size
                    downloaded = 0
                    chunk_size = 8192
                    with open(temp_path, "wb") as f:
                        while True:
                            chunk = resp.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                wx.CallAfter(dlg_ref.update_progress, downloaded, total)
                wx.CallAfter(dlg_ref.Destroy)
                wx.CallAfter(self._finish_update, temp_path)
            except Exception as e:
                wx.CallAfter(dlg_ref.Destroy)
                wx.CallAfter(wx.MessageBox, f"Error al descargar: {e}", "Error", wx.OK | wx.ICON_ERROR)

        threading.Thread(target=_worker, args=(dlg,), daemon=True).start()

    def _finish_update(self, new_exe: str):
        """Aplica la actualización en .exe compilado o informa ruta en modo fuente."""
        if not getattr(sys, 'frozen', False):
            wx.MessageBox(
                f"Descarga terminada.\nGuardado en: {new_exe}",
                "Descarga completada", wx.OK | wx.ICON_INFORMATION
            )
            return

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
            "Actualización descargada. La aplicación se cerrará para aplicar los cambios.",
            "Actualización", wx.OK | wx.ICON_INFORMATION
        )
        os.startfile(updater_bat)
        self._parent.Close()
