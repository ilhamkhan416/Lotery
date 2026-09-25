class HKLottoEvaluator:
    @staticmethod
    def evaluate_hit(bbfs_7digit, actual_result_4d):
        """
        Mengecek apakah result 4D tercakup dalam BBFS 7 digit.
        Kategori: '4D', '3D', '2D', atau 'MISS'
        """
        result_digits = [int(d) for d in str(actual_result_4d).zfill(4)]
        unique_result_digits = set(result_digits)
        bbfs_set = set(bbfs_7digit)

        # Hitung berapa digit unik result yang ada di dalam BBFS
        matched_count = len(unique_result_digits.intersection(bbfs_set))

        # Jika result memiliki angka kembar (misal 8224 -> unik 3 digit)
        if len(unique_result_digits) < 4:
            if matched_count == len(unique_result_digits):
                return "4D"  # Seluruh digit pembentuknya ada di BBFS
            elif matched_count == 2:
                return "3D"
            elif matched_count == 1:
                return "2D"
            else:
                return "MISS"

        # Result 4 digit unik biasa
        if matched_count == 4:
            return "4D"
        elif matched_count == 3:
            return "3D"
        elif matched_count == 2:
            return "2D"
        else:
            return "MISS"

    @classmethod
    def calculate_summary(cls, history_logs):
        """
        Menghitung persentase akurasi real-time dari riwayat backtest.
        """
        total = len(history_logs)
        if total == 0:
            return {}

        v1_hits = {"4D": 0, "3D": 0, "2D": 0, "MISS": 0}
        v2_hits = {"4D": 0, "3D": 0, "2D": 0, "MISS": 0}

        for log in history_logs:
            v1_hits[log["v1_result"]] += 1
            v2_hits[log["v2_result"]] += 1

        return {
            "total_evaluated_periods": total,
            "variasi_1": {
                "counts": v1_hits,
                "accuracy_4d_pct": round((v1_hits["4D"] / total) * 100, 2),
                "overall_winrate_pct": round(((total - v1_hits["MISS"]) / total) * 100, 2)
            },
            "variasi_2": {
                "counts": v2_hits,
                "accuracy_4d_pct": round((v2_hits["4D"] / total) * 100, 2),
                "overall_winrate_pct": round(((total - v2_hits["MISS"]) / total) * 100, 2)
            }
        }
