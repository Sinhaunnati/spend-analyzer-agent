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
    """Flags transactions significantly larger than typical transaction size, excluding recurring costs."""
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


def run_financial_health_audit() -> str:
    """Performs a comprehensive financial health audit, calculating fixed vs discretionary spend."""
    df = load_data()
    total_spend = df["amount"].sum()
    fixed_cats = ["Rent", "Subscriptions", "Utilities"]
    fixed_spend = df[df["category"].isin(fixed_cats)]["amount"].sum()
    discretionary_spend = total_spend - fixed_spend
    dupes = df[df.duplicated(subset=["merchant", "amount", "date"], keep=False)]
    
    report = (
        f"📊 **Financial Health Audit Report**\n"
        f"- **Total Spend (3 Months):** ₹{total_spend:,.2f}\n"
        f"- **Fixed Costs (Rent, Utilities, Subs):** ₹{fixed_spend:,.2f} ({(fixed_spend/total_spend)*100:.1f}%)\n"
        f"- **Discretionary Spend:** ₹{discretionary_spend:,.2f} ({(discretionary_spend/total_spend)*100:.1f}%)\n"
        f"- **Active Anomalies Found:** {len(dupes)} potential duplicate charges or waste items flagged.\n"
        f"💡 *Recommendation: Review active subscription renewals to cut unused overhead.*"
    )
    return report


def check_budget_status(monthly_limit: float = 60000.0) -> str:
    """Checks total spending against a target monthly budget limit."""
    df = load_data()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%B %Y')
    monthly_spend = df.groupby('month')['amount'].sum()
    
    report = []
    for month, total in monthly_spend.items():
        status = "⚠️ OVER BUDGET" if total > monthly_limit else "✅ Within Budget"
        report.append(f"- {month}: ₹{total:,.2f} / ₹{monthly_limit:,.2f} ({status})")
    return "Budget Health Report:\n" + "\n".join(report)


def search_transactions_by_keyword(keyword: str) -> str:
    """Searches for transactions matching a specific merchant or description keyword."""
    df = load_data()
    matches = df[df['merchant'].str.contains(keyword, case=False, na=False) | 
                 df['description'].str.contains(keyword, case=False, na=False)]
    if matches.empty:
        return f"No transactions found matching '{keyword}'."
    lines = [f"- {row.date}: {row.merchant} — ₹{row.amount} ({row.category})" for row in matches.itertuples()]
    return f"Found {len(matches)} matching transactions:\n" + "\n".join(lines)