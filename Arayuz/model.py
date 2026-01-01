import networkx as nx
from dataclasses import dataclass
from typing import List, Optional


__all__ = ["Node", "Link", "NetworkTopology"]


@dataclass
class Node:
    id: int
    processing_delay: float
    reliability: float

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "processing_delay": self.processing_delay,
            "reliability": self.reliability,
        }


@dataclass
class Link:
    source: int
    target: int
    bandwidth: float
    delay: float
    reliability: float

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "bandwidth": self.bandwidth,
            "delay": self.delay,
            "reliability": self.reliability,
        }


class NetworkTopology:
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node: Node) -> None:
        self.graph.add_node(int(node.id), data=node)

    def add_link(self, link: Link) -> None:
        self.graph.add_edge(int(link.source), int(link.target), data=link)

    def get_nodes(self) -> List[Node]:
        return [self.graph.nodes[n]["data"] for n in self.graph.nodes]

    def get_links(self) -> List[Link]:
        return [self.graph.edges[u, v]["data"] for u, v in self.graph.edges]

    def get_node(self, u: int) -> Optional[Node]:
        return self.graph.nodes[u]["data"] if self.graph.has_node(u) else None

    def get_link(self, u: int, v: int) -> Optional[Link]:
        return self.graph.edges[u, v]["data"] if self.graph.has_edge(u, v) else None

    def clear(self) -> None:
        self.graph.clear()

    @staticmethod
    def from_nx_graph(G: nx.Graph) -> "NetworkTopology":
        topology = NetworkTopology()

        for node_id, data in G.nodes(data=True):
            topology.add_node(Node(
                id=int(node_id),
                processing_delay=float(data.get("processing_delay_ms", 0.0)),
                reliability=float(data.get("node_reliability", 1.0)),
            ))

        for u, v, data in G.edges(data=True):
            topology.add_link(Link(
                source=int(u),
                target=int(v),
                bandwidth=float(data.get("bandwidth_mbps", 100.0)),
                delay=float(data.get("link_delay_ms", 5.0)),
                reliability=float(data.get("link_reliability", 1.0)),
            ))

        return topology

