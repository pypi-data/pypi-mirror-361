import requests
from datetime import datetime


def request_token(destination_address, chain="ETH", token="USDC"):
    url = "https://faucet.circle.com/api/graphql"
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "origin": "https://faucet.circle.com",
        "referer": "https://faucet.circle.com/",
    }
    payload = {
        "operationName": "RequestToken",
        "variables": {
            "input": {
                "destinationAddress": destination_address,
                "token": token,
                "blockchain": chain,
            }
        },
        "query": """
            mutation RequestToken($input: RequestTokenInput!) {
              requestToken(input: $input) {
                ...RequestTokenResponseInfo
                __typename
              }
            }

            fragment RequestTokenResponseInfo on RequestTokenResponse {
              amount
              blockchain
              contractAddress
              currency
              destinationAddress
              explorerLink
              hash
              status
              __typename
            }
        """,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "fail",
                "error": "Invalid JSON response",
                "raw_response": response.text,
            }

        if not isinstance(data, dict):
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "fail",
                "error": "Malformed response (not a dict)",
                "raw_response": str(data),
            }

        faucet_status = data.get("data", {}).get("requestToken", {}).get("status", "")

        return {
            "timestamp": datetime.now().isoformat(),
            "status": "fail" if faucet_status == "rate_limited" else "success",
            "response": data,
        }

    except requests.exceptions.RequestException as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "fail",
            "error": str(e),
        }
