import networkx as nx
import matplotlib.pyplot as plt
from generate_graf import graf_uret

# Graf olustur
G = graf_uret()

# alt graf olustur
nodes = list(G.nodes())[:40]
H = G.subgraph(nodes)

plt.figure(figsize=(8, 8))
pos = nx.spring_layout(H, seed=241)
nx.draw(H, pos, node_size=50, edge_color='gray')

plt.title("Mini UI (40 Nodes)")
plt.show()
