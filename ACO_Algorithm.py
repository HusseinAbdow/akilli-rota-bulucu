import pandas as pd
import random
import math
import os


import generate_graf as gg

# File path fix
# Dynamic path check so the 'data/' folder does not cause errors
# when the project is run on different machines. If files are in the
# main directory, update the path accordingly.
if not os.path.exists("data/NodeData.xlsx") and os.path.exists("NodeData.xlsx"):
    gg.NODE_DATA_PATH = "NodeData.xlsx"
    gg.EDGE_DATA_PATH = "EdgeData.xlsx"

# Add metric calculation and path improvement modules
import Metrics as mt
import path_utilities as pu

class AntColonyOptimizer:
    def __init__(self, G, S, D, demand, weights, num_ants=20, max_iter=50, alpha=1.0, beta=2.0, evaporation=0.5):
        """
        ACO Algorithm Initializer (Constructor).
        Goal: Find the most cost-effective path from S to D under the given constraints.
        
        Parameters:
        - G: Network topology (NetworkX graph object)
        - S, D: Source and destination nodes
        - demand: Requested bandwidth (paths not meeting it are eliminated)
        - weights: Weights for delay, reliability and bandwidth
        - alpha: Influence of pheromone (scent) on selection
        - beta: Influence of heuristic (path quality) on selection
        - evaporation: Evaporation coefficient (for forgetting old paths)
        """
        self.G = G
        self.S = S
        self.D = D
        self.demand = demand 
        self.weights = weights
        self.num_ants = num_ants
        self.max_iter = max_iter
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        
        # --- PHEROMONE INITIALIZATION ---
        self.pheromones = {}
        # Initially assign equal pheromone (1.0) to all paths.
        # This way ants spread completely randomly in the first iteration.
        for u, v in G.edges():
            self.pheromones[(u, v)] = 1.0
            self.pheromones[(v, u)] = 1.0  # Graph is undirected, so also add the reverse direction
            
        # Precompute heuristic values
        # Compute once up front and cache them instead of recomputing for every ant.
        self.heuristic_cache = {}
        self._precompute_heuristics()

    def _precompute_heuristics(self):
        """
        Precompute the heuristic (attractiveness) value for each edge.
        This avoids heavy repeated log/division operations inside the loop.
        """
        for u, v in self.G.edges():
            # Compute and store for the forward direction
            h_val = self._calculate_single_heuristic(u, v)
            self.heuristic_cache[(u, v)] = h_val
            
            # Compute and store for the reverse direction
            h_val_reverse = self._calculate_single_heuristic(v, u)
            self.heuristic_cache[(v, u)] = h_val_reverse

    def _calculate_single_heuristic(self, u, v):
        """
        Calculate the heuristic (attractiveness) value for a single edge (u -> v).
        Heuristic = 1 / (weighted total cost)
        Low cost → High heuristic → More attractive path
        """
        edge_data = self.G.edges[u, v] # Edge data (bandwidth, delay, reliability)
        node_data = self.G.nodes[v]    # Destination node data
        
        # CONSTRAINT CHECK
        # If the link capacity does not meet the requested demand;
        # set its heuristic value to 0. The ant sees it like a "wall".
        if edge_data.get('bandwidth_mbps', 0) < self.demand:
            return 0.0

        # 1. Delay metric
        # Total Delay = Link Delay + Processing Time at the node
        delay_cost = edge_data.get('link_delay_ms', 10) + node_data.get('processing_delay_ms', 1)
        
        # 2. Reliability metric (-log transformation)
        # Reliability is probabilistic (e.g. 0.99) and multiplied in serial systems.
        # But -log() transformation is applied so it can be summed in the cost function.
        # Result: As reliability increases, the cost value approaches zero (decreases).
        r_link = edge_data.get('link_reliability', 0.99)
        r_node = node_data.get('node_reliability', 0.99)

        # Safe lower bound to avoid Log(0) errors
        if r_link <= 0: r_link = 0.0001
        if r_node <= 0: r_node = 0.0001
        rel_cost = (-1 * math.log(r_link)) + (-1 * math.log(r_node))
        
        # 3. Bandwidth metric
        # High bandwidth should be preferred (low cost).
        # Hence Cost = 1000 / Bandwidth formula is used.
        bw = edge_data.get('bandwidth_mbps', 100)
        bw_cost = 1000 / bw if bw > 0 else 10000

        # Weighted Sum
        # Sum three different units with user-provided weights after normalizing.
        total_step_cost = (self.weights['delay'] * delay_cost) + \
                          (self.weights['reliability'] * rel_cost) + \
                          (self.weights['bandwidth'] * bw_cost)
        
        # Cost and heuristic are inversely proportional 
        return 1.0 / (total_step_cost + 0.0001) # (+0.0001 added so denominator is never 0)

    def _select_next_node(self, current_node, visited):
        """
        Select the next node for an ant from its current node.
        Uses roulette wheel selection mechanism.
        """
        neighbors = list(self.G.neighbors(current_node))  # Neighbors of the current node
        
        candidates = []  # Selectable neighbor nodes
        probabilities = [] # Selection probability of each neighbor
        total_prob = 0.0 # Total probability (for normalization)
        
        for n in neighbors:
            # Skip visited nodes to prevent cyclic moves
            if n in visited: 
                continue
            
            # Read from precomputed values
            eta = self.heuristic_cache.get((current_node, n), 0)
            
            if eta == 0: continue # Skip this candidate if heuristic is 0 (insufficient capacity)
            
            # Get pheromone value (1.0 initially)
            tau = self.pheromones.get((current_node, n), 1.0)
            
            # ACO FORMULA: (Pheromone^alpha) * (Heuristic^beta)
            prob = (tau ** self.alpha) * (eta ** self.beta)
            
            candidates.append(n)
            probabilities.append(prob)
            total_prob += prob
            
        if not candidates:  # No suitable neighbor
            return None

        if total_prob == 0: # If probabilities could not be computed, pick randomly
            return random.choice(candidates)
            
        # ROULETTE WHEEL SELECTION
        # Pick a random point between 0 and Total Probability.
        threshold = random.random() * total_prob
        current_sum = 0.0
        for i, p in enumerate(probabilities):
            current_sum += p
            # The node is selected once the cumulative sum passes the threshold.
            if current_sum >= threshold:
                return candidates[i]
        
        return candidates[-1]

    def run(self):
        """
        Run the ACO algorithm, find the best path and its cost.
        
        Return values:
        - best_global_path: Best path (node list)
        - best_global_cost: Total cost of the best path
        - best_metrics: Detailed metrics of the best path
        """
        best_global_path = None
        best_global_cost = float('inf') # Start with infinity (minimization problem)
        best_metrics = {'delay': 0, 'rel_cost': 0, 'bw_cost': 0}
        
        # Convergence check
        # If no new record arrives for a certain time, finish the algorithm early.
        no_improve_count = 0
        
        # Main loop: max_iter iterations
        for iteration in range(self.max_iter):
            all_paths = []  # All successful paths in this iteration
            
            # Run the ants: each searches for a path
            for ant in range(self.num_ants):
                path = [self.S] # Path starts at the source
                visited = set([self.S]) # Set of visited nodes
                current = self.S # Ant's current position
                
                # Ant moves step by step (max 100 steps limit to avoid infinite loops)
                steps = 0
                while current != self.D and steps < 100:
                    nxt = self._select_next_node(current, visited)
                    if nxt is None: break # Stop if there is nowhere to go
                    path.append(nxt)
                    visited.add(nxt)
                    current = nxt
                    steps += 1
                
                # Did the ant reach the destination?
                if current == self.D:
                    # Simplify the found path (clean unnecessary loops) - path_utilities module
                    clean_path = pu.yolu_Sadelestir(path)
                    
                    # Calculate the real metrics of the path
                    d_cost = mt.Total_Delay(self.G, clean_path)
                    r_cost = mt.Total_Reliability(self.G, clean_path)
                    b_cost = mt.Total_Bandwidth(self.G, clean_path)
                    
                    # Total cost: weighted sum formula
                    total_cost = (self.weights['delay'] * d_cost) + \
                                 (self.weights['reliability'] * r_cost) + \
                                 (self.weights['bandwidth'] * b_cost)
                    
                    all_paths.append((clean_path, total_cost))
                    
                    # Update best path (if a lower cost was found)
                    if total_cost < best_global_cost:
                        best_global_cost = total_cost
                        best_global_path = clean_path
                        best_metrics = {'delay': d_cost, 'rel_cost': r_cost, 'bw_cost': b_cost}
                        no_improve_count = 0 # Improvement found, reset counter
            
            if not all_paths: continue # If no ant found a path this round, move to next round

            # Early stopping: stop if no improvement for 10 iterations.
            no_improve_count += 1
            if no_improve_count > 10: break
            
            # Pheromone update

            # 1. Evaporation:
            # Scent on all paths is reduced by a certain ratio.
            # This makes old and bad paths forgotten.
            for key in self.pheromones:
                self.pheromones[key] *= (1.0 - self.evaporation)
            
            # 2. New pheromone deposit:
            # Pheromone is added only to the BEST 3 solutions of this iteration.
            # This strategy makes the solution converge faster.
            all_paths.sort(key=lambda x: x[1]) # Sort by cost (ascending)
            best_iteration_paths = all_paths[:3] 
            
            Q = 10.0  # Pheromone constant
            for path, cost in best_iteration_paths:
                deposit = Q / cost # The lower the cost, the more scent is deposited
                for i in range(len(path) - 1):
                    u, v = path[i], path[i+1]
                    self.pheromones[(u, v)] += deposit
                    self.pheromones[(v, u)] += deposit

        return best_global_path, best_global_cost, best_metrics

