# Contributing

¡Gracias por tu interés en contribuir a Diagramas de Flujo Accesibles!

## Requisitos

- Python 3.12+
- wxPython 4.2.5
- Git
- PyInstaller (solo para compilar .exe)

## Entorno de desarrollo

```bash
git clone https://github.com/bastidasaul06-rgb/-DiagramasAccesibles-.git
cd -DiagramasAccesibles-
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Reportar bugs

Usa la sección [Issues](https://github.com/bastidasaul06-rgb/-DiagramasAccesibles-/issues) e incluye:

- Pasos para reproducir el error
- Captura de pantalla o log de error (`error.log`)
- Versión del programa (Ayuda > Acerca de)

## Hacer cambios

1. Crea un branch: `git checkout -b feature/nombre-corto`
2. Haz tus cambios
3. Prueba con `python main.py`
4. Confirma que no hay errores de lint
5. Crea un Pull Request describiendo qué cambia y por qué

## Compilar .exe

```bash
.\venv\Scripts\python.exe -m PyInstaller DiagramasAccesibles.spec --clean
```

El .exe se genera en `dist/DiagramasAccesibles.exe`.

## Notas

- El proyecto es solo Windows
- La accesibilidad con NVDA/JAWS es prioridad
- No uses dependencias externas sin justificarlas en el PR
