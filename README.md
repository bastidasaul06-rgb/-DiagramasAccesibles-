# Diagramas de Flujo Accesibles

[![Licencia](https://img.shields.io/badge/Licencia-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-brightgreen)](https://python.org)
[![wxPython](https://img.shields.io/badge/wxPython-4.2.5-orange)](https://wxpython.org)
[![Plataforma](https://img.shields.io/badge/Plataforma-Windows%2010%2B-0078D6)](https://windows.com)
[![GitHub release](https://img.shields.io/github/v/release/bastidasaul06-rgb/-DiagramasAccesibles-)](https://github.com/bastidasaul06-rgb/-DiagramasAccesibles-/releases)
[![Stars](https://img.shields.io/github/stars/bastidasaul06-rgb/-DiagramasAccesibles-)](https://github.com/bastidasaul06-rgb/-DiagramasAccesibles-/stargazers)

Aplicación de escritorio para Windows que permite crear diagramas de flujo de forma completamente accesible con lectores de pantalla como NVDA y JAWS.

Desarrollada en Python con wxPython, pensada desde cero para que una persona ciega pueda usarla sin necesidad de ver la pantalla.

## Palabras clave

Diagramas de flujo accesibles, wxPython, Python, Windows, NVDA, JAWS, MSAA, accesibilidad, editor de diagramas, software para ciegos.

## Características

- Navegación completa por teclado: Tab, flechas, F6 para cambiar entre áreas
- Anuncios por voz al mover nodos y al consultar posición (Ctrl+P)
- Compatible con NVDA y JAWS mediante MSAA
- 5 tipos de nodo: Inicio, Proceso, Decisión, Entrada/Salida y Fin
- Conexión de nodos mediante diálogo accesible (Alt+Shift+C) o modo conectar visual (Ctrl+Shift+C)
- Deshacer/Rehacer (Ctrl+Z/Ctrl+Y) con historial de 50 acciones
- Guardar y abrir archivos (.dfd)
- Exportar a PNG y SVG
- Panel de propiedades editable
- Zoom y cuadrícula
- Plantillas predefinidas
- Actualizador automático integrado (Ayuda > Buscar actualizaciones)
- Manejador global de errores con `error.log`

## Enlaces

- [Releases](https://github.com/bastidasaul06-rgb/-DiagramasAccesibles-/releases)
- [Issues](https://github.com/bastidasaul06-rgb/-DiagramasAccesibles-/issues)
- [Discusiones](https://github.com/bastidasaul06-rgb/-DiagramasAccesibles-/discussions)

## Requisitos

- Windows 10 o superior (64 bits)
- No requiere instalación

## Uso

1. Descargar y ejecutar `DiagramasAccesibles.exe` desde [Releases](https://github.com/bastidasaul06-rgb/-DiagramasAccesibles-/releases)
2. Presionar "Crear diagrama" o "Plantillas"
3. Usar **F6** para moverse entre paleta, lienzo y propiedades
4. **Tab** para navegar entre nodos, **flechas** para moverlos
5. **Alt+Shift+C** para conectar nodos, **Ctrl+Shift+C** para modo conectar visual
6. **Ctrl+Z/Ctrl+Y** para deshacer/rehacer
7. **Ctrl+G** para guardar el diagrama

Ver la guía de uso completa en [`guia_de_uso.txt`](guia_de_uso.txt).

## Desarrollo

### Clonar y ejecutar

```bash
git clone https://github.com/bastidasaul06-rgb/-DiagramasAccesibles-.git
cd -DiagramasAccesibles-
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Compilar .exe

```bash
.\venv\Scripts\python.exe -m PyInstaller DiagramasAccesibles.spec --clean
```

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md) para más detalles.

## Licencia

GNU General Public License v3.0 — ver [LICENSE](LICENSE).

## Créditos

- **Estefanía** — desarrollo
- **Saúl** — pruebas y accesibilidad
- **@Wang_ling** — asistencia durante el desarrollo
