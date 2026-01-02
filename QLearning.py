import numpy as np
import random
import networkx as nx
import generate_graf 
import Metrics       


EPISODES = 5000      
ALPHA = 0.1            
GAMMA = 0.9            
EPSILON = 0.1          


W_DELAY = 0.33
W_RELIABILITY = 0.33
W_RESOURCE = 0.34

class QLearningAgent:
    def __init__(self, start_node, goal_node):
        
        print("Graf yükleniyor...")
        self.G = generate_graf.graf_uret()
        self.nodes = list(self.G.nodes())
        self.num_nodes = len(self.nodes)
        
        self.start_node = start_node
        self.goal_node = goal_node
        
        
        self.q_table = np.zeros((self.num_nodes, self.num_nodes))

    def get_valid_actions(self, current_node):
        """Bir düğümden gidilebilecek komşuları döndürür"""
        return list(self.G.neighbors(current_node))

    def calculate_reward(self, path):
        """
        PDF'teki Formül (Sayfa 6):
        Reward = 1000 / TotalCost(P)
        
        TotalCost(P) = (W_delay * Delay) + (W_rel * RelCost) + (W_res * ResCost)
        """
        
        if not path or path[-1] != self.goal_node:
            return 0.1 
        
        
        total_delay = Metrics.Total_Delay(self.G, path)
        rel_cost = Metrics.Total_Reliability(self.G, path)
        res_cost = Metrics.Total_Bandwidth(self.G, path)
        
        
        total_cost = (W_DELAY * total_delay) + \
                     (W_RELIABILITY * rel_cost) + \
                     (W_RESOURCE * res_cost)
        
        
        if total_cost == 0: total_cost = 0.001
        
        
        return 1000.0 / total_cost

    def train(self):
        print(f"Q-Learning Eğitimi Başlıyor ({EPISODES} epizot)...")
        
        for episode in range(EPISODES):
            current_node = self.start_node
            path = [current_node]
            
            
            for _ in range(self.num_nodes * 2):
                if current_node == self.goal_node:
                    break
                
                actions = self.get_valid_actions(current_node)
                if not actions:
                    break 
                
                
                if random.uniform(0, 1) < EPSILON:
                    next_node = random.choice(actions) 
                else:
                    
                    q_values = [self.q_table[current_node, n] for n in actions]
                    max_q = max(q_values)
                    
                    best_candidates = [actions[i] for i in range(len(actions)) if q_values[i] == max_q]
                    next_node = random.choice(best_candidates)
                
                
                
                
                next_actions = self.get_valid_actions(next_node)
                if next_actions:
                    max_future_q = np.max([self.q_table[next_node, n] for n in next_actions])
                else:
                    max_future_q = 0
                
                
                reward = 0
                if next_node == self.goal_node:
                    temp_path = path + [next_node]
                    reward = self.calculate_reward(temp_path)
                
                current_q = self.q_table[current_node, next_node]
                
                
                new_q = (1 - ALPHA) * current_q + ALPHA * (reward + GAMMA * max_future_q)
                self.q_table[current_node, next_node] = new_q
                
                current_node = next_node
                path.append(current_node)
                
            if (episode + 1) % 1000 == 0:
                print(f"Epizot {episode + 1}/{EPISODES} tamamlandı...")

        print("Eğitim Bitti!")

    def get_best_path(self):
        """Eğitilmiş Q-Tablosunu kullanarak en iyi yolu çıkarır"""
        path = [self.start_node]
        current_node = self.start_node
        visited = set([self.start_node])
        
        print(f"\nEn iyi yol aranıyor ({self.start_node} -> {self.goal_node})...")
        
        while current_node != self.goal_node:
            actions = self.get_valid_actions(current_node)
            
            valid_actions = [n for n in actions if n not in visited]
            
            if not valid_actions:
                print("Hata: Yol tıkandı!")
                return None
            
            
            q_values = [self.q_table[current_node, n] for n in valid_actions]
            best_next_node = valid_actions[np.argmax(q_values)]
            
            path.append(best_next_node)
            visited.add(best_next_node)
            current_node = best_next_node
            
            if len(path) > self.num_nodes: 
                print("Hata: Sonsuz döngü tespit edildi.")
                return None
                
        return path


if __name__ == "__main__":
    
    import pandas as pd
    import Metrics
    import generate_graf
    
    print("\n" + "="*60)
    print("📢 Q-Learning Standalone Modu (Excel Verisi Okunuyor)...")
    print("="*60)
    
    try:
        
        df = pd.read_excel("data/DemandData.xlsx")
        print(f"📂 {len(df)} talep (senaryo) bulundu.\n")
        
        
        print("⚙️ Graf oluşturuluyor (generate_graf)...")
        G = generate_graf.graf_uret()

        
        for index, row in df.iterrows():
            try:
                
                src = int(row.iloc[0])
                dst = int(row.iloc[1])
                demand_val = str(row.iloc[2]).replace(',', '.')
                demand = float(demand_val)
                
                print(f"🔹 Senaryo {index+1}: {src} -> {dst} (Demand: {demand})")
                
                
                agent = QLearningAgent(src, dst)
                agent.G = G 
                
                
                agent.train()  
                # ----------------------------------
                
                path = agent.get_best_path()
                
                if path:
                    d = Metrics.Total_Delay(G, path)
                    r = Metrics.Total_Reliability(G, path)
                    bw = Metrics.Total_Bandwidth(G, path)
                    
                    print(f"   ✅ Yol: {path}")
                    print(f"   📊 Delay: {d:.2f} | Rel: {r:.2f} | BW: {bw:.2f}")
                else:
                    print("   ❌ Yol bulunamadı.")
                
                print("-" * 40)
                
            except Exception as e:
                print(f"⚠️ Hata (Satır {index+1}): {e}")
                
    except Exception as e:
        print(f"❌ Genel Hata: {e}")
        print("Lütfen 'generate_graf.py' dosyasının ve 'data' klasörünün varlığını kontrol et.")
