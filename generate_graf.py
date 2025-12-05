import random
import networkx as nx


# hocadan genel node sayisi ve kenar olasligi
N_NODES = 250
P_EDGE = 0.4
SEED = 245

# hocadan gelen özellik aralıkları
node_proc_delay_range  = (0.5, 2.0)       # ms
node_reliability_range = (0.95, 0.999)    # olaslik

edge_link_delay_range  = (3.0, 15.0)      # ms
edge_bandwidth_range   = (100.0, 1000.0)  # Mbps
edge_reliability_range = (0.95, 0.999)    # olaslik

# Sonuçların tekrarlanabilir olması için global RNG tohumunu/seed ayarlar.
def seeded_random(seed):
    
    random.seed(seed)


# Bu, grafiğin bağlı olduğundan emin olur.
def bagli_graf_olustur(G, n, p, seed=None):
    deneme_sayisi = 0
    while  True:
        # Eğer grafik bağlıysa, geri döndür.
        if nx.is_connected(G):
            return G

        deneme_sayisi += 1

        # degilse farklı tohumlarla/seed birkaç kez yeniden oluştur.
        if seed is None:
            yeni_seed= None
        else:
            yeni_seed = seed + deneme_sayisi

        seeded_random(yeni_seed)
        G = nx.erdos_renyi_graph(n, p, seed=yeni_seed)


# Graf oluşturucu
def graf_uret(n=N_NODES, p=P_EDGE, seed=SEED, force_connected=True):

    seeded_random(seed)

    # Erdos-Renyi grafiği oluşturur
    G = nx.erdos_renyi_graph(n, p, seed=seed)

    # Bu, grafiğin bağlı olduğundan emin olur.
    if force_connected:
        G = bagli_graf_olustur(G, n, p, seed=seed)

    # Düğüm özelliklerini atar
    for node in G.nodes():
        G.nodes[node]['processing_delay_ms'] = round(random.uniform(*node_proc_delay_range), 4)
        G.nodes[node]['node_reliability']    = round(random.uniform(*node_reliability_range), 6)

    # kenar özelliklerini atar
    for u, v in G.edges():
        G.edges[u, v]['link_delay_ms']   = round(random.uniform(*edge_link_delay_range), 4)
        G.edges[u, v]['bandwidth_mbps']  = round(random.uniform(*edge_bandwidth_range), 3)
        G.edges[u, v]['link_reliability']= round(random.uniform(*edge_reliability_range), 6)

    return G

# Grafik yapısının doğru olup olmadığını doğrulamak
def kontrol_yazdir(G):
    print("GRAF HIZLI KONTROL")
    print("Düğüm sayısı:", G.number_of_nodes())
    print("Kenar sayısı:", G.number_of_edges())

    node = list(G.nodes())[1]
    print(f"Örnek düğüm {node} özellikler:", G.nodes[node])

    u, v = list(G.edges())[1]
    print(f"Örnek kenar ({u}, {v}) özellikler:", G.edges[u, v])

    print("Bağlı mı?:", nx.is_connected(G))

# Eğer ana sınıf ise, bunu çalıştır
if __name__ == "__main__":
    G = graf_uret(seed=SEED)
    kontrol_yazdir(G)
