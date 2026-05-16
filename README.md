# Diagramas de Flujo Accesibles

Aplicación de escritorio para Windows que permite crear diagramas de flujo de forma completamente accesible con lectores de pantalla como NVDA y JAWS.

Desarrollada en Python con wxPython, pensada desde cero para que una persona ciega pueda usarla sin necesidad de ver la pantalla.

## Características

- Navegación completa por teclado: Tab, flechas, F6 para cambiar entre áreas
- Anuncios por voz al mover nodos y al consultar posición (Ctrl+P)
- Compatible con NVDA y JAWS mediante MSAA
- 5 tipos de nodo: Inicio, Proceso, Decisión, Entrada/Salida y Fin
- Conexión de nodos mediante diálogo accesible (Alt+Shift+C)
- Guardar y abrir archivos (.dfd)
- Exportar a PNG y SVG
- Panel de propiedades editable
- Zoom y cuadrícula
- Plantillas predefinidas

## Requisitos

- Windows 10 o superior (64 bits)
- No requiere instalación

## Uso

1. Descargar y ejecutar `DiagramasAccesibles.exe`
2. Presionar "Crear diagrama" o "Plantillas"
3. Usar F6 para moverse entre paleta, lienzo y propiedades
4. Tab para navegar entre nodos, flechas para moverlos
5. Alt+Shift+C para conectar nodos
6. Ctrl+Guardar para guardar el diagrama

Ver la guía de uso completa en `guia_de_uso.txt`.

## Desarrollo

### Dependencias

```
pip install -r requirements.txt
```


## Licencia

GNU General Public License v3.0 - ver [LICENSE](LICENSE).

## Créditos

- **Estefanía** — desarrollo
- **Saúl** — pruebas y accesibilidad
- **@Wang_ling** — asistencia durante el desarrollo