#  MAIN EXECUTION BLOCK 
if __name__ == "__main__":
    print("\n--- ACO ALGORITHM RESULTS ---\n")
    
    # Load the graph
    try:
        G = gg.graf_uret()
        print(f"Graph loaded. Node Count: {len(G.nodes)}")
    except Exception as e:
        print(f"ERROR: Could not create graph: {e}")
        exit()

    # Read the demand file (DemandData)
    DEMAND_FILE = "DemandData.xlsx"
    if not os.path.exists(DEMAND_FILE) and os.path.exists("data/DemandData.xlsx"):
        DEMAND_FILE = "data/DemandData.xlsx"
        
    try:
        df_demands = pd.read_excel(DEMAND_FILE)
    except:
        df_demands = pd.DataFrame()

    # SCENARIO WEIGHTS [0.4, 0.4, 0.2]
    weights = {'delay': 0.4, 'reliability': 0.4, 'bandwidth': 0.2}
    print(f"Weights used: {weights}\n")
    
    # Table headers
    header = f"{'No':<4} {'Src':<6} {'Dst':<6} {'Demand':<8} {'Status':<10} {'Delay(ms)':<10} {'Rel(Cost)':<10} {'BW(Cost)':<10} {'TOTAL':<10}"
    print(header)
    print("-" * 85)

    # Variables to keep statistics
    total_scenarios = 0 # Total number of test scenarios
    success_count = 0 # Number of successful solutions
    total_cost_sum = 0.0 # Cost sum of all successful solutions
    
    min_cost_value = float('inf') # Lowest cost (initial: infinity)
    min_cost_info = "" # Info of the lowest-cost scenario

    # Run the algorithm for each row in Excel
    for index, row in df_demands.iterrows():
        total_scenarios += 1
        S = int(row['src']) # Source node
        D = int(row['dst']) # Destination node
        B = float(row['demand_mbps']) # Minimum bandwidth demand
        
        # Run ACO
        aco = AntColonyOptimizer(G, S, D, B, weights, num_ants=20, max_iter=50)
        best_path, cost, metrics = aco.run()
        
        if best_path:
            status = "Success"
            success_count += 1
            total_cost_sum += cost
            
            # Check the lowest cost
            if cost < min_cost_value:
                min_cost_value = cost
                min_cost_info = f"No: {index+1} ({S}->{D})"
            
            cost_str = f"{cost:.2f}"
            d_str = f"{metrics['delay']:.2f}"
            r_str = f"{metrics['rel_cost']:.2f}"
            b_str = f"{metrics['bw_cost']:.2f}"
        else:
            status = "Failed"
            cost_str = "-"
            d_str = "-"
            r_str = "-"
            b_str = "-"
        
        print(f"{index+1:<4} {S:<6} {D:<6} {B:<8} {status:<10} {d_str:<10} {r_str:<10} {b_str:<10} {cost_str:<10}")

    print("-" * 85)
    
    # --- GENERAL SUMMARY TABLE ---
    if success_count > 0:
        avg_cost = total_cost_sum / success_count
    else:
        avg_cost = 0.0
        min_cost_value = 0.0

    print("\n--- GENERAL PERFORMANCE SUMMARY ---")
    print(f"Total Scenarios    : {total_scenarios}")
    print(f"Successful Solutions: {success_count}")
    print(f"Average Cost       : {avg_cost:.2f}")
    print(f"Lowest Cost        : {min_cost_value:.2f} [Scenario {min_cost_info}]")

    print("------------------------------")
