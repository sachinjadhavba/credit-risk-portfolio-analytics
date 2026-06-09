# Credit Risk & Portfolio Analytics
### SME Loan Portfolio — NPA Trend Analysis · Delinquency Bucketing · Early Warning Indicators

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-Latest-150458?style=flat&logo=pandas)](https://pandas.pydata.org)
[![Domain](https://img.shields.io/badge/Domain-Credit_Risk-1F4E79?style=flat)](https://finsight-one-4cao.vercel.app/)
[![Author](https://img.shields.io/badge/Author-Sachin_Jadhav-2E75B6?style=flat)](https://www.linkedin.com/in/sachin-jadhav-consulting)

---

## Overview

This repository demonstrates end-to-end credit risk analytics on a **simulated SME loan portfolio** — built from 19 years of hands-on banking experience managing ₹500+ Crore portfolios across multiple credit cycles.

The analysis covers the full portfolio health workflow used by senior banking professionals:
- NPA trend analysis across 12-month rolling window
- Delinquency bucket classification (0–30 / 31–60 / 61–90 / 90+ DPD)
- Portfolio concentration risk flags
- Early warning indicator (EWI) scoring
- Customer risk segmentation

> **Note:** All data is synthetically generated. No real customer or bank data is used.

---

## Repository Structure

```
credit-risk-portfolio-analytics/
│
├── data/
│   └── generate_portfolio_data.py     # Synthetic loan portfolio generator
│
├── notebooks/
│   ├── 01_npa_trend_analysis.ipynb    # NPA trend + YoY/QoQ analysis
│   ├── 02_delinquency_buckets.ipynb   # DPD bucketing + flow rate analysis
│   ├── 03_early_warning_indicators.ipynb  # EWI scoring model
│   └── 04_risk_segmentation.ipynb     # Customer risk segmentation
│
├── src/
│   ├── portfolio_analyzer.py          # Core analysis engine
│   ├── ewi_scorer.py                  # Early warning indicator logic
│   └── report_generator.py           # Executive summary generator
│
├── outputs/
│   └── sample_portfolio_report.pdf   # Sample output report
│
├── requirements.txt
└── README.md
```

---

## Key Analysis Modules

### 1. NPA Trend Analysis
Tracks Non-Performing Assets over time with YoY and QoQ variance — the core metric every credit risk manager monitors daily.

### 2. Delinquency Bucket Analysis
Classifies loan accounts into standard DPD buckets and calculates roll-forward rates — predicts future NPA build-up before it happens.

### 3. Early Warning Indicators
Rule-based EWI system that flags accounts at risk using 8 behavioural and financial triggers — the same approach used in real bank portfolio monitoring.

### 4. Risk Segmentation
Segments the portfolio by risk profile, ticket size, and segment to support targeted interventions.

---

## Sample Output

```
PORTFOLIO HEALTH CHECK — SUMMARY REPORT
========================================
Total Portfolio:     ₹487.3 Crore
Active Accounts:     1,847
NPA Ratio:           2.84%  (prev: 3.12%)  ▼ Improving
Gross NPA:          ₹13.84 Crore

DELINQUENCY BUCKETS
-------------------
0–30 DPD:    ₹312.4 Cr  (64.1%)  ✓ Normal
31–60 DPD:   ₹89.2 Cr   (18.3%)  ⚠ Monitor
61–90 DPD:   ₹52.1 Cr   (10.7%)  ⚠ Action
90+ DPD:     ₹33.6 Cr   (6.9%)   ✗ NPA

EARLY WARNING FLAGS (3 accounts triggered)
------------------------------------------
Account A1847:  3 consecutive EMI bounces + declining turnover
Account A0923:  Cheque dishonour + account dormancy > 45 days
Account A1234:  Industry stress flag + leverage ratio > 3.5x

TOP RISK CONCENTRATION
----------------------
SME Manufacturing:  38.4%  ⚠ Concentration risk
Agri Processing:    22.1%  ✓ Within policy
Retail Trade:       19.8%  ✓ Within policy
```

---

## Installation

```bash
git clone https://github.com/sachinjadhavba/credit-risk-portfolio-analytics.git
cd credit-risk-portfolio-analytics
pip install -r requirements.txt
python data/generate_portfolio_data.py
jupyter notebook notebooks/
```

---

## Requirements

```
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
jupyter>=1.0.0
openpyxl>=3.0.10
```

---

## About the Author

**Sachin Jadhav** — 19 years in BFSI · Credit Risk · Loan Portfolio Management · Banking Analytics

- 🌐 [FinsightOne](https://finsight-one-4cao.vercel.app/)
- 💼 [LinkedIn](https://www.linkedin.com/in/sachin-jadhav-consultant)
- 📧 jadhav.sachin6290@gmail.com
- 📅 [Book a discovery call](https://calendly.com/jadhav-sachin6290)

Attribution
Domain framework: Sachin Jadhav — 19 years SME/MSME credit appraisal and portfolio management, IndusInd Bank, CSB Bank, ING Vysya Bank, Yes Bank, South Indian Bank, Axis Bank.

Code: Developed with AI assistance (Claude by Anthropic). The analytical logic, trigger thresholds, and portfolio concepts are based on real banking experience. The Python implementation was built with AI tools.

This is honest. The framework is mine. The code is assisted.
---

*Built from real-world banking experience. Every analysis technique here has been applied to live portfolios.*
