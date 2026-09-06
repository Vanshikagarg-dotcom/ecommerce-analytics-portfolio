-- PostgreSQL-compatible SQL. Import customers, products, and orders as named tables.
WITH completed_orders AS (
    SELECT o.order_id, o.customer_id, o.order_date, o.product_id, o.sales, o.cost,
           c.region, c.acquisition_channel, p.category
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN products p ON o.product_id = p.product_id
    WHERE o.status = 'Completed'
), customer_orders AS (
    SELECT customer_id,
           COUNT(DISTINCT order_id) AS order_count,
           SUM(sales) AS lifetime_revenue,
           MAX(order_date) AS last_order_date
    FROM completed_orders
    GROUP BY customer_id
)
SELECT ROUND(SUM(sales), 2) AS revenue,
       ROUND(SUM(sales - cost), 2) AS profit,
       ROUND(100.0 * SUM(sales - cost) / NULLIF(SUM(sales), 0), 2) AS profit_margin_pct,
       ROUND(AVG(sales), 2) AS average_order_value,
       ROUND(100.0 * AVG(CASE WHEN co.order_count > 1 THEN 1.0 ELSE 0 END), 2) AS repeat_purchase_rate_pct
FROM completed_orders o
JOIN customer_orders co USING (customer_id);

-- Monthly revenue and month-over-month growth (window function).
WITH monthly AS (
  SELECT DATE_TRUNC('month', order_date)::date AS month, SUM(sales) AS revenue
  FROM orders WHERE status = 'Completed' GROUP BY 1
)
SELECT month, ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * (revenue / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) - 1), 2) AS mom_growth_pct
FROM monthly ORDER BY month;

-- Retention cohort: percent of customers who ordered in each later month.
WITH first_purchase AS (
  SELECT customer_id, DATE_TRUNC('month', MIN(order_date)) AS cohort_month
  FROM orders WHERE status = 'Completed' GROUP BY 1
), activity AS (
  SELECT DISTINCT o.customer_id, f.cohort_month, DATE_TRUNC('month', o.order_date) AS order_month
  FROM orders o JOIN first_purchase f USING (customer_id) WHERE o.status = 'Completed'
)
SELECT cohort_month::date,
       (EXTRACT(YEAR FROM order_month) - EXTRACT(YEAR FROM cohort_month)) * 12 +
       EXTRACT(MONTH FROM order_month) - EXTRACT(MONTH FROM cohort_month) AS months_since_first_order,
       COUNT(DISTINCT customer_id) AS retained_customers
FROM activity GROUP BY 1, 2 ORDER BY 1, 2;

-- Churn-risk audience: customers with no completed order in the last 90 days.
WITH last_orders AS (
  SELECT customer_id, MAX(order_date) AS last_order_date, SUM(sales) AS lifetime_revenue
  FROM orders WHERE status = 'Completed' GROUP BY 1
), cutoff AS (SELECT MAX(order_date) AS max_order_date FROM orders)
SELECT l.customer_id, c.region, c.acquisition_channel, l.last_order_date, ROUND(l.lifetime_revenue, 2) AS lifetime_revenue
FROM last_orders l CROSS JOIN cutoff x JOIN customers c USING (customer_id)
WHERE l.last_order_date < x.max_order_date - INTERVAL '90 days'
ORDER BY lifetime_revenue DESC;
