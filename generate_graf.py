import networkx as nx
import pandas as pd

# Paths to the Excel files
NODE_DATA_PATH = "data/NodeData.xlsx"
EDGE_DATA_PATH = "data/EdgeData.xlsx"


# Build a graph from Excel files
def graf_uret():

    # Create an empty graph
    G = nx.Graph()

    
    # READ NODE DATA
    df_nodes = pd.read_excel(NODE_DATA_PATH)

    # Each row represents one node
    for _, row in df_nodes.iterrows():
        node_id = int(row["node_id"])

        G.add_node(
            node_id,
            processing_delay_ms = float(row["s_ms"]),
            node_reliability    = float(row["r_node"])
        )

   
    # 2) READ EDGE DATA
    df_edges = pd.read_excel(EDGE_DATA_PATH)

    # Each row represents one edge
    for _, row in df_edges.iterrows():
        src = int(row["src"])
        dst = int(row["dst"])

        G.add_edge(
            src,
            dst,
            bandwidth_mbps   = float(row["capacity_mbps"]),
            link_delay_ms    = float(row["delay_ms"]),
            link_reliability = float(row["r_link"])
        )

    return G


# Quick check of the graph structure
def kontrol_yazdir(G):
    print("GRAPH QUICK CHECK")
    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())

    # Print a sample node
    node = list(G.nodes())[0]
    print(f"Sample node {node} attributes:", G.nodes[node])

    # Print a sample edge
    u, v = list(G.edges())[0]
    print(f"Sample edge ({u}, {v}) attributes:", G.edges[u, v])

    print("Is connected?:", nx.is_connected(G))


# Main execution block
if __name__ == "__main__":
    G = graf_uret()
    kontrol_yazdir(G)
