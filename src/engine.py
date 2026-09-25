import numpy as np

class HKLottoEngine:
    def __init__(self, decay_rate=0.003, weight_decay=0.4, weight_markov=0.35, weight_gap=0.25):
        self.decay_rate = decay_rate
        self.w_decay = weight_decay
        self.w_markov = weight_markov
        self.w_gap = weight_gap

    def _calculate_time_decay(self, draws):
        """Layer 1: Exponential Time-Decay Weighting"""
        N = len(draws)
        scores = np.zeros(10)
        for t, draw in enumerate(draws):
            weight = np.exp(-self.decay_rate * (N - 1 - t))
            digits = [int(d) for d in str(draw).zfill(4)]
            for d in digits:
                scores[d] += weight
        
        # Normalisasi skor 0.0 - 1.0
        return scores / np.max(scores) if np.max(scores) > 0 else scores

    def _calculate_gap_scores(self, draws):
        """Layer 1: Gap & Overdue Normalization"""
        N = len(draws)
        last_seen = {d: -1 for d in range(10)}
        
        for t, draw in enumerate(draws):
            digits = set([int(d) for d in str(draw).zfill(4)])
            for d in digits:
                last_seen[d] = t
                
        gaps = np.array([N - 1 - last_seen[d] for d in range(10)])
        # Normalisasi skor gap
        return gaps / np.max(gaps) if np.max(gaps) > 0 else gaps

    def _calculate_markov_position(self, draws):
        """Layer 2: First-Order Markov Chain per Posisi (As, Kop, Kepala, Ekor)"""
        if len(draws) < 2:
            return np.zeros(10)

        # Matriks transisi 10x10 untuk 4 posisi
        transition_matrix = np.zeros((4, 10, 10))
        
        for t in range(len(draws) - 1):
            curr_digits = [int(d) for d in str(draws[t]).zfill(4)]
            next_digits = [int(d) for d in str(draws[t+1]).zfill(4)]
            
            for pos in range(4):
                transition_matrix[pos, curr_digits[pos], next_digits[pos]] += 1

        # Prediksi probabilitas berdasarkan digit periode terakhir
        last_draw = [int(d) for d in str(draws[-1]).zfill(4)]
        pos_scores = np.zeros(10)
        
        for pos in range(4):
            last_digit = last_draw[pos]
            row = transition_matrix[pos, last_digit, :]
            total = np.sum(row)
            if total > 0:
                pos_scores += (row / total)

        return pos_scores / np.max(pos_scores) if np.max(pos_scores) > 0 else pos_scores

    def analyze(self, draws):
        """
        Input: list of string/int result 4D (ex: ['8294', '1503', ...])
        Output: Variasi 1 (Trend) & Variasi 2 (Reversal) BBFS 7 Digit
        """
        # 1. Hitung Sub-Skor
        s_decay = self._calculate_time_decay(draws)
        s_gap = self._calculate_gap_scores(draws)
        s_markov = self._calculate_markov_position(draws)

        # 2. Agregasi Skor Total
        score_trend = (self.w_decay * s_decay) + (self.w_markov * s_markov)
        score_reversal = (self.w_decay * s_decay) + (self.w_gap * s_gap)

        # 3. Ranking Digit 0-9
        rank_trend = np.argsort(score_trend)[::-1]
        rank_gap = np.argsort(s_gap)[::-1]

        # 4. Alokasi 2 Variasi BBFS 7 Digit
        # Variasi 1: 7 Digit Trend Tertinggi
        var1 = sorted([int(d) for d in rank_trend[:7]])

        # Variasi 2: 4 Digit Trend Tertinggi + 3 Digit Gap/Overdue Tertinggi
        top_trend_4 = list(rank_trend[:4])
        top_gap_3 = [d for d in rank_gap if d not in top_trend_4][:3]
        var2 = sorted([int(d) for d in top_trend_4 + top_gap_3])

        return {
            "variasi_1_trend": var1,
            "variasi_2_reversal": var2,
            "scores": {
                "trend": {d: round(float(score_trend[d]), 4) for d in range(10)},
                "reversal": {d: round(float(score_reversal[d]), 4) for d in range(10)}
            }
        }
