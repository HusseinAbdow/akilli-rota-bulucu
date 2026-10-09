import networkx as nx
from math import log,exp
import generate_graf as gg

def Total_Delay(G,path):
    """
        Calculate the total delay of the given path (Link + Node Processing).
        """
    TotalDelay = 0

    for i in range(len(path)-1):
        u=path[i]
        v=path[i+1]
        TotalDelay += G.edges[u,v]["link_delay_ms"]

    for i in range(1,len(path)-1):
        TotalDelay+=G.nodes[path[i]]["processing_delay_ms"]

    return round(TotalDelay,4)

def Total_Reliability(G,path):
    """
        Calculate the total reliability of the given path.
        Note: -log transformation is used to convert multiplication into addition.
        Lower value = Higher reliability.
        """
    TotalReliability = 0

    for i in range(len(path)-1):
        u=path[i]
        v=path[i+1]
        TotalReliability += (-1*log(G.edges[u,v]["link_reliability"]))

    for i in range(1,len(path)-1):
        TotalReliability+=(-1*log(G.nodes[path[i]]["node_reliability"]))

    return round(TotalReliability,4)

def Total_Bandwidth(G,path):
    """
        Calculate the bandwidth cost of the given path.
        OSPF logic (1000 / Bandwidth) is used.
        """

    ResourceCost=0
    for i in range(len(path)-1):
        u=path[i]
        v=path[i+1]
        ResourceCost+= (1000/G.edges[u,v]["bandwidth_mbps"])
    return round(ResourceCost,4)


if __name__ == "__main__":
    print("--- METRIC CALCULATION TEST STARTING ---\n")

    # 1. Create the graph
    G = gg.graf_uret()
    print(f"Graph created. Node count: {len(G.nodes)}")

    # 2. Find a random path (e.g. shortest path from 0 to 4)
    # Note: Not your algorithm, using a built-in function for testing.
    try:
        sample_path = nx.shortest_path(G, source=0, target=4)
        print(f"Path under test: {sample_path}")
        print("-" * 30)

        # 3. Test your functions

        # --- TEST A: DELAY ---
        delay = Total_Delay(G, sample_path)
        print(f"1. Total Delay (Total_Delay): {delay} ms")

        # --- TEST B: RELIABILITY ---
        reliability_cost = Total_Reliability(G, sample_path)
        actual_rate = exp(-reliability_cost)  # Convert cost back to percentage
        print(f"2. Reliability Cost: {reliability_cost}")
        print(f"   -> Actual Reliability Rate: %{actual_rate * 100:.4f}")

        # --- TEST C: BANDWIDTH ---
        bandwidth_cost = Total_Bandwidth(G, sample_path)
        print(f"3. Bandwidth Cost: {bandwidth_cost}")

        print("-" * 30)
        print("✅ TEST COMPLETED SUCCESSFULLY. Your code runs without errors.")

    except nx.NetworkXNoPath:
        print("❌ Error: No path between selected nodes. Change the seed and try again.")
    except KeyError as e:
        print(f"❌ Error: Name mismatch! Code could not find '{e}'.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
