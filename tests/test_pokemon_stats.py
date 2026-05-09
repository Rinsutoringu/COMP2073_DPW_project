import unittest
import pandas as pd


_SAMPLE_ROWS = [
    ["Bulbasaur", "Grass", 49, 49, 45, 45, 65, 65, False],
    ["Ivysaur", "Grass", 62, 63, 60, 60, 80, 80, False],
    ["Charmander", "Fire", 52, 43, 65, 39, 60, 50, False],
    ["Squirtle", "Water", 48, 65, 43, 44, 50, 64, False],
    ["Pikachu", "Electric", 55, 40, 90, 35, 50, 40, False],
    ["Raichu", "Electric", 90, 55, 110, 60, 90, 80, False],
    ["Mewtwo", "Psychic", 110, 90, 130, 106, 154, 90, True],
    ["Articuno", "Ice", 85, 100, 85, 90, 95, 125, True],
]

_COLUMNS = ["name", "type1", "attack", "defense", "speed", "hp", "sp_attack", "sp_defense", "is_legendary"]


def _make_df():
    return pd.DataFrame(_SAMPLE_ROWS, columns=_COLUMNS)


class MostCommonType1Test(unittest.TestCase):

    def test_returns_tied_winner(self):
        from src.data_analysis.pokemon_stats import most_common_type1

        df = _make_df()
        top_type, top_count = most_common_type1(df)
        self.assertIn(top_type, ("Grass", "Electric"))
        self.assertEqual(top_count, 2)

    def test_returns_single_winner_when_no_tie(self):
        from src.data_analysis.pokemon_stats import most_common_type1

        df = _make_df().iloc[:-1]
        df = df[df["name"] != "Raichu"]
        top_type, top_count = most_common_type1(df)
        self.assertEqual(top_type, "Grass")
        self.assertEqual(top_count, 2)


class Type1HighestAvgAttackTest(unittest.TestCase):

    def test_psychic_has_highest_avg_attack(self):
        from src.data_analysis.pokemon_stats import highest_avg_attack_type1

        df = _make_df()
        type_name, avg_val = highest_avg_attack_type1(df)

        self.assertEqual(type_name, "Psychic")
        self.assertAlmostEqual(avg_val, 110.0, places=1)

    def test_fire_alone_returns_its_own_average(self):
        from src.data_analysis.pokemon_stats import highest_avg_attack_type1

        df = _make_df()
        df_fire = df[df["type1"] == "Fire"]
        type_name, avg_val = highest_avg_attack_type1(df_fire)

        self.assertEqual(type_name, "Fire")
        self.assertAlmostEqual(avg_val, 52.0, places=1)

    def test_grass_avg_is_correct(self):
        from src.data_analysis.pokemon_stats import highest_avg_attack_type1

        df = _make_df()
        df_grass = df[df["type1"] == "Grass"]
        type_name, avg_val = highest_avg_attack_type1(df_grass)

        self.assertEqual(type_name, "Grass")
        self.assertAlmostEqual(avg_val, 55.5, places=1)


class AttackSpeedCorrelationTest(unittest.TestCase):

    def test_correlation_is_positive(self):
        from src.data_analysis.pokemon_stats import attack_speed_correlation

        df = _make_df()
        corr = attack_speed_correlation(df)
        self.assertGreater(corr, 0.0)

    def test_correlation_in_expected_range(self):
        from src.data_analysis.pokemon_stats import attack_speed_correlation

        df = _make_df()
        corr = attack_speed_correlation(df)
        self.assertTrue(0.5 < corr <= 1.0,
                        f"Expected correlation in (0.5, 1.0], got {corr:.4f}")

    def test_correlation_is_nan_for_single_row(self):
        from src.data_analysis.pokemon_stats import attack_speed_correlation

        corr = attack_speed_correlation(_make_df().iloc[:1])
        self.assertTrue(pd.isna(corr))

    def test_perfect_positive_linear_returns_one(self):
        from src.data_analysis.pokemon_stats import attack_speed_correlation

        df = pd.DataFrame({"attack": [10, 20, 30], "speed": [10, 20, 30]})
        corr = attack_speed_correlation(df)
        self.assertAlmostEqual(corr, 1.0, places=6)


class LegendaryVsNormalTest(unittest.TestCase):

    def test_legendary_attack_higher(self):
        from src.data_analysis.pokemon_stats import legendary_vs_nonlegendary

        df = _make_df()
        result = legendary_vs_nonlegendary(df)

        row = result[result["stat"] == "attack"].iloc[0]
        self.assertGreater(row["diff"], 0.0)

    def test_average_differences_match_expected(self):
        from src.data_analysis.pokemon_stats import legendary_vs_nonlegendary

        df = _make_df()
        result = legendary_vs_nonlegendary(df)

        expected_diffs = {
            "attack": round(97.5 - 356 / 6, 2),
            "defense": round(95.0 - 315 / 6, 2),
            "speed": round(107.5 - 413 / 6, 2),
        }

        for stat, expected in expected_diffs.items():
            row = result[result["stat"] == stat].iloc[0]
            self.assertAlmostEqual(row["diff"], expected, places=4,
                                   msg=f"{stat} diff mismatch")

    def test_handles_no_legendary_gracefully(self):
        from src.data_analysis.pokemon_stats import legendary_vs_nonlegendary

        df = _make_df()[_make_df()["is_legendary"] == False]
        try:
            result = legendary_vs_nonlegendary(df)
            self.assertIsNotNone(result)
        except (ValueError, KeyError) as e:
            pass
        except Exception as e:
            self.assertIn("legendary", str(e).lower(),
                          "Expected a graceful handling, not a general crash")


if __name__ == "__main__":
    unittest.main()
