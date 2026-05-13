"""Pokemon CSV cleaning pipeline.

Usage:
    python src/data_clean/clean.py
    python src/data_clean/clean.py --step 4
    python src/data_clean/clean.py --no-split
"""

import argparse
import ast
import re
from pathlib import Path

import numpy as np
import pandas as pd


ARCHIVE_DIR = Path("archive")
RAW_PATH = ARCHIVE_DIR / "pokemon.csv"
CLEANED_PATH = ARCHIVE_DIR / "pokemon_cleaned.csv"
REPORT_PATH = ARCHIVE_DIR / "cleaning_report.txt"

FIXED_COLUMNS = {"classfication": "classification"}

CRITICAL_COLS = [
    "name", "pokedex_number", "type1", "hp", "attack",
    "defense", "sp_attack", "sp_defense", "speed", "generation",
]

MISSING_OK_COLS = {
    "type2": "single-type Pokemon",
    "percentage_male": "genderless Pokemon",
    "height_m": "missing data",
    "weight_kg": "missing data",
}

INT_COLS = [
    "pokedex_number", "generation", "base_total", "base_egg_steps",
    "base_happiness", "capture_rate", "experience_growth",
    "hp", "attack", "defense", "sp_attack", "sp_defense", "speed",
]
FLOAT_COLS = ["height_m", "weight_kg", "percentage_male"]
BOOL_COLS = ["is_legendary"]
CAT_COLS = ["type1", "type2", "generation", "classification"]

# Validation rules sourced from the official Pokemon dataset spec.
TYPE_MULTIPLIERS = {0.0, 0.25, 0.5, 1.0, 2.0, 4.0}
VALID_EXPERIENCE_GROWTH = {600000, 800000, 1000000, 1059860, 1250000, 1640000}
VALID_EGG_STEPS = {1280, 2560, 3840, 5120, 6400, 7680, 8960, 10240, 20480, 30720}

RANGE_RULES = [
    ("hp",             1,    255),
    ("attack",         1,    255),
    ("defense",        1,    255),
    ("sp_attack",      1,    255),
    ("sp_defense",     1,    255),
    ("speed",          1,    255),
    ("base_total",   175,    780),
    ("base_happiness", 0,    255),
    ("capture_rate",   3,    255),
    ("height_m",       0.1,   20.0),
    ("weight_kg",      0.1, 1000.0),
    ("percentage_male", 0,   100),
]

STAT_COLS = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]


