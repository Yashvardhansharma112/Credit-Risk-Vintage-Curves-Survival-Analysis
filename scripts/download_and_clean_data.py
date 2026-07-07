"""
download_and_clean_data.py
--------------------------
Downloads and preprocesses the Lending Club (2007-2018) loan dataset.

Data Source: https://www.kaggle.com/datasets/wordsforthewise/lending-club
Place 'accepted_2007_to_2018Q4.csv.gz' in the data/ directory before running.

Usage:
    python scripts/download_and_clean_data.py
"""

import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
RAW_FILE = os.path.join(DATA_DIR, 'accepted_2007_to_2018Q4.csv.gz')
CLEAN_FILE = os.path.join(DATA_DIR, 'clean_loans.csv')


def load_and_clean():
    """Load raw Lending Club data and engineer features for credit risk analysis."""

    print(f"Loading raw data from: {RAW_FILE}")
    df = pd.read_csv(RAW_FILE, low_memory=False)
    print(f"  Raw dataset: {len(df):,} loans")

    # ── Select relevant columns ──────────────────────────────────────────
    cols = [
        'id', 'issue_d', 'loan_status', 'loan_amnt', 'funded_amnt',
        'term', 'int_rate', 'grade', 'sub_grade', 'emp_length',
        'home_ownership', 'annual_inc', 'purpose', 'addr_state',
        'dti', 'delinq_2yrs', 'fico_range_low', 'fico_range_high',
        'total_pymnt', 'recoveries', 'last_pymnt_d',
        'chargeoff_within_12_mths'
    ]
    df = df[[c for c in cols if c in df.columns]].copy()

    # ── Parse dates ──────────────────────────────────────────────────────
    df['issue_date'] = pd.to_datetime(df['issue_d'], format='%b-%Y', errors='coerce')
    df['last_pymnt_date'] = pd.to_datetime(df['last_pymnt_d'], format='%b-%Y', errors='coerce')
    df['issue_month'] = df['issue_date'].dt.to_period('M').astype(str)
    df['issue_quarter'] = df['issue_date'].dt.to_period('Q').astype(str)
    df['issue_year'] = df['issue_date'].dt.year

    # ── Default flag ─────────────────────────────────────────────────────
    default_statuses = ['Charged Off', 'Default', 'Late (31-120 days)']
    df['is_default'] = df['loan_status'].isin(default_statuses).astype(int)

    # ── Clean interest rate ──────────────────────────────────────────────
    if df['int_rate'].dtype == object:
        df['int_rate'] = df['int_rate'].str.replace('%', '', regex=False).astype(float)

    # ── FICO score engineering ───────────────────────────────────────────
    df['fico_score'] = (df['fico_range_low'] + df['fico_range_high']) / 2
    df['fico_bucket'] = pd.cut(
        df['fico_score'],
        bins=[0, 660, 700, 740, 780, 850],
        labels=['<660', '660-700', '700-740', '740-780', '780+']
    )

    # ── Months on Book (MOB) ─────────────────────────────────────────────
    df['mob'] = (
        (df['last_pymnt_date'] - df['issue_date']).dt.days / 30
    ).fillna(0).astype(int)

    # ── Loss amount ──────────────────────────────────────────────────────
    df['loss_amount'] = np.where(
        df['is_default'] == 1,
        df['funded_amnt'] - df['total_pymnt'] - df['recoveries'].fillna(0),
        0
    )

    # ── Drop rows with no issue date ─────────────────────────────────────
    df = df.dropna(subset=['issue_date'])

    # ── Save ─────────────────────────────────────────────────────────────
    df.to_csv(CLEAN_FILE, index=False)
    print(f"\n✅ Cleaned dataset saved to: {CLEAN_FILE}")
    print(f"   Rows: {len(df):,}")
    print(f"   Default rate: {df['is_default'].mean():.2%}")
    print(f"   Date range: {df['issue_date'].min().date()} → {df['issue_date'].max().date()}")
    print(f"   Grades: {sorted(df['grade'].dropna().unique())}")

    return df


if __name__ == '__main__':
    load_and_clean()
