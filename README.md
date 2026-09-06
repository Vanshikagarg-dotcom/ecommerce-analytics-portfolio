# E-commerce Sales & Customer Retention Analytics

An end-to-end analytics case study for a fictional online retailer, **Northstar Retail**. The project converts raw order-level data into commercial insights on revenue, product performance, customer retention, and churn risk.

## Business question

Where should Northstar Retail focus to grow profitable revenue while improving repeat purchase behavior?

## What this project demonstrates

- Data modelling and cleaning with Python/pandas
- Analytical SQL using joins, CTEs, window functions, and cohort logic
- KPI design: revenue, profit, AOV, repeat-purchase rate, customer lifetime value
- Customer segmentation and churn-risk identification
- Dashboard design for business stakeholders

## Repository structure

```text
data/                 Generated source tables (customers, products, orders)
sql/                  Portfolio-quality SQL analysis
src/generate_data.py  Deterministic synthetic-data generator
src/analyze.py        Python analysis and visual outputs
dashboard/            Power BI build guide and measures
outputs/              Generated charts and summary tables
```

## Quick start

```bash
pip install -r requirements.txt
python src/generate_data.py
python src/analyze.py
```

The data are synthetic and deterministic (`seed=42`), making the work safe to share publicly and reproducible for reviewers.

## Update the data and refresh everything

Yes—replace or edit the CSVs in `data/` while preserving their column names, then run:

```powershell
.\refresh_analysis.ps1
```

This recreates the KPI summary, performance tables, customer list, and SVG charts in `outputs/`. In Power BI, choose **Home → Refresh** after the script finishes; since the report reads the same CSV paths, its visuals and measures update automatically. For a published Power BI Service report, configure scheduled refresh (and an on-premises data gateway if the files remain on your computer).

Important: do **not** run `src/generate_data.py` after replacing the files—it intentionally overwrites them with the synthetic sample. It is only for resetting the demo data.

## Executive findings

The completed analysis produced **$2.10M revenue**, **$1.02M profit**, a **48.7% profit margin**, and a **67% repeat-purchase rate**. Read [the executive summary](EXECUTIVE_SUMMARY.md) for the stakeholder narrative and recommendations.

## Suggested resume bullet

> Built an end-to-end e-commerce analytics case study using SQL, Python, and Power BI; modeled customer and transaction data, quantified revenue, profit, repeat-purchase behavior, and churn risk, and translated findings into stakeholder-ready dashboard recommendations.

## Interview walkthrough

1. Explain the business question and the three-table model.
2. Show how you validated order status, dates, prices, and margins.
3. Discuss the KPI definitions and why order-level grain matters.
4. Walk through cohort retention and the 90-day churn-risk rule.
5. Finish with the dashboard recommendations and how you would measure campaign impact.

## Notes

Do not claim the fictional company or synthetic records are real. Lead with the methods, analysis, and decisions you produced.
