import argparse
import time
from faucetbot.logger import log_to_file
from faucetbot.faucet import request_token


def main_loop(destination_address, chain, token, interval_seconds=3600):
    print(f"Starting hourly faucet runner for {destination_address} ⏰")
    while True:
        result = request_token(destination_address, chain, token)
        log_to_file(result, chain, token)

        status = result.get("status", "unknown").upper()
        summary = ""
        response = result.get("response")
        if isinstance(response, dict):
            summary = response.get("data", {}).get("requestToken", {}).get("status", "")

        print(f"[{result['timestamp']}] {status} – {summary}")
        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Circle faucet requests hourly.")
    parser.add_argument(
        "address", help="The destination wallet address to receive USDC."
    )
    parser.add_argument(
        "--token",
        type=str,
        default="USDC",
        choices=["USDC", "EURC"],
        help="Name of token to receive: USDC or EURC (default: USDC)",
    )

    parser.add_argument(
        "--chain",
        type=str,
        default="ETH",
        choices=["BASE", "UNI", "ETH", "ARB", "AVAX", "OP"],
        help="Chain to receive test token (default: ETH)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Request interval in seconds (default: 3600)",
    )
    args = parser.parse_args()

    main_loop(args.address, args.chain, args.token, interval_seconds=args.interval)
