import json
from src.engine import HKLottoEngine
from src.evaluator import HKLottoEvaluator

def load_data(filepath="data/paito_master.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def run_pipeline():
    paito_data = load_data()
    engine = HKLottoEngine()
    
    # Extract seluruh result 4D
    all_draws = [item["result"] for item in paito_data]

    # --- TAHAP 1: Prediksi Periode Mendatang ---
    analysis_next = engine.analyze(all_draws)
    
    print("=" * 60)
    print("      HK LOTO ANALYZER - PURE LOCAL ALGORITHM")
    print("=" * 60)
    print(f"Total Data Historis Diproses: {len(all_draws)} Periode")
    print("-" * 60)
    print(f">>> PREDIKSI BBFS PERIODE BERIKUTNYA <<<")
    print(f"Variasi 1 (Trend-Follower) : {analysis_next['variasi_1_trend']}")
    print(f"Variasi 2 (Reversal/Hybrid): {analysis_next['variasi_2_reversal']}")
    print("=" * 60)

    # --- TAHAP 2: Backtesting (Data Uji 2 Sep 2026 s/d Hari Ini) ---
    # Asumsi data di-cutoff untuk pelatihan sampai index tertentu (1 Sep 2026)
    cutoff_index = 0
    for idx, item in enumerate(paito_data):
        if item.get("tanggal") == "2026-09-01":
            cutoff_index = idx + 1
            break

    if cutoff_index > 0 and cutoff_index < len(paito_data):
        test_history = []
        for i in range(cutoff_index, len(paito_data)):
            train_draws = all_draws[:i]
            actual_result = all_draws[i]
            actual_date = paito_data[i].get("tanggal", f"Periode-{i}")

            # Predict
            pred = engine.analyze(train_draws)
            
            # Evaluate
            res_v1 = HKLottoEvaluator.evaluate_hit(pred["variasi_1_trend"], actual_result)
            res_v2 = HKLottoEvaluator.evaluate_hit(pred["variasi_2_reversal"], actual_result)

            test_history.append({
                "tanggal": actual_date,
                "result": actual_result,
                "v1_result": res_v1,
                "v2_result": res_v2
            })

        summary = HKLottoEvaluator.calculate_summary(test_history)
        
        print("\n" + "=" * 60)
        print("   LIVE BACKTESTING RESULTS (2 Sep 2026 - Hari Ini)")
        print("=" * 60)
        print(f"Total Periode Pengujian: {summary['total_evaluated_periods']} Hari")
        print("\n[VARIASI 1 - TREND]")
        print(f"• Win-Rate Total (2D/3D/4D): {summary['variasi_1']['overall_winrate_pct']}%")
        print(f"• Akurasi Jackpot 4D      : {summary['variasi_1']['accuracy_4d_pct']}%")
        print(f"• Rincian Hit             : {summary['variasi_1']['counts']}")
        
        print("\n[VARIASI 2 - REVERSAL]")
        print(f"• Win-Rate Total (2D/3D/4D): {summary['variasi_2']['overall_winrate_pct']}%")
        print(f"• Akurasi Jackpot 4D      : {summary['variasi_2']['accuracy_4d_pct']}%")
        print(f"• Rincian Hit             : {summary['variasi_2']['counts']}")
        print("=" * 60)

if __name__ == "__main__":
    run_pipeline()
