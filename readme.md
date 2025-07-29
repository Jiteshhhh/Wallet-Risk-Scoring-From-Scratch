# DeFi Wallet Risk Scoring System

This project analyzes historical user activity from the Compound V2 protocol to assign **risk scores (0–1000)** to Ethereum wallet addresses.

---

## Objective

To build a scoring system that quantifies how risky a wallet's behavior has been on Compound lending protocols. This can be used for:

- Risk-aware airdrops
- DeFi creditworthiness
- Anomaly detection

---

## Data Collection

The data was fetched from [The Graph](https://thegraph.com/) using Compound V2 subgraphs.

Each wallet's activity includes:

- Number of borrows, repays, withdraws, liquidations
- Total USD borrowed, repaid, and withdrawn
- Timestamps and token details for each event

### Query Schema Used

```graphql
query($user: String!) {
  account(id: $user) {
    id
    borrowCount
    repayCount
    withdrawCount
    liquidateCount

    borrows {
      amountUSD
      amount
      timestamp
      asset {
        symbol
        lastPriceUSD
      }
    }

    repays {
      amountUSD
      amount
      timestamp
      asset {
        symbol
        lastPriceUSD
      }
    }

    withdraws {
      amountUSD
      amount
      timestamp
      asset {
        symbol
        lastPriceUSD
      }
    }

    liquidates {
      amountUSD
      amount
      timestamp
      asset {
        symbol
        lastPriceUSD
      }
    }
  }
}
```

---

## Data Preparation / Feature Selection

Parsed the raw wallet data to compute the following features:

| Feature              | Description                                             |
| -------------------- | ------------------------------------------------------- |
| `borrow_count`       | Number of borrow events                                 |
| `borrow_total_usd`   | Total borrowed amount in USD                            |
| `repay_count`        | Number of repay events                                  |
| `repay_total_usd`    | Total repaid amount in USD                              |
| `liquidation_count`  | Number of liquidation events (higher means higher risk) |
| `withdraw_total_usd` | Total withdrawn from protocol                           |
| `net_borrowed`       | `borrow_total_usd - repay_total_usd`                    |
| `repay_ratio`        | `repay_total_usd / borrow_total_usd`                    |

Missing or zero borrows default to a safe repay ratio of 1.

---

## Risk Scoring

Assigned scores from 0 to 1000 where higher means higher risk.

### Feature Weights

| Feature             | Direction of Risk | Weight |
| ------------------- | ----------------- | ------ |
| `liquidation_count` | ↑ higher = risky  | 0.4    |
| `repay_ratio`       | ↓ lower = risky   | 0.3    |
| `net_borrowed`      | ↑ higher = risky  | 0.2    |
| `borrow_total_usd`  | ↑ higher = risky  | 0.1    |


### Normalization Method

Used Min-Max Normalization:
```python
from sklearn.preprocessing import MinMaxScaler
```
`repay_ratio` is inverted `(1 - ratio)` so that higher values mean higher risk.

### Final Score

```python
score = (
    0.4 * normalized_liquidation_count +
    0.3 * (1 - normalized_repay_ratio) +
    0.2 * normalized_net_borrowed +
    0.1 * normalized_borrow_usd
)

risk_score = round(score * 1000)
```

---

# Steps to Run the code

1. Install dependencies:
```bash
pip install pandas tqdm scikit-learn
```

2. Head to [the graph] `https://thegraph.com/studio/apikeys/` and create your own API key to use it for retrieving the data.

3. Create .env file to store your API key as shown:
`THE_GRAPH_API_KEY = <ENTER_YOUR_API_KEY>`

4. First download the data by running the following script:
```bash
python dataRetrieval.py
```
This will create a `wallet_data.json` file.

5. Place the `walletids.csv` file in the same directory as `riskScoring.py` file which contains the `wallet_id` of all the wallets for which the risk score is needed.

6. Run the following bash command to get `risk_scores.csv` file which has two columns named: `wallet_id` and `score`
```bash
python riskScoring.py
```
