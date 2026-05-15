"""
portfolio_analyzer.py
=====================
Core credit risk and portfolio analysis engine.
Author: Sachin Jadhav | 19 Yrs BFSI | Credit Risk & Portfolio Management
Contact: jadhav.sachin6290@gmail.com
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ─── COLOUR PALETTE ──────────────────────────────────────────────────────────
NAVY   = '#1F4E79'
BLUE   = '#2E75B6'
TEAL   = '#0F6E56'
AMBER  = '#E6A817'
RED    = '#C0392B'
GREEN  = '#27AE60'
GRAY   = '#7F8C8D'

# ─── DATA GENERATOR ──────────────────────────────────────────────────────────
def generate_sample_portfolio(n_accounts=500, seed=42):
    """
    Generate a realistic synthetic SME loan portfolio.
    Mirrors structure of an actual regional banking portfolio.
    """
    np.random.seed(seed)
    
    segments = ['SME Manufacturing', 'Agri Processing', 'Retail Trade', 
                'Service Sector', 'Construction', 'Healthcare']
    seg_weights = [0.35, 0.20, 0.20, 0.12, 0.08, 0.05]
    
    data = {
        'account_id': [f'A{str(i).zfill(4)}' for i in range(1, n_accounts+1)],
        'segment': np.random.choice(segments, n_accounts, p=seg_weights),
        'sanction_amount': np.random.lognormal(mean=8.5, sigma=0.8, size=n_accounts),
        'outstanding_balance': None,
        'dpd': np.random.choice(
            [0, 15, 45, 75, 120], n_accounts,
            p=[0.64, 0.18, 0.11, 0.04, 0.03]
        ),
        'emi_bounces_3m': np.random.choice([0,1,2,3], n_accounts, p=[0.75,0.15,0.07,0.03]),
        'monthly_turnover_drop_pct': np.random.normal(0, 15, n_accounts),
        'cheque_dishonour': np.random.choice([0,1], n_accounts, p=[0.92,0.08]),
        'leverage_ratio': np.random.lognormal(mean=0.8, sigma=0.4, size=n_accounts),
        'months_on_book': np.random.randint(3, 84, n_accounts),
    }
    
    df = pd.DataFrame(data)
    df['sanction_amount'] = df['sanction_amount'].clip(25, 3000)  # ₹25L to ₹3000L
    df['outstanding_balance'] = df['sanction_amount'] * np.random.uniform(0.3, 1.0, n_accounts)
    df['is_npa'] = df['dpd'] >= 90
    
    return df

# ─── DELINQUENCY BUCKET ANALYSIS ─────────────────────────────────────────────
def delinquency_bucket_analysis(df):
    """
    Classify portfolio into standard DPD buckets.
    Standard banking framework: 0-30 / 31-60 / 61-90 / 90+ DPD.
    """
    bins   = [-1, 30, 60, 90, float('inf')]
    labels = ['0–30 DPD', '31–60 DPD', '61–90 DPD', '90+ DPD (NPA)']
    
    df = df.copy()
    df['dpd_bucket'] = pd.cut(df['dpd'], bins=bins, labels=labels)
    
    bucket_summary = df.groupby('dpd_bucket', observed=True).agg(
        accounts    = ('account_id', 'count'),
        outstanding = ('outstanding_balance', 'sum'),
    ).reset_index()
    
    total_os = bucket_summary['outstanding'].sum()
    bucket_summary['pct_portfolio'] = (bucket_summary['outstanding'] / total_os * 100).round(1)
    bucket_summary['outstanding_cr'] = (bucket_summary['outstanding'] / 100).round(2)
    
    return bucket_summary

# ─── NPA TREND ANALYSIS ──────────────────────────────────────────────────────
def npa_trend_analysis(months=12):
    """
    Simulate NPA trend over 12 months — mirrors real portfolio monitoring.
    """
    np.random.seed(99)
    base_npa = 3.2
    trend = np.cumsum(np.random.normal(-0.08, 0.15, months))
    npa_rates = np.clip(base_npa + trend, 1.5, 5.5).round(2)
    
    month_labels = pd.date_range(end=datetime.today(), periods=months, freq='ME')
    month_labels = [m.strftime('%b %y') for m in month_labels]
    
    return pd.DataFrame({'month': month_labels, 'npa_pct': npa_rates})

# ─── EARLY WARNING INDICATOR SCORING ─────────────────────────────────────────
def ewi_scorer(df):
    """
    Rule-based Early Warning Indicator system.
    8 triggers — each adds to a risk score. Score >= 3 = flag for review.
    
    Based on standard EWI frameworks used in Indian commercial banking.
    """
    df = df.copy()
    df['ewi_score'] = 0
    
    # Trigger 1: Multiple EMI bounces
    df.loc[df['emi_bounces_3m'] >= 2, 'ewi_score'] += 2
    df.loc[df['emi_bounces_3m'] == 1, 'ewi_score'] += 1
    
    # Trigger 2: Cheque dishonour
    df.loc[df['cheque_dishonour'] == 1, 'ewi_score'] += 2
    
    # Trigger 3: Declining monthly turnover
    df.loc[df['monthly_turnover_drop_pct'] < -15, 'ewi_score'] += 2
    df.loc[df['monthly_turnover_drop_pct'].between(-15, -5), 'ewi_score'] += 1
    
    # Trigger 4: High leverage
    df.loc[df['leverage_ratio'] > 3.5, 'ewi_score'] += 2
    df.loc[df['leverage_ratio'].between(2.5, 3.5), 'ewi_score'] += 1
    
    # Trigger 5: DPD creep (not yet NPA but slipping)
    df.loc[df['dpd'].between(31, 89), 'ewi_score'] += 1
    
    # Flag accounts
    df['ewi_flag'] = df['ewi_score'] >= 3
    df['ewi_risk_level'] = pd.cut(
        df['ewi_score'],
        bins=[-1, 2, 4, 6, float('inf')],
        labels=['Normal', 'Watch', 'Special Mention', 'Immediate Action']
    )
    
    return df

# ─── PORTFOLIO CONCENTRATION ANALYSIS ────────────────────────────────────────
def concentration_analysis(df, threshold_pct=30):
    """
    Flag segments with portfolio concentration above policy threshold.
    Concentration risk is a key regulatory and credit risk concern.
    """
    seg_summary = df.groupby('segment').agg(
        outstanding=('outstanding_balance', 'sum'),
        accounts=('account_id', 'count'),
        npa_accounts=('is_npa', 'sum')
    ).reset_index()
    
    total = seg_summary['outstanding'].sum()
    seg_summary['pct'] = (seg_summary['outstanding'] / total * 100).round(1)
    seg_summary['npa_rate'] = (seg_summary['npa_accounts'] / seg_summary['accounts'] * 100).round(1)
    seg_summary['concentration_flag'] = seg_summary['pct'] > threshold_pct
    
    return seg_summary.sort_values('pct', ascending=False)

# ─── EXECUTIVE SUMMARY REPORT ────────────────────────────────────────────────
def generate_executive_summary(df):
    """
    Generate the portfolio executive summary — the format used for
    C-suite and leadership presentations in regional bank reviews.
    """
    total_portfolio   = df['outstanding_balance'].sum() / 100  # ₹ Crore
    total_accounts    = len(df)
    npa_accounts      = df['is_npa'].sum()
    npa_amount        = df[df['is_npa']]['outstanding_balance'].sum() / 100
    npa_ratio         = (npa_amount / total_portfolio * 100)
    ewi_flagged       = df['ewi_flag'].sum() if 'ewi_flag' in df.columns else 0
    
    print("=" * 52)
    print("  PORTFOLIO HEALTH CHECK — EXECUTIVE SUMMARY")
    print("=" * 52)
    print(f"  Report Date       : {datetime.today().strftime('%d %b %Y')}")
    print(f"  Total Portfolio   : ₹{total_portfolio:.1f} Crore")
    print(f"  Active Accounts   : {total_accounts:,}")
    print(f"  NPA Accounts      : {npa_accounts} ({npa_accounts/total_accounts*100:.1f}%)")
    print(f"  NPA Amount        : ₹{npa_amount:.2f} Crore")
    print(f"  NPA Ratio         : {npa_ratio:.2f}%")
    print(f"  EWI Flagged       : {ewi_flagged} accounts")
    print("=" * 52)
    
    buckets = delinquency_bucket_analysis(df)
    print("\n  DELINQUENCY BUCKETS")
    print("  " + "-" * 48)
    colors_map = {'0–30 DPD': '✓', '31–60 DPD': '⚠', '61–90 DPD': '⚠', '90+ DPD (NPA)': '✗'}
    for _, row in buckets.iterrows():
        icon = colors_map.get(str(row['dpd_bucket']), ' ')
        print(f"  {icon}  {str(row['dpd_bucket']):<16} ₹{row['outstanding_cr']:>7.1f} Cr  ({row['pct_portfolio']:>5.1f}%)")
    
    conc = concentration_analysis(df)
    print("\n  TOP CONCENTRATION FLAGS")
    print("  " + "-" * 48)
    for _, row in conc.head(3).iterrows():
        flag = '⚠ HIGH' if row['concentration_flag'] else '✓ OK  '
        print(f"  {flag}  {row['segment']:<22} {row['pct']:>5.1f}%  NPA: {row['npa_rate']:.1f}%")
    print("=" * 52)

# ─── VISUALISATION ───────────────────────────────────────────────────────────
def plot_portfolio_dashboard(df):
    """
    Generate a 4-panel portfolio analytics dashboard.
    Mirrors the Power BI dashboards built for leadership reviews.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle('SME Loan Portfolio Analytics Dashboard', 
                 fontsize=16, fontweight='bold', color=NAVY, y=0.98)
    fig.patch.set_facecolor('white')

    # Panel 1: NPA Trend
    ax1 = axes[0, 0]
    npa_data = npa_trend_analysis()
    ax1.plot(npa_data['month'], npa_data['npa_pct'], 
             color=AMBER, linewidth=2.5, marker='o', markersize=5)
    ax1.fill_between(range(len(npa_data)), npa_data['npa_pct'], 
                     alpha=0.15, color=AMBER)
    ax1.set_title('NPA Trend (12-Month)', fontweight='bold', color=NAVY, pad=10)
    ax1.set_ylabel('NPA %', color=GRAY)
    ax1.set_xticks(range(len(npa_data)))
    ax1.set_xticklabels(npa_data['month'], rotation=45, fontsize=8)
    ax1.axhline(y=3.0, color=RED, linestyle='--', alpha=0.5, linewidth=1)
    ax1.text(11, 3.05, 'Threshold 3%', color=RED, fontsize=8)
    ax1.spines[['top','right']].set_visible(False)

    # Panel 2: Delinquency Buckets
    ax2 = axes[0, 1]
    buckets = delinquency_bucket_analysis(df)
    bar_colors = [GREEN, AMBER, '#E67E22', RED]
    bars = ax2.bar(buckets['dpd_bucket'].astype(str), 
                   buckets['outstanding_cr'],
                   color=bar_colors, edgecolor='white', linewidth=0.5)
    ax2.set_title('Delinquency Bucket Analysis (₹ Crore)', fontweight='bold', color=NAVY, pad=10)
    ax2.set_ylabel('Outstanding (₹ Cr)', color=GRAY)
    for bar, pct in zip(bars, buckets['pct_portfolio']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{pct}%', ha='center', va='bottom', fontsize=9, color=NAVY, fontweight='bold')
    ax2.spines[['top','right']].set_visible(False)
    ax2.tick_params(axis='x', labelsize=8)

    # Panel 3: Segment Concentration
    ax3 = axes[1, 0]
    conc = concentration_analysis(df)
    seg_colors = [RED if f else BLUE for f in conc['concentration_flag']]
    bars3 = ax3.barh(conc['segment'], conc['pct'], color=seg_colors, 
                     edgecolor='white', linewidth=0.5)
    ax3.axvline(x=30, color=RED, linestyle='--', alpha=0.7, linewidth=1.5)
    ax3.text(30.5, -0.5, 'Policy limit\n30%', color=RED, fontsize=8)
    ax3.set_title('Portfolio Concentration by Segment (%)', fontweight='bold', color=NAVY, pad=10)
    ax3.set_xlabel('% of Portfolio', color=GRAY)
    ax3.spines[['top','right']].set_visible(False)
    red_p = mpatches.Patch(color=RED, label='Above policy limit')
    blue_p = mpatches.Patch(color=BLUE, label='Within policy')
    ax3.legend(handles=[red_p, blue_p], fontsize=8, loc='lower right')

    # Panel 4: EWI Risk Distribution
    ax4 = axes[1, 1]
    df_ewi = ewi_scorer(df)
    ewi_dist = df_ewi['ewi_risk_level'].value_counts()
    ewi_colors = {'Normal': GREEN, 'Watch': AMBER, 
                  'Special Mention': '#E67E22', 'Immediate Action': RED}
    ewi_c = [ewi_colors.get(str(k), GRAY) for k in ewi_dist.index]
    wedges, texts, autotexts = ax4.pie(
        ewi_dist.values, labels=ewi_dist.index, 
        colors=ewi_c, autopct='%1.0f%%',
        startangle=90, pctdistance=0.8,
        wedgeprops=dict(edgecolor='white', linewidth=1.5)
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight('bold')
    ax4.set_title('EWI Risk Distribution', fontweight='bold', color=NAVY, pad=10)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('outputs/portfolio_dashboard.png', dpi=150, bbox_inches='tight',
                facecolor='white')
    plt.show()
    print("Dashboard saved to outputs/portfolio_dashboard.png")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating synthetic SME loan portfolio...")
    df = generate_sample_portfolio(n_accounts=500)
    
    print("Scoring Early Warning Indicators...")
    df = ewi_scorer(df)
    
    print("\nGenerating Executive Summary...\n")
    generate_executive_summary(df)
    
    print("\nGenerating Portfolio Dashboard...")
    plot_portfolio_dashboard(df)
