import time
import pandas as pd
import os

# Gerekli modülleri import ediyoruz
import GraphUpdate as gg
import Metrics as mt
import ACO_Algorithm as aco_module
import GeneticAlgorithm as ga_module


# ---------------------------------------------------------
# YARDIMCI FONKSİYON: GA İÇİN MALİYET HESAPLAMA
# ---------------------------------------------------------
def calculate_weighted_cost(G, path, weights):
    """
    Genetik Algoritma sadece yol döndürdüğü için,
    ACO ile karşılaştırılabilir 'Ağırlıklı Maliyet' (Cost)
    değerini burada hesaplıyoruz.
    """
    if not path:
        return float('inf')

    # Metrikleri hesapla (Gecikme, Güvenilirlik, Bant Genişliği)
    d_cost = mt.Total_Delay(G, path)
    r_cost = mt.Total_Reliability(G, path)
    b_cost = mt.Total_Bandwidth(G, path)

    # Formül: (w1 * Delay) + (w2 * Reliability) + (w3 * Bandwidth)
    total_cost = (weights['delay'] * d_cost) + \
                 (weights['reliability'] * r_cost) + \
                 (weights['bandwidth'] * b_cost)

    return total_cost


# ---------------------------------------------------------
# ANA PROGRAM
# ---------------------------------------------------------
def main():
    print("\n" + "=" * 80)
    print("      ACO vs GA: DETAYLI KARŞILAŞTIRMA VE YOL ANALİZİ")
    print("=" * 80)
    print("PARAMETRELER:")
    print("   ACO -> Karınca: 50 | İterasyon : 3000")
    print("   GA  -> Popülasyon: 50 | Jenerasyon: 3000")
    print("-" * 80)

    # 1. GRAFİĞİ YÜKLE
    try:
        G = gg.graf_uret()
        print(f"✅ Graf Yüklendi: {len(G.nodes)} Düğüm, {len(G.edges)} Kenar")
    except Exception as e:
        print(f"❌ HATA: Graf oluşturulamadı: {e}")
        return

    # 2. TALEP DOSYASINI BUL VE OKU
    if os.path.exists("data/DemandData.xlsx"):
        df_demands = pd.read_excel("data/DemandData.xlsx")
    elif os.path.exists("BSM307_317_Guz2025_TermProject_DemandData.csv"):
        df_demands = pd.read_csv("data/BSM307_317_Guz2025_TermProject_DemandData(in)(1).csv", sep=";")
    else:
        print("❌ HATA: Talep dosyası (DemandData) bulunamadı!")
        return

    # 3. AĞIRLIKLAR (İKİ ALGORİTMA İÇİN EŞİT)
    weights = {'delay': 0.4, 'reliability': 0.4, 'bandwidth': 0.2}

    results = []

    # BAŞLIKLAR
    print("\nTEST SONUÇLARI BAŞLIYOR...\n")

    # HER BİR TALEP İÇİN DÖNGÜ
    for index, row in df_demands.iterrows():
        # Veri güvenliği (String/Float dönüşümü)
        try:
            S = int(row['src'])
            D = int(row['dst'])
            val = row['demand_mbps']
            B = float(val.replace(',', '.')) if isinstance(val, str) else float(val)
        except:
            continue

        print(f"🔹 SENARYO {index + 1}: {S} -> {D} (Talep: {B} Mbps)")

        # --- A. ACO ÇALIŞTIR ---
        start_aco = time.time()
        aco = aco_module.AntColonyOptimizer(
            G, S, D, B, weights,
            num_ants=50, max_iter=3000,
            alpha=1.0, beta=2.0, evaporation=0.5
        )
        aco_path, aco_cost, _ = aco.run()
        time_aco = time.time() - start_aco

        # --- B. GA ÇALIŞTIR ---
        start_ga = time.time()
        ga_path = ga_module.genetic_algorithm(
            G, source=S, target=D, demand_mbps=B,
            pop_size=50, generations=3000,
            mutation_rate=0.1,
            w_delay=weights['delay'], w_rel=weights['reliability'], w_band=weights['bandwidth']
        )
        time_ga = time.time() - start_ga

        # GA Maliyet Hesabı
        ga_cost = calculate_weighted_cost(G, ga_path, weights) if ga_path else float('inf')

        # --- SONUÇLARI KAYDET VE YAZDIR ---

        # Kazanan Belirle
        if aco_cost < ga_cost:
            winner = "ACO"
        elif ga_cost < aco_cost:
            winner = "GA"
        else:
            winner = "EŞİT" if aco_cost != float('inf') else "BAŞARISIZ"

        # Ekrana Yazdır
        print(f"   🔸 [ACO] Süre: {time_aco:.4f}s | Maliyet: {aco_cost:.4f} | Yol: {aco_path}")
        print(f"   🔸 [GA ] Süre: {time_ga:.4f}s | Maliyet: {ga_cost:.4f} | Yol: {ga_path}")
        print(f"   🏆 KAZANAN: {winner}")
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

    # 4. GENEL ÖZET VE ORTALAMALAR
    if results:
        df_res = pd.DataFrame(results)

        avg_aco_cost = df_res['ACO_Cost'].mean()
        avg_ga_cost = df_res['GA_Cost'].mean()
        avg_aco_time = df_res['ACO_Time'].mean()
        avg_ga_time = df_res['GA_Time'].mean()

        print("\n" + "=" * 80)
        print("📊 GENEL PERFORMANS ÖZETİ")
        print("=" * 80)
        print(f"{'Metrik':<20} | {'ACO':<15} | {'GA':<15}")
        print("-" * 60)
        print(f"{'Ortalama Maliyet':<20} | {avg_aco_cost:<15.4f} | {avg_ga_cost:<15.4f}")
        print(f"{'Ortalama Süre (sn)':<20} | {avg_aco_time:<15.4f} | {avg_ga_time:<15.4f}")
        print("-" * 60)

        success_aco = df_res['ACO_Cost'].count()
        success_ga = df_res['GA_Cost'].count()
        print(f"Başarılı Çözüm Sayısı : ACO ({success_aco}/{len(df_res)}) - GA ({success_ga}/{len(df_res)})")
        print("=" * 80)


if __name__ == "__main__":
    main()