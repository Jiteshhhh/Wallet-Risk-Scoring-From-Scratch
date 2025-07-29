import requests
import pandas as pd
from tqdm import tqdm
import json
import os

API_KEY = os.getenv("THE_GRAPH_API_KEY")

COMPOUND_V2 = f"https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/4TbqVA8p2DoBd5qDbPMwmDZv3CsJjWtxo8nVSqF2tA9a"
COMPOUND_V3 = f"https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/AwoxEZbiWLvv6e3QdvdMZw4WDURdGbvPfHmZRc8Dpfz9"

def fetch_user_events(wallet, gql_endpoint):
    query = """
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
    """
    resp = requests.post(gql_endpoint, json={"query": query, "variables": {"user": wallet.lower()}})
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        raise ValueError(f"GraphQL error for {wallet}: {data['errors']}")

    return data.get("data", {}).get("account")

# Load wallet list
df = pd.read_csv("walletids.csv")
wallets = df["wallet_id"].tolist()

# Store all data here
wallet_data = {}

# Loop through each wallet
for wallet in tqdm(wallets, desc="Fetching user events"):
    try:
        user_data_v2 = fetch_user_events(wallet, COMPOUND_V2)
        user_data_v3 = fetch_user_events(wallet, COMPOUND_V3)

        wallet_data[wallet] = {
            "compound_v2": user_data_v2 if user_data_v2 else {},
            "compound_v3": user_data_v3 if user_data_v3 else {}
        }

    except Exception as e:
        print(f"Error processing wallet {wallet}: {e}")
        wallet_data[wallet] = {"error": str(e)}

# Save everything to a single JSON file
with open("wallet_data.json", "w") as f:
    json.dump(wallet_data, f, indent=2)

print("All wallet data saved to wallet_data.json")
