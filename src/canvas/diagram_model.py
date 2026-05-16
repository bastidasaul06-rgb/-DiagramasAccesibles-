from __future__ import annotations
from typing import Optional


NODE_TYPES = {
    "start": {"label": "Inicio", "width": 120, "height": 50, "color": "#2E86AB"},
    "process": {"label": "Proceso", "width": 140, "height": 60, "color": "#F5A623"},
    "decision": {"label": "¿Decisión?", "width": 100, "height": 80, "color": "#7ED321"},
    "input_output": {"label": "Entrada/Salida", "width": 140, "height": 60, "color": "#D0021B"},
    "end": {"label": "Fin", "width": 120, "height": 50, "color": "#2E86AB"},
}


class NodeModel:
    _next_id: int = 0

    def __init__(self, node_type: str, label: str, x: float, y: float,
                 description: str = ""):
        NodeModel._next_id += 1
        self.id: int = NodeModel._next_id
        self.type: str = node_type
        self.label: str = label
        self.description: str = description
        self.x: float = x
        self.y: float = y

        info = NODE_TYPES.get(node_type, NODE_TYPES["process"])
        self.width: float = info["width"]
        self.height: float = info["height"]
        self.color: str = info["color"]

        self.selected: bool = False
        self.focused: bool = False

    def hit_test(self, x: float, y: float) -> bool:
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def center_x(self) -> float:
        return self.x + self.width / 2

    def center_y(self) -> float:
        return self.y + self.height / 2

    def get_port_position(self, port: str) -> tuple[float, float]:
        cx = self.center_x()
        cy = self.center_y()
        ports = {
            "top": (cx, self.y),
            "bottom": (cx, self.y + self.height),
            "left": (self.x, cy),
            "right": (self.x + self.width, cy),
        }
        return ports.get(port, (cx, cy))


class EdgeModel:
    _next_id: int = 0

    def __init__(self, source_id: int, target_id: int, label: str = ""):
        EdgeModel._next_id += 1
        self.id: int = EdgeModel._next_id
        self.source_id: int = source_id
        self.target_id: int = target_id
        self.label: str = label
        self.selected: bool = False


class DiagramModel:
    def __init__(self):
        self.nodes: list[NodeModel] = []
        self.edges: list[EdgeModel] = []

    def add_node(self, node: NodeModel) -> NodeModel:
        self.nodes.append(node)
        return node

    def remove_node(self, node_id: int) -> Optional[NodeModel]:
        node = self.get_node_by_id(node_id)
        if node:
            self.nodes.remove(node)
            self.edges = [
                e for e in self.edges
                if e.source_id != node_id and e.target_id != node_id
            ]
        return node

    def add_edge(self, edge: EdgeModel) -> EdgeModel:
        self.edges.append(edge)
        return edge

    def remove_edge(self, edge_id: int) -> Optional[EdgeModel]:
        edge = self.get_edge_by_id(edge_id)
        if edge:
            self.edges.remove(edge)
        return edge

    def get_node_by_id(self, node_id: int) -> Optional[NodeModel]:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_edge_by_id(self, edge_id: int) -> Optional[EdgeModel]:
        for edge in self.edges:
            if edge.id == edge_id:
                return edge
        return None

    def get_connections_for(self, node_id: int) -> str:
        incoming = [e for e in self.edges if e.target_id == node_id]
        outgoing = [e for e in self.edges if e.source_id == node_id]
        parts = []
        if incoming:
            names = []
            for e in incoming:
                n = self.get_node_by_id(e.source_id)
                if n:
                    names.append(n.label)
            parts.append(f"Conectado desde: {', '.join(names)}")
        if outgoing:
            names = []
            for e in outgoing:
                n = self.get_node_by_id(e.target_id)
                if n:
                    names.append(n.label)
            parts.append(f"hacia: {', '.join(names)}")
        return ". ".join(parts)

    def to_dict(self) -> dict:
        return {
            "nodes": [
                {
                    "type": n.type,
                    "label": n.label,
                    "description": n.description,
                    "x": n.x,
                    "y": n.y,
                }
                for n in self.nodes
            ],
            "edges": [
                {
                    "source_id": e.source_id,
                    "target_id": e.target_id,
                    "label": e.label,
                }
                for e in self.edges
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> DiagramModel:
        model = cls()
        node_map = {}
        for ndata in data.get("nodes", []):
            node = NodeModel(ndata["type"], ndata["label"], ndata["x"], ndata["y"], ndata.get("description", ""))
            model.add_node(node)
            node_map[node.id] = node
        for edata in data.get("edges", []):
            edge = EdgeModel(edata["source_id"], edata["target_id"], edata.get("label", ""))
            model.add_edge(edge)
        return model

    def deselect_all(self):
        for node in self.nodes:
            node.selected = False
        for edge in self.edges:
            edge.selected = False

    def clear_focus(self):
        for node in self.nodes:
            node.focused = False
