TEMPLATES = [
    {
        "name": "Proceso basico",
        "description": "Inicio, un proceso y fin. Ideal para diagramas simples de un solo paso.",
        "nodes": [
            {"type": "start", "label": "Inicio", "x": 50, "y": 50, "description": "Inicio del proceso"},
            {"type": "process", "label": "Ejecutar tarea", "x": 50, "y": 150, "description": "Paso principal del proceso"},
            {"type": "end", "label": "Fin", "x": 50, "y": 260, "description": "Fin del proceso"},
        ],
        "edges": [
            {"source": 0, "target": 1},
            {"source": 1, "target": 2},
        ],
    },
    {
        "name": "Diagrama con decision",
        "description": "Inicio, decision con dos caminos (Si/No). Para flujos condicionales.",
        "nodes": [
            {"type": "start", "label": "Inicio", "x": 150, "y": 50, "description": "Inicio del proceso"},
            {"type": "process", "label": "Validar datos", "x": 150, "y": 150, "description": "Validar los datos de entrada"},
            {"type": "decision", "label": "Es valido?", "x": 150, "y": 270, "description": "Decidir si los datos son validos"},
            {"type": "process", "label": "Procesar", "x": 150, "y": 400, "description": "Procesar datos validos"},
            {"type": "input_output", "label": "Mostrar error", "x": 350, "y": 270, "description": "Mostrar mensaje de error"},
            {"type": "end", "label": "Fin", "x": 150, "y": 510, "description": "Fin del proceso"},
        ],
        "edges": [
            {"source": 0, "target": 1},
            {"source": 1, "target": 2},
            {"source": 2, "target": 3, "label": "Si"},
            {"source": 2, "target": 4, "label": "No"},
            {"source": 3, "target": 5},
        ],
    },
    {
        "name": "Bucle de validacion",
        "description": "Repite un proceso hasta que se cumpla una condicion. Incluye retroalimentacion.",
        "nodes": [
            {"type": "start", "label": "Inicio", "x": 50, "y": 50, "description": "Inicio"},
            {"type": "process", "label": "Ingresar dato", "x": 50, "y": 150, "description": "Usuario ingresa un dato"},
            {"type": "decision", "label": "Es valido?", "x": 50, "y": 270, "description": "Verificar si el dato es valido"},
            {"type": "process", "label": "Guardar dato", "x": 50, "y": 400, "description": "Guardar el dato en el sistema"},
            {"type": "end", "label": "Fin", "x": 50, "y": 510, "description": "Fin"},
        ],
        "edges": [
            {"source": 0, "target": 1},
            {"source": 1, "target": 2},
            {"source": 2, "target": 3, "label": "Si"},
            {"source": 2, "target": 1, "label": "No"},
            {"source": 3, "target": 4},
        ],
    },
    {
        "name": "Menu de opciones",
        "description": "Un menu con varias opciones que llevan a diferentes procesos.",
        "nodes": [
            {"type": "start", "label": "Inicio", "x": 200, "y": 50, "description": "Inicio del menu"},
            {"type": "process", "label": "Mostrar menu", "x": 200, "y": 150, "description": "Mostrar las opciones disponibles"},
            {"type": "decision", "label": "Opcion 1?", "x": 50, "y": 270, "description": "Decidir si elige la opcion 1"},
            {"type": "decision", "label": "Opcion 2?", "x": 350, "y": 270, "description": "Decidir si elige la opcion 2"},
            {"type": "process", "label": "Ejecutar opcion 1", "x": 50, "y": 400, "description": "Ejecutar la opcion 1"},
            {"type": "process", "label": "Ejecutar opcion 2", "x": 350, "y": 400, "description": "Ejecutar la opcion 2"},
            {"type": "end", "label": "Fin", "x": 200, "y": 510, "description": "Fin del programa"},
        ],
        "edges": [
            {"source": 0, "target": 1},
            {"source": 1, "target": 2},
            {"source": 1, "target": 3},
            {"source": 2, "target": 4, "label": "Si"},
            {"source": 3, "target": 5, "label": "Si"},
            {"source": 4, "target": 6},
            {"source": 5, "target": 6},
        ],
    },
]
