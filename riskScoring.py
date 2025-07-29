import pandas as pd
import json
from sklearn.preprocessing import MinMaxScaler
from featureExtraction import extract_features


def compute_risk_scores(features_dict):
    df = pd.DataFrame.from_dict(features_dict, orient='index')

    # Fill missing and clip ratios
    df["repay_ratio"] = df["repay_ratio"].fillna(1).clip(0, 1)

    # Normalize selected features
    scaler = MinMaxScaler()
    df_scaled = scaler.fit_transform(df[["liquidation_count", "net_borrowed", "repay_ratio", "borrow_total_usd"]])

    df_norm = pd.DataFrame(df_scaled, index=df.index, columns=["liquidation", "net_borrowed", "repay_ratio", "borrow_usd"])

    # Invert repay_ratio because higher is safer
    df_norm["repay_ratio"] = 1 - df_norm["repay_ratio"]

    # Weighted sum
    score = (
        df_norm["liquidation"] * 0.4 +
        df_norm["repay_ratio"] * 0.3 +
        df_norm["net_borrowed"] * 0.2 +
        df_norm["borrow_usd"] * 0.1
    )

    # Final score: scale to 0–1000
    df["score"] = (score * 1000).round().astype(int)
    df["wallet_id"] = df.index

    return df[["wallet_id", "score"]]



with open("wallet_data.json", "r") as f:
    wallet_data = json.load(f)

features = extract_features(wallet_data)
risk_scores = compute_risk_scores(features)
risk_scores.to_csv("risk_scores.csv", index=False)