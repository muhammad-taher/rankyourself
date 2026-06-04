import math
from typing import Dict, Any, List

class UnifiedRankingEngine:
    def __init__(self):
        # Asymptotic tuning parameters (k-constants) 
        # These control how smoothly the score curves approach the max limits
        self.K_CF_SOLVES = 300.0  # Decays smoothly around 300+ high-tier solves
        self.K_LC_WEIGHTS = 1000.0 # Decays smoothly around 1000 points (e.g., ~150 H, 300 M, 100 E)
        self.K_AC_SOLVES = 200.0  # AtCoder problem density
        self.K_CC_SOLVES = 400.0  # CodeChef problem density
        self.K_BC_SOLVES = 500.0  # Beecrowd problem density

        # Maximum capped thresholds for ratings (Anti-AI inflation defense)
        self.CF_MAX_RATING = 2400.0  # Grandmaster cap
        self.CC_MAX_RATING = 2200.0  # 5-6 Star cap

    def calculate_codeforces_score(self, solved_problems_ratings: List[int], peak_rating: int) -> float:
        """
        Codeforces: Max 35 Points.
        - Solves (Max 25): Quality-weighted via squared difficulty scale.
        - Peak Rating (Max 10): Linear scaling with lower priority to mitigate AI contest cheating.
        """
        # Part 1: Quality-Weighted Solves
        quality_sum = 0.0
        for rating in solved_problems_ratings:
            # If a problem is unrated (0), default to a baseline entry difficulty of 800
            effective_rating = rating if rating > 0 else 800
            quality_sum += (effective_rating / 1000.0) ** 2

        # Asymptotic curve mapping to 25 points
        s_solves = 25.0 * (1.0 - math.exp(-quality_sum / self.K_CF_SOLVES))

        # Part 2: Peak Rating Component
        s_rating = 10.0 * min(1.0, peak_rating / self.CF_MAX_RATING)

        return round(s_solves + s_rating, 2)

    def calculate_leetcode_score(self, easy_count: int, medium_count: int, hard_count: int) -> float:
        """
        LeetCode: Max 25 Points.
        - Uses strict internal weighting (Easy=1, Medium=3, Hard=6) to favor algorithmic depth over count grinding.
        """
        weighted_score = (easy_count * 1) + (medium_count * 3) + (hard_count * 6)
        
        # Asymptotic curve mapping to 25 points
        s_lc = 25.0 * (1.0 - math.exp(-weighted_score / self.K_LC_WEIGHTS))
        return round(s_lc, 2)

    def calculate_atcoder_score(self, total_solved: int) -> float:
        """
        AtCoder: Max 20 Points.
        - Pure solve count mapping due to uniform high-quality problem standards.
        """
        s_ac = 20.0 * (1.0 - math.exp(-total_solved / self.K_AC_SOLVES))
        return round(s_ac, 2)

    def calculate_codechef_score(self, total_solved: int, peak_rating: int) -> float:
        """
        CodeChef: Max 12 Points.
        - Solves (Max 9) takes precedence.
        - Peak Rating (Max 3) acts as a low-weight metric modifier.
        """
        s_solves = 9.0 * (1.0 - math.exp(-total_solved / self.K_CC_SOLVES))
        s_rating = 3.0 * min(1.0, peak_rating / self.CC_MAX_RATING)
        
        return round(s_solves + s_rating, 2)

    def calculate_beecrowd_score(self, total_solved: int) -> float:
        """
        Beecrowd: Max 8 Points.
        - Pure solve count baseline tracking.
        """
        s_bc = 8.0 * (1.0 - math.exp(-total_solved / self.K_BC_SOLVES))
        return round(s_bc, 2)

    def compute_unified_score(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregates individual platform calculations into a single absolute profile score out of 100.
        """
        # Fetch configurations safely with sensible defaults if student missing platform data
        cf_data = student_data.get("codeforces", {"solves": [], "peak_rating": 0})
        lc_data = student_data.get("leetcode", {"easy": 0, "medium": 0, "hard": 0})
        ac_data = student_data.get("atcoder", {"total_solved": 0})
        cc_data = student_data.get("codechef", {"total_solved": 0, "peak_rating": 0})
        bc_data = student_data.get("beecrowd", {"total_solved": 0})

        # Calculate isolated metric components
        cf_score = self.calculate_codeforces_score(cf_data["solves"], cf_data["peak_rating"])
        lc_score = self.calculate_leetcode_score(lc_data["easy"], lc_data["medium"], lc_data["hard"])
        ac_score = self.calculate_atcoder_score(ac_data["total_solved"])
        cc_score = self.calculate_codechef_score(cc_data["total_solved"], cc_data["peak_rating"])
        bc_score = self.calculate_beecrowd_score(bc_data["total_solved"])

        # Final absolute sum aggregation
        total_score = round(cf_score + lc_score + ac_score + cc_score + bc_score, 2)

        return {
            "total_unified_score": min(100.0, total_score), # Guard rail absolute maximum
            "breakdown": {
                "codeforces": cf_score,
                "leetcode": lc_score,
                "atcoder": ac_score,
                "codechef": cc_score,
                "beecrowd": bc_score
            }
        }

# =====================================================================
# Verification Block & Test Scenario Simulation
# =====================================================================
if __name__ == "__main__":
    engine = UnifiedRankingEngine()

    # Scenario: High-performing student profile
    student_metrics = {
        "codeforces": {
            # 15 problems solved with varying ratings
            "solves": [1200, 1300, 1400, 1500, 1600, 1000, 1100, 900, 800, 1400, 1500, 1600, 1700, 1800, 1900],
            "peak_rating": 1550
        },
        "leetcode": {
            "easy": 45,
            "medium": 80,
            "hard": 15
        },
        "atcoder": {
            "total_solved": 35
        },
        "codechef": {
            "total_solved": 110,
            "peak_rating": 1650
        },
        "beecrowd": {
            "total_solved": 85
        }
    }

    result = engine.compute_unified_score(student_metrics)
    
    print("--- MBSTU Unified Developer Ranking Analysis ---")
    print(f"Final Aggregated Score: {result['total_unified_score']} / 100.00")
    print("\nPlatform Allocation Breakdown:")
    for platform, score in result["breakdown"].items():
        print(f" - {platform.capitalize()}: {score}")