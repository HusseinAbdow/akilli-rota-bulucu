import networkx as nx
import pandas as pd
import random
from generate_graf import graf_uret, kontrol_yazdir

# 1. Create the graph (using the function from the other file)
G = graf_uret()

def yolu_Sadelestir(path):
    """
    Detect and remove unnecessary cycles in the given path.
    Uses a Dictionary for speed.
    E.g.: [0, 5, 7, 9, 7, 10] -> [0, 5, 7, 10]
    """
    cleaned = []
    seen = {}  # Dictionary: Key-Value mapping.

    # The 'seen' dict acts as memory.
    # It stores which node appears at which index in the cleaned list.
    # Structure: {Node_No: Index_No} e.g.: {0:0, 5:1, 7:2}

    for node in path:
        # CYCLE DETECTION
        # If the current node is already in memory (seen),
        # it means we visited it before and looped back.
        if node in seen:
            
            # cut back to the previous index
            idx = seen[node]
            cleaned = cleaned[:idx+1]
            # memory cleanup
            # Since we truncated the list, deleted nodes must also be removed from memory (seen).
            # We rebuild the dict only for nodes remaining in 'cleaned'.
            seen = {n: i for i, n in enumerate(cleaned)}  # Python built-in to enumerate a list with indices.
        else:
            cleaned.append(node) # Add to list
            seen[node] = len(cleaned) - 1 # Store in memory (Node: Index)

    return cleaned
"""
test_path =  [
    0, 3, 7, 12, 18, 21, 33, 40, 7, 12, 45, 50, 33, 21, 
    77, 88, 99, 77, 12, 3, 150, 160, 170, 12, 18, 200]

print("Original path:", test_path)
print("After simplification:", yolu_Sadelestir(test_path))

"""
def  yol_gecerli_mi(G, path, S, D):
    """
    Check whether the given path follows the rules.
    1. Path must not be empty.
    2. It must start at the requested source (S) and end at the destination (D).
    3. Every step on the path must be physically connected in the graph.
    """
    # Empty or very short paths are invalid
    if not path or len(path) < 2:
        return False
    
    # Start and end check
    if path[0] != S:
        return False
    if path[-1] != D:
        return False
    
    # Does every step exist in the graph?
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        if not G.has_edge(u, v): # Query whether an edge between nodes u and v is defined in the in-memory graph.
            return False
    
    return True
def generate_random_path(G, source, destination, max_steps=300):
    """
    Generate a random but valid path from the
    source node to the destination node.
    """
    for _ in range(500):  # allow many attempts
        path = [source]
        current = source
        visited = {source}

        while current != destination and len(path) < max_steps: # This condition stops the loop when the path gets too long.
            neighbors = list(G.neighbors(current))

            if not neighbors:
                break
            


            # Unvisited neighbors
            unvisited = [n for n in neighbors if n not in visited]

            # 80% chance: go to an unvisited neighbor
            if unvisited and random.random() < 0.8:
                next_node = random.choice(unvisited)
            else:
                # 20% chance: pick a random neighbor
                next_node = random.choice(neighbors)

            path.append(next_node)
            visited.add(next_node)
            current = next_node

        if current == destination:
            return yolu_Sadelestir(path)

    return None

def tamamla_path(G, path, D, max_steps=300): #→ Will be IMPORTANT in the GA / SA stage. Can be modified.
    """
    Complete a broken or half-finished path after mutation
    so that it reaches D.
    """

    if not path:
        return None

    current = path[-1]
    steps = 0

    while current != D and steps < max_steps:
        neighbors = list(G.neighbors(current))

        if not neighbors:
            return None  

        nxt = random.choice(neighbors)
        path.append(nxt)
        current = nxt
        steps += 1

    return yolu_Sadelestir(path) 

# → Will be used in the Simulated Annealing (SA) code. Can be modified.


def generate_neighbor_path(G, path, S, D): 
    """
    Generate a neighbor path for SA by making
    a small change to the existing path.
    """
    
    if len(path) < 3:
        return path[:]  
    
    idx = random.randint(1, len(path) - 2)
    
    new_path = path[:idx]
    
    completed = tamamla_path(G, new_path, D)
    
    if completed is None:
        return path[:]
    
    return completed


"""
#  CODE TEST 

# 1. Pick random Source (S) and Destination (D)
nodes_list = list(G.nodes())
S = random.choice(nodes_list)
D = random.choice(nodes_list)


# S and D must not be the same
while S == D:
    D = random.choice(nodes_list)

print(f"\n--- Searching route: {S} -> {D} ---")

# 2. Call the function (assign result to 'random_path')
random_path = generate_random_path(G, S, D)

if random_path: 
    print("Path found.")
    
    print(f"path= {random_path}")
    print(f"Step count: {len(random_path)}")
    
    # 3. Validity check
    is_valid = yol_gecerli_mi(G, random_path, S, D)
    print(f"Is path valid? {is_valid}")

    
    # Is the list length equal to the set (unique elements) length?
    if len(random_path) == len(set(random_path)):

        
        print("No node is repeated.")
    else:
        print("ERROR: Repeated nodes exist")

else:
    # If no path found after 500 attempts
    print("No path found. Try again.")


"""
