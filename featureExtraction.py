import json

def extract_features(wallet_data):
    features = {}

    for wallet, protocols in wallet_data.items():
        v2 = protocols.get("compound_v2", {}) or {}

        borrow_count = v2.get("borrowCount", 0) or 0
        repay_count = v2.get("repayCount", 0) or 0
        liquidation_count = v2.get("liquidateCount", 0) or 0

        borrows = v2.get("borrows", [])
        repays = v2.get("repays", [])
        withdraws = v2.get("withdraws", [])

        borrow_total = sum(float(b["amountUSD"]) for b in borrows if b.get("amountUSD"))
        repay_total = sum(float(r["amountUSD"]) for r in repays if r.get("amountUSD"))
        withdraw_total = sum(float(w["amountUSD"]) for w in withdraws if w.get("amountUSD"))

        repay_ratio = repay_total / borrow_total if borrow_total else 1  # assume full repay if no borrow

        features[wallet] = {
            "borrow_count": borrow_count,
            "repay_count": repay_count,
            "liquidation_count": liquidation_count,
            "borrow_total_usd": borrow_total,
            "repay_total_usd": repay_total,
            "withdraw_total_usd": withdraw_total,
            "net_borrowed": borrow_total - repay_total,
            "repay_ratio": repay_ratio
        }

    return features

with open("wallet_data.json", "r") as f:
    wallet_data = json.load(f)

features = extract_features(wallet_data)
print(json.dumps(features, indent=2))   