def step1_precheck_and_fix(raw_path):
    print(f"[step 1] precheck: {raw_path}")
    with open(raw_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    expected_cols = lines[0].strip().count(",") + 1

    bad_lines = []
    for i, line in enumerate(lines[1:], start=1):
        in_quotes = False
        comma_count = 0
        for ch in line:
            if ch == '"':
                in_quotes = not in_quotes
            elif ch == ',' and not in_quotes:
                comma_count += 1
        if comma_count + 1 != expected_cols:
            bad_lines.append((i + 1, comma_count + 1))

    print(f"  header columns: {expected_cols}, bad rows: {len(bad_lines)}")
    return raw_path


def _normalize_abilities_quoting(line):
    m = re.match(r'^"(\[.*?\])"', line)
    if m:
        inner = re.sub(r"'\s+", "' ", m.group(1))
        inner = re.sub(r"\s+'", " '", inner)
        return '"' + inner + '"' + line[m.end():]

    if line.startswith("["):
        end = line.index("]") + 1
        inner = re.sub(r"'\s+", "' ", line[:end])
        inner = re.sub(r"\s+'", " '", inner)
        return '"' + inner + '"' + line[end:]

    return line


def step2_load_and_clean(csv_path):
    print(f"[step 2] load + dedupe: {csv_path}")
    df = pd.read_csv(csv_path, encoding="utf-8")
    df = df.rename(columns=FIXED_COLUMNS)

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

    dups = df.duplicated().sum()
    if dups:
        df = df.drop_duplicates()
        print(f"  dropped {dups} duplicates")

    print(f"  shape: {df.shape}")
    return df


def step3_audit_missing(df):
    print("[step 3] missing value audit")
    for col, reason in MISSING_OK_COLS.items():
        if col in df.columns:
            count = df[col].isna().sum()
            if count:
                print(f"  {col}: {count} NaN ({reason})")

    for col in CRITICAL_COLS:
        if col in df.columns:
            count = df[col].isna().sum()
            if count:
                print(f"  WARNING: {col} has {count} NaN")

    print(f"  total NaN: {df.isnull().sum().sum()}")
    return df


def _safe_parse_ability(s):
    if pd.isna(s) or not isinstance(s, str):
        return []
    s = s.strip().strip('"')
    try:
        result = ast.literal_eval(s)
        if isinstance(result, list):
            return [item.strip() for item in result]
    except (ValueError, SyntaxError):
        pass
    return [s]


def step4_parse_abilities(df):
    print("[step 4] parse abilities")
    df["abilities_parsed"] = df["abilities"].apply(_safe_parse_ability)
    df["ability_count"] = df["abilities_parsed"].apply(len)

    merged = df[df["ability_count"] > 4]
    print(f"  mean: {df['ability_count'].mean():.1f}, max: {df['ability_count'].max()}, merged forms: {len(merged)}")
    return df


def step5_split_regional_forms(df, do_split=True):
    if not do_split:
        print("[step 5] split regional variants: skipped")
        return df

    print("[step 5] split regional variants")
    is_merged = df["ability_count"] > 4

    if not is_merged.any():
        print("  nothing to split")
        return df

    df_normal = df[~is_merged].copy()
    df_normal["form_index"] = 0

    new_rows = []
    for _, row in df[is_merged].iterrows():
        abilities = row["abilities_parsed"]
        form_size = max(2, len(abilities) // 2) if len(abilities) >= 4 else len(abilities)
        num_forms = max(2, len(abilities) // form_size)

        for form_idx in range(num_forms):
            new_row = row.copy()
            start = form_idx * form_size
            end = start + form_size if form_idx < num_forms - 1 else len(abilities)
            new_row["abilities_parsed"] = abilities[start:end]
            new_row["ability_count"] = len(abilities[start:end])
            new_row["abilities"] = str(abilities[start:end])
            new_row["form_index"] = form_idx
            new_rows.append(new_row)

    df_split = pd.concat([df_normal, pd.DataFrame(new_rows)], ignore_index=True)
    print(f"  {len(df)} -> {len(df_split)} rows ({is_merged.sum()} split)")
    return df_split


def step6_normalize_types(df):
    print("[step 6] normalize dtypes")

    for col in INT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    for col in FLOAT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(bool)

    for col in CAT_COLS:
        if col in df.columns:
            df[col] = df[col].astype("category")

    mem_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
    print(f"  memory: {mem_mb:.2f} MB")
    return df


def _flag(df, mask, reason):
    df.loc[mask, "is_suspicious"] = True
    df.loc[mask, "suspicious_reason"] += reason + "; "


def step7_detect_outliers(df):
    print("[step 7] outlier detection")
    df["is_suspicious"] = False
    df["suspicious_reason"] = ""
    issues = 0

    against_cols = [c for c in df.columns if c.startswith("against_")]
    for col in against_cols:
        series = df[col].dropna()
        valid_mask = series.apply(
            lambda v: any(np.isclose(v, mv, atol=0.001) for mv in TYPE_MULTIPLIERS)
        )
        bad_values = series[~valid_mask]
        if len(bad_values):
            print(f"  {col}: invalid multipliers {sorted(bad_values.unique())}")
            _flag(df, df[col].notna() & ~df[col].isin(TYPE_MULTIPLIERS),
                  f"{col} not in {TYPE_MULTIPLIERS}")
            issues += 1

    for col, lo, hi in RANGE_RULES:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        bad = (series < lo) | (series > hi)
        if bad.any():
            print(f"  {col} outside [{lo}, {hi}]: {bad.sum()} rows")
            mask = df[col].notna() & ((df[col] < lo) | (df[col] > hi))
            _flag(df, mask, f"{col} outside [{lo}, {hi}]")
            issues += 1

    if "experience_growth" in df.columns:
        series = df["experience_growth"].dropna()
        bad = ~series.isin(VALID_EXPERIENCE_GROWTH)
        if bad.any():
            print(f"  experience_growth invalid: {sorted(series[bad].unique())}")
            _flag(df, df["experience_growth"].notna() & ~df["experience_growth"].isin(VALID_EXPERIENCE_GROWTH),
                  "invalid experience_growth")
            issues += 1

    if "base_egg_steps" in df.columns:
        series = df["base_egg_steps"].dropna()
        bad = ~series.isin(VALID_EGG_STEPS)
        if bad.any():
            print(f"  base_egg_steps invalid: {sorted(series[bad].unique())}")
            _flag(df, df["base_egg_steps"].notna() & ~df["base_egg_steps"].isin(VALID_EGG_STEPS),
                  "invalid base_egg_steps")
            issues += 1

    if all(c in df.columns for c in STAT_COLS + ["base_total"]):
        mismatch = abs(df["base_total"] - df[STAT_COLS].sum(axis=1)) > 5
        if mismatch.any():
            print(f"  base_total mismatch: {mismatch.sum()} rows")
            _flag(df, mismatch, "base_total mismatch with stat sum")
            issues += 1

    if "weight_kg" in df.columns and "height_m" in df.columns:
        ratio = df["weight_kg"] / df["height_m"].replace(0, np.nan)
        extreme = ratio > 500
        if extreme.any():
            print(f"  extreme weight/height ratio: {df.loc[extreme, 'name'].tolist()}")
            _flag(df, extreme, "extreme weight/height ratio")
            issues += 1

    flagged = df["is_suspicious"].sum()
    print(f"  issues: {issues}, flagged: {flagged}/{len(df)}")
    return df


def step8_export(df, output_path, report_path):
    print(f"[step 8] export -> {output_path}")
    df_out = df.copy()
    df_out["abilities"] = df_out["abilities_parsed"].apply(str)
    df_out.to_csv(output_path, index=False, encoding="utf-8")

    _write_report(df_out, report_path)
    print(f"  report -> {report_path}")


def _write_report(df, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("Pokemon Data Cleaning Report\n\n")
        f.write(f"input:  {RAW_PATH}\n")
        f.write(f"output: {CLEANED_PATH}\n")
        f.write(f"shape:  {df.shape}\n")
        f.write(f"cols:   {len(df.columns)}\n\n")

        f.write("columns:\n")
        for i, col in enumerate(df.columns, 1):
            f.write(f"  {i:2d}. {col}\n")

        f.write("\nnull counts:\n")
        for col, cnt in df.isnull().sum().items():
            if cnt:
                f.write(f"  {col}: {cnt}\n")

        f.write("\ndtypes:\n")
        for col, dtype in df.dtypes.items():
            f.write(f"  {col}: {dtype}\n")

        suspicious = df[df.get("is_suspicious", False)]
        if len(suspicious):
            f.write(f"\nflagged rows: {len(suspicious)}\n")
            for _, row in suspicious.iterrows():
                f.write(f"  {row['name']} (#{row['pokedex_number']}): {row['suspicious_reason']}\n")


PIPELINE = [
    ("precheck",          step1_precheck_and_fix),
    ("load",              step2_load_and_clean),
    ("audit_missing",     step3_audit_missing),
    ("parse_abilities",   step4_parse_abilities),
    ("split_forms",       step5_split_regional_forms),
    ("normalize_types",   step6_normalize_types),
    ("detect_outliers",   step7_detect_outliers),
    ("export",            step8_export),
]


def run_pipeline(do_split=True, start_step=1, raw_path=None):
    if raw_path is None:
        raw_path = RAW_PATH

    path = raw_path
    df = None

    for i, (name, fn) in enumerate(PIPELINE, start=1):
        if i < start_step:
            continue

        if name == "split_forms":
            df = fn(df, do_split)
        elif name == "export":
            fn(df, CLEANED_PATH, REPORT_PATH)
        elif name == "precheck":
            path = fn(path)
        elif name == "load":
            df = fn(path)
        else:
            df = fn(df)

    print("done.")
    return df


def _parse_args():
    parser = argparse.ArgumentParser(description="Pokemon CSV cleaning pipeline")
    parser.add_argument("--step", type=int, default=1, help="start from step N (1-8)")
    parser.add_argument("--no-split", action="store_true", help="skip regional form splitting")
    parser.add_argument("--raw", type=Path, default=None, help="override raw CSV path")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_pipeline(do_split=not args.no_split, start_step=args.step, raw_path=args.raw)
