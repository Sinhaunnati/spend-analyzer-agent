import pandas as pd

def load_data():
    return pd.read_csv("data/transactions_categorized.csv")


def get_total_by_category(category: str) -> str:
    """Returns the total amount spent in a given category."""
    df = load_data()
    matches = df[df["category"].str.lower() == category.lower()]
    if matches.empty:
        return f"No transactions found in category '{category}'."
    total = matches["amount"].sum()
    return f"Total spent on {category}: ₹{total:,.2f} across {len(matches)} transactions."


def find_duplicate_charges() -> str:
    """Finds transactions with the same merchant, amount, and date — likely accidental double-charges."""
    df = load_data()
    dupes = df[df.duplicated(subset=["merchant", "amount", "date"], keep=False)]
    if dupes.empty:
        return "No duplicate charges found."
    lines = [
        f"- {row.date}: {row.merchant} charged ₹{row.amount} twice (txn {row.txn_id})"
        for row in dupes.itertuples()
    ]
    return "Possible duplicate charges found:\n" + "\n".join(lines)


def find_unusual_transactions() -> str:
    """Flags transactions significantly larger than the person's typical transaction size, excluding known recurring costs like rent."""
    df = load_data()
    RECURRING_CATEGORIES = ["Rent", "Subscriptions", "Utilities"]
    candidates = df[~df["category"].isin(RECURRING_CATEGORIES)]
    mean = candidates["amount"].mean()
    std = candidates["amount"].std()
    threshold = mean + 2 * std
    unusual = candidates[candidates["amount"] > threshold]
    if unusual.empty:
        return "No unusually large transactions found."
    lines = [
        f"- {row.date}: {row.merchant} — ₹{row.amount} ({row.category})"
        for row in unusual.itertuples()
    ]
    return "Unusually large transactions:\n" + "\n".join(lines)


def get_monthly_comparison(category: str) -> str:
    """Compares spending in a given category across different months."""
    df = load_data()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%B %Y')
    matches = df[df["category"].str.lower() == category.lower()]
    if matches.empty:
        return f"No transactions found in category '{category}'."
    grouped = matches.groupby('month')['amount'].sum().to_dict()
    breakdown = ", ".join([f"{m}: ₹{amt:,.2f}" for m, amt in grouped.items()])
    return f"Monthly trend for {category} — {breakdown}"