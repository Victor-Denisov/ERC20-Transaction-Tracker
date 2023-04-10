import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd


def fetch_token_balances(wallet_address):
    # Request token transfers from etherscan API
    url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={wallet_address}&startblock=0&endblock=999999999&sort=asc&apikey={etherscan_api_key}"
    response = requests.get(url)

    # Extract relevant information from response and store in a list of dictionaries
    transfers = []
    for tx in response.json()["result"]:
        if tx["to"].lower() == wallet_address.lower():
            direction = "in"
        else:
            direction = "out"
        token_data = {
            "timestamp": int(tx["timeStamp"]),
            "token_symbol": tx["tokenSymbol"],
            "token_amount": float(tx["value"]) / 10 ** int(tx["tokenDecimal"]),
            "direction": direction
        }
        transfers.append(token_data)

    # Group token transfers by timestamp and token symbol
    token_balances = {}
    for transfer in transfers:
        timestamp = transfer["timestamp"]
        token_symbol = transfer["token_symbol"]
        token_amount = transfer["token_amount"]
        direction = transfer["direction"]
        if timestamp not in token_balances:
            token_balances[timestamp] = {}
        if token_symbol not in token_balances[timestamp]:
            token_balances[timestamp][token_symbol] = 0
        if direction == "in":
            token_balances[timestamp][token_symbol] += token_amount
        else:
            token_balances[timestamp][token_symbol] -= token_amount

    # Convert dictionary to pandas dataframe
    df = pd.DataFrame.from_dict(token_balances, orient="index")
    df.index = pd.to_datetime(df.index, unit="s")
    df = df.sort_index()

    return df


def main():
    st.title("Crypto ERC20 Transaction Tracker")
    st.write("Enter your wallet address to track your cryptocurrency portfolio.")
    wallet_address = st.text_input("Wallet Address")
    if wallet_address:
        token_balances = fetch_token_balances(wallet_address)
        st.write(token_balances)
        token = st.selectbox('Please select a token', token_balances.columns)

        # Plot token balances over time
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(token_balances.index, token_balances[token], label=token)
        ax.legend()
        ax.set_xlabel("Time")
        ax.set_ylabel("Token Value")
        ax.set_title("Token Transactions Over Time")
        st.pyplot(fig)

        # Fetch ETH balance
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={wallet_address}&tag=latest&apikey={etherscan_api_key}"
        response = requests.get(url)
        eth_balance = float(response.json()["result"]) / 10 ** 18

        st.write("The wallet's ETH balance is: " + str(eth_balance))


if __name__ == "__main__":
    main()
