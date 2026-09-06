# Power BI Dashboard Build Guide

## Data model

Import `orders.csv` as the fact table and relate it many-to-one to `customers.csv` on `customer_id` and to `products.csv` on `product_id`. Add a dedicated calendar table related to `orders[order_date]`.

Use **Get Data → Text/CSV** and keep the source files in this project's `data/` folder. When those files are updated, select **Home → Refresh** to update all visuals without rebuilding the report.

```DAX
Calendar = CALENDAR(MIN(orders[order_date]), MAX(orders[order_date]))
Revenue = CALCULATE(SUM(orders[sales]), orders[status] = "Completed")
Profit = CALCULATE(SUM(orders[sales]) - SUM(orders[cost]), orders[status] = "Completed")
Profit Margin % = DIVIDE([Profit], [Revenue])
Completed Orders = CALCULATE(DISTINCTCOUNT(orders[order_id]), orders[status] = "Completed")
Average Order Value = DIVIDE([Revenue], [Completed Orders])
Repeat Customers = COUNTROWS(FILTER(VALUES(customers[customer_id]), CALCULATE([Completed Orders]) > 1))
Repeat Purchase Rate % = DIVIDE([Repeat Customers], DISTINCTCOUNT(customers[customer_id]))
```

## One-page layout

Top row: Revenue, Profit, Profit Margin %, AOV, Repeat Purchase Rate cards.

Middle left: monthly revenue line chart. Middle right: revenue/profit by category clustered bar chart.

Bottom left: region-by-category matrix with conditional formatting. Bottom center: acquisition-channel revenue bar chart. Bottom right: churn-risk customer table containing region, last order date, and lifetime revenue.

## Stakeholder narrative

Lead with growth and profitability trends, then explain which categories and regions drive them. Close with the at-risk customer list and a retention action: prioritize high-lifetime-value customers who have been inactive for 90+ days, then evaluate an email incentive via holdout-group incremental revenue.
