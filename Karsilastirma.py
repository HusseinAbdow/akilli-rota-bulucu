import time
import pandas as pd
import os

# Import the required modules
import generate_graf as gg
import Metrics as mt
import ACO_Algorithm as aco_module
import GeneticAlgorithm as ga_module


# ---------------------------------------------------------
# HELPER FUNCTION: COST CALCULATION FOR GA
# ---------------------------------------------------------
def calculate_weighted_cost(G, path, weights):
    """
    Since the Genetic Algorithm only returns a path,
    calculate the comparable 'Weighted Cost' value here
    for comparison with ACO.
    """
    if not path:
        return float('inf')

    # Calculate metrics (Delay, Reliability, Bandwidth)
    d_cost = mt.Total_Delay(G, path)
    r_cost = mt.Total_Reliability(G, path)
    b_cost = mt.Total_Bandwidth(G, path)

    # Formula: (w1 * Delay) + (w2 * Reliability) + (w3 * Bandwidth)
    total_cost = (weights['delay'] * d_cost) + \
                 (weights['reliability'] * r_cost) + \
                 (weights['bandwidth'] * b_cost)

    return total_cost


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------
def main():
    print("\n" + "=" * 80)
    print("      ACO vs GA: DETAILED COMPARISON AND PATH ANALYSIS")
    print("=" * 80)
    print("PARAMETERS:")
    print("   ACO -> Ants: 50 | Iterations : 3000")
    print("   GA  -> Population: 50 | Generations: 3000")
    print("-" * 80)

    # 1. LOAD THE GRAPH
    try:
        G = gg.graf_uret()
        print(f"✅ Graph loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")
    except Exception as e:
        print(f"❌ ERROR: Could not create graph: {e}")
        return

    # 2. FIND AND READ THE DEMAND FILE
    if os.path.exists("data/DemandData.xlsx"):
        df_demands = pd.read_excel("data/DemandData.xlsx")
    elif os.path.exists("BSM307_317_Guz2025_TermProject_DemandData.csv"):
        df_demands = pd.read_csv("data/BSM307_317_Guz2025_TermProject_DemandData(in)(1).csv", sep=";")
    else:
        print("❌ ERROR: Demand file (DemandData) not found!")
        return

    # 3. WEIGHTS (EQUAL FOR BOTH ALGORITHMS)
    weights = {'delay': 0.4, 'reliability': 0.4, 'bandwidth': 0.2}

    results = []

    # HEADERS
    print("\nTEST RESULTS STARTING...\n")

    # LOOP FOR EACH DEMAND
    for index, row in df_demands.iterrows():
        # Data safety (String/Float conversion)
        try:
            S = int(row['src'])
            D = int(row['dst'])
            val = row['demand_mbps']
            B = float(val.replace(',', '.')) if isinstance(val, str) else float(val)
        except:
            continue

        print(f"🔹 SCENARIO {index + 1}: {S} -> {D} (Demand: {B} Mbps)")

        # --- A. RUN ACO ---
        start_aco = time.time()
        aco = aco_module.AntColonyOptimizer(
            G, S, D, B, weights,
            num_ants=50, max_iter=3000,
            alpha=1.0, beta=2.0, evaporation=0.5
        )
        aco_path, aco_cost, _ = aco.run()
        time_aco = time.time() - start_aco

        # --- B. RUN GA ---
        start_ga = time.time()
        ga_path = ga_module.genetic_algorithm(
            G, source=S, target=D, demand_mbps=B,
            pop_size=50, generations=3000,
            mutation_rate=0.1,
            w_delay=weights['delay'], w_rel=weights['reliability'], w_band=weights['bandwidth']
        )
        time_ga = time.time() - start_ga

        # GA cost calculation
        ga_cost = calculate_weighted_cost(G, ga_path, weights) if ga_path else float('inf')

        # --- SAVE AND PRINT RESULTS ---

        # Determine winner
        if aco_cost < ga_cost:
            winner = "ACO"
        elif ga_cost < aco_cost:
            winner = "GA"
        else:
            winner = "TIE" if aco_cost != float('inf') else "FAILED"

        # Print to screen
        print(f"   🔸 [ACO] Time: {time_aco:.4f}s | Cost: {aco_cost:.4f} | Path: {aco_path}")
        print(f"   🔸 [GA ] Time: {time_ga:.4f}s | Cost: {ga_cost:.4f} | Path: {ga_path}")
        print(f"   🏆 WINNER: {winner}")
        print("-" * 50)

        results.append({
            'Scenario': index + 1,
            'ACO_Cost': aco_cost if aco_cost != float('inf') else None,
            'GA_Cost': ga_cost if ga_cost != float('inf') else None,
            'ACO_Time': time_aco,
            'GA_Time': time_ga,
            'ACO_Path': str(aco_path),
            'GA_Path': str(ga_path)
        })

    # 4. GENERAL SUMMARY AND AVERAGES
    if results:
        df_res = pd.DataFrame(results)

        avg_aco_cost = df_res['ACO_Cost'].mean()
        avg_ga_cost = df_res['GA_Cost'].mean()
        avg_aco_time = df_res['ACO_Time'].mean()
        avg_ga_time = df_res['GA_Time'].mean()

        print("\n" + "=" * 80)
        print("📊 GENERAL PERFORMANCE SUMMARY")
        print("=" * 80)
        print(f"{'Metric':<20} | {'ACO':<15} | {'GA':<15}")
        print("-" * 60)
        print(f"{'Average Cost':<20} | {avg_aco_cost:<15.4f} | {avg_ga_cost:<15.4f}")
        print(f"{'Average Time (s)':<20} | {avg_aco_time:<15.4f} | {avg_ga_time:<15.4f}")
        print("-" * 60)

        success_aco = df_res['ACO_Cost'].count()
        success_ga = df_res['GA_Cost'].count()
        print(f"Successful solutions : ACO ({success_aco}/{len(df_res)}) - GA ({success_ga}/{len(df_res)})")
        print("=" * 80)


if __name__ == "__main__":
    main()
