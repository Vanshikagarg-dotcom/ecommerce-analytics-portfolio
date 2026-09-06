"""Create reproducible, portfolio-safe e-commerce source tables."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RNG = np.random.default_rng(42)


def main() -> None:
    DATA.mkdir(exist_ok=True)
    n_customers, n_orders = 8500, 18000
    customer_ids = np.arange(10001, 10001 + n_customers)
    signup_dates = pd.Timestamp("2022-01-01") + pd.to_timedelta(
        RNG.integers(0, 730, n_customers), unit="D"
    )
    customers = pd.DataFrame({
        "customer_id": customer_ids,
        "signup_date": signup_dates,
        "region": RNG.choice(["North", "South", "East", "West"], n_customers,
                             p=[0.28, 0.22, 0.25, 0.25]),
        "acquisition_channel": RNG.choice(["Organic", "Paid Search", "Email", "Social", "Referral"],
                                            n_customers, p=[0.32, 0.25, 0.16, 0.17, 0.10]),
    })

    products = pd.DataFrame([
        (1, "Noise-cancelling Headphones", "Electronics", 145, 79),
        (2, "Wireless Keyboard", "Electronics", 72, 34),
        (3, "Desk Lamp", "Home Office", 48, 21),
        (4, "Ergonomic Chair", "Home Office", 280, 155),
        (5, "Running Shoes", "Sports", 95, 43),
        (6, "Yoga Mat", "Sports", 35, 13),
        (7, "Insulated Bottle", "Lifestyle", 27, 8),
        (8, "Travel Backpack", "Lifestyle", 88, 39),
        (9, "Coffee Grinder", "Kitchen", 62, 28),
        (10, "Chef Knife Set", "Kitchen", 110, 54),
    ], columns=["product_id", "product_name", "category", "unit_price", "unit_cost"])

    # Prefer earlier customers slightly, giving a realistic repeat-purchase distribution.
    weights = np.linspace(1.7, 0.6, n_customers)
    sampled_customers = RNG.choice(customer_ids, n_orders, p=weights / weights.sum())
    order_dates = pd.Timestamp("2023-01-01") + pd.to_timedelta(
        RNG.integers(0, 730, n_orders), unit="D"
    )
    product_ids = RNG.choice(products.product_id, n_orders,
                             p=[.13, .10, .10, .05, .12, .10, .12, .09, .10, .09])
    lookup = products.set_index("product_id")
    quantities = RNG.choice([1, 2, 3, 4], n_orders, p=[.61, .27, .09, .03])
    discount = RNG.choice([0, .05, .10, .15, .20], n_orders, p=[.43, .23, .18, .10, .06])
    unit_price = lookup.loc[product_ids, "unit_price"].to_numpy()
    unit_cost = lookup.loc[product_ids, "unit_cost"].to_numpy()
    sales = np.round(unit_price * quantities * (1 - discount), 2)
    orders = pd.DataFrame({
        "order_id": np.arange(500001, 500001 + n_orders),
        "customer_id": sampled_customers,
        "order_date": order_dates,
        "product_id": product_ids,
        "quantity": quantities,
        "discount_pct": discount,
        "sales": sales,
        "cost": np.round(unit_cost * quantities, 2),
        "status": RNG.choice(["Completed", "Returned", "Cancelled"], n_orders, p=[.92, .05, .03]),
    })
    # A completed order must occur after customer sign-up.
    signup_lookup = customers.set_index("customer_id").signup_date
    invalid = orders.order_date < orders.customer_id.map(signup_lookup)
    orders.loc[invalid, "order_date"] = orders.loc[invalid, "customer_id"].map(signup_lookup) + pd.to_timedelta(
        RNG.integers(0, 60, invalid.sum()), unit="D"
    )

    customers.to_csv(DATA / "customers.csv", index=False)
    products.to_csv(DATA / "products.csv", index=False)
    orders.sort_values("order_date").to_csv(DATA / "orders.csv", index=False)
    print(f"Wrote {len(customers):,} customers, {len(products)} products, and {len(orders):,} orders to {DATA}")


if __name__ == "__main__":
    main()
