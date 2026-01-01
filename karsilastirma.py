import time
import os
import pandas as pd
import generate_graf
import Metrics
import QLearning
import GeneticAlgorithm
import ACO_Algorithm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

DEMAND_XLSX = os.path.join(DATA_DIR, "DemandData.xlsx")
DEMAND_CSV = os.path.join(DATA_DIR, "DemandData.csv")

def main():
    print("\n" + "="*100)
    print("🚀 GRAND FINAL: 30 SENARYO (Q-LEARNING vs GENETIC vs ACO)")
    print("="*100)

    G = generate_graf.graf_uret()

    try:
        df = pd.read_excel(DEMAND_XLSX)
    except:
        try:
            df = pd.read_csv(DEMAND_CSV, sep=";")
        except:
            print("❌ HATA: DemandData dosyası bulunamadı!")
            return

    print(f"📂 Toplam {len(df)} talep (senaryo) yüklendi.\n")

    header = f"{'No':<4} {'Src->Dst':<10} | {'Q-L Cost':<10} {'Time':<6} | {'Gen Cost':<10} {'Time':<6} | {'ACO Cost':<10} {'Time':<6} | {'KAZANAN':<10}"
    print(header)
    print("-" * 115)

    wins = {'Q-Learn': 0, 'Genetic': 0, 'ACO': 0, 'Draw': 0}
    w_delay, w_rel, w_bw = 0.33, 0.33, 0.34
    weights_list = [w_delay, w_rel, w_bw]

    for index, row in df.iterrows():
        try:
            src = int(row.iloc[0])
            dst = int(row.iloc[1])
            demand = float(str(row.iloc[2]).replace(',', '.'))
        except:
            continue

        start = time.time()
        q_cost = 999999
        try:
            q_agent = QLearning.QLearningAgent(src, dst)
            q_agent.train()
            q_path = q_agent.get_best_path()
            if q_path:
                d = Metrics.Total_Delay(G, q_path)
                r = Metrics.Total_Reliability(G, q_path)
                bw = Metrics.Total_Bandwidth(G, q_path)
                penalty = 500 if bw < demand else 0
                q_cost = (w_delay * d) + (w_rel * r) + (w_bw * (1000 / (bw + 0.1))) + penalty
        except:
            pass
        q_time = time.time() - start

        start = time.time()
        ga_cost = 999999
        try:
            ga_path = GeneticAlgorithm.genetic_algorithm(
                G, src, dst,
                demand_mbps=demand,
                pop_size=25,
                generations=1000,
                w_delay=w_delay,
                w_rel=w_rel,
                w_band=w_bw,
                max_delay=1000
            )
            if ga_path:
                d = Metrics.Total_Delay(G, ga_path)
                r = Metrics.Total_Reliability(G, ga_path)
                bw = Metrics.Total_Bandwidth(G, ga_path)
                penalty = 500 if bw < demand else 0
                ga_cost = (w_delay * d) + (w_rel * r) + (w_bw * (1000 / (bw + 0.1))) + penalty
        except:
            pass
        ga_time = time.time() - start

        start = time.time()
        aco_cost = 999999
        try:
            aco_solver = ACO_Algorithm.AntColonyOptimizer(
                G, src, dst, demand, weights_list,
                num_ants=10,
                max_iter=10
            )
            aco_path, _, _ = aco_solver.run()
            if aco_path:
                d = Metrics.Total_Delay(G, aco_path)
                r = Metrics.Total_Reliability(G, aco_path)
                bw = Metrics.Total_Bandwidth(G, aco_path)
                penalty = 500 if bw < demand else 0
                aco_cost = (w_delay * d) + (w_rel * r) + (w_bw * (1000 / (bw + 0.1))) + penalty
        except:
            pass
        aco_time = time.time() - start

        costs = {'Q-Learn': q_cost, 'Genetic': ga_cost, 'ACO': aco_cost}
        valid_costs = {k: v for k, v in costs.items() if v < 900000}

        winner = "FAIL"
        if valid_costs:
            min_val = min(valid_costs.values())
            winners_list = [k for k, v in valid_costs.items() if v == min_val]
            if len(winners_list) > 1:
                winner = "EŞİT"
                wins['Draw'] += 1
            else:
                winner = winners_list[0]
                wins[winner] += 1

        q_s = f"{q_cost:.2f}" if q_cost < 900000 else "FAIL"
        g_s = f"{ga_cost:.2f}" if ga_cost < 900000 else "FAIL"
        a_s = f"{aco_cost:.2f}" if aco_cost < 900000 else "FAIL"

        print(f"{index+1:<4} {f'{src}->{dst}':<10} | {q_s:<10} {q_time:<6.2f} | {g_s:<10} {ga_time:<6.2f} | {a_s:<10} {aco_time:<6.2f} | {winner:<10}")

    print("-" * 115)
    print(f"🏁 SONUÇ: Q-Learning: {wins['Q-Learn']} | Genetic: {wins['Genetic']} | ACO: {wins['ACO']} | Eşit: {wins['Draw']}")
    print("="*100)

if __name__ == "__main__":
    main()
