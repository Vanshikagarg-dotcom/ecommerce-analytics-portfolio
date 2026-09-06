"""Generate executive KPI tables and charts from the source tables."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / "data", ROOT / "outputs"


def svg_bar_chart(frame: pd.DataFrame, label: str, value: str, title: str, path: Path) -> None:
    """Write a dependency-free horizontal bar chart for portfolio previews."""
    width, height, left, row = 840, 80 + 55 * len(frame), 185, 55
    maximum = frame[value].max()
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
             '<style>text{font-family:Arial;fill:#192A3A}.title{font-size:20px;font-weight:bold}.label{font-size:14px}.value{font-size:13px}</style>',
             f'<text x="30" y="35" class="title">{title}</text>']
    for i, (_, item) in enumerate(frame.iterrows()):
        y = 60 + i * row
        bar_width = 600 * item[value] / maximum
        parts += [f'<text x="{left - 10}" y="{y + 20}" text-anchor="end" class="label">{item[label]}</text>',
                  f'<rect x="{left}" y="{y}" width="{bar_width:.0f}" height="30" fill="#4C78A8" rx="3"/>',
                  f'<text x="{left + bar_width + 8:.0f}" y="{y + 20}" class="value">${item[value]:,.0f}</text>']
    parts.append('</svg>')
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    customers = pd.read_csv(DATA / "customers.csv", parse_dates=["signup_date"])
    products = pd.read_csv(DATA / "products.csv")
    orders = pd.read_csv(DATA / "orders.csv", parse_dates=["order_date"])
    fact = (orders.query("status == 'Completed'")
            .merge(customers, on="customer_id")
            .merge(products[["product_id", "product_name", "category"]], on="product_id"))
    fact["profit"] = fact["sales"] - fact["cost"]
    fact["month"] = fact["order_date"].dt.to_period("M").astype(str)

    customer_rollup = fact.groupby("customer_id").agg(
        orders=("order_id", "nunique"), revenue=("sales", "sum"), profit=("profit", "sum"),
        last_order=("order_date", "max")
    ).reset_index()
    max_date = fact.order_date.max()
    customer_rollup["at_risk"] = (max_date - customer_rollup.last_order).dt.days > 90
    kpis = pd.DataFrame({"metric": ["Revenue", "Profit", "Profit margin", "Average order value", "Repeat purchase rate", "At-risk customers"],
                         "value": [fact.sales.sum(), fact.profit.sum(), fact.profit.sum()/fact.sales.sum(),
                                   fact.sales.mean(), (customer_rollup.orders.gt(1).mean()), customer_rollup.at_risk.sum()]})
    kpis.to_csv(OUT / "kpi_summary.csv", index=False)

    category = fact.groupby("category", as_index=False).agg(revenue=("sales", "sum"), profit=("profit", "sum")).sort_values("revenue")
    region = fact.groupby("region", as_index=False).agg(revenue=("sales", "sum"), profit=("profit", "sum")).sort_values("revenue", ascending=False)
    category.to_csv(OUT / "category_performance.csv", index=False)
    region.to_csv(OUT / "regional_performance.csv", index=False)
    customer_rollup.sort_values("revenue", ascending=False).head(100).to_csv(OUT / "top_customers.csv", index=False)

    monthly = fact.groupby("month", as_index=False).agg(revenue=("sales", "sum"), profit=("profit", "sum"))
    svg_bar_chart(category.sort_values("revenue", ascending=False), "category", "revenue", "Revenue by category", OUT / "category_revenue.svg")
    svg_bar_chart(region, "region", "revenue", "Revenue by region", OUT / "regional_revenue.svg")
    monthly.to_csv(OUT / "monthly_performance.csv", index=False)
    print(kpis.to_string(index=False, formatters={"value": lambda x: f"{x:,.2f}"}))


if __name__ == "__main__":
    main()
