# faucetbot

A simple Python bot to automatically request testnet USDC or EURC tokens from the [Circle Faucet](https://faucet.circle.com/) every hour.

Useful for developers testing smart contracts on networks like Uniswap V4, Base, Arbitrum, and others.

## 🚀 Features

- Requests USDC or EURC tokens from the Circle faucet
- Supports multiple chains (ETH, BASE, UNI, OP, ARB, AVAX, etc.)
- Logs all requests to `~/.faucetbot/{chain}_{token}_log.jsonl`
- Automatically rotates logs when they get too large
- Configurable request interval (default: every 1 hour)

## 🛠 Installation

```bash
pip install faucetbot
````

## ⚙️ Usage

```bash
faucetbot 0xYourWalletAddressHere
```

### Optional Flags

| Flag         | Default | Description                            |
| ------------ | ------- | -------------------------------------- |
| `--token`    | USDC    | Token to request: `USDC` or `EURC`     |
| `--chain`    | ETH     | Chain name: `ETH`, `BASE`, `UNI`, etc. |
| `--interval` | 3600    | Time between requests (in seconds)     |

### Example

```bash
faucetbot 0x1234567890abcdef --token EURC --chain UNI --interval 1800
```

## 📂 Logs

Logs are stored by chain and token in your home directory:

```
~/.faucetbot/uni_usdc_log.jsonl
```

Each line is a JSON object with timestamp, status, and response.

Logs rotate when they reach \~5MB and are archived as:

```
~/.faucetbot/uni_usdc_log.jsonl.<timestamp>.bak
```

## ⚠️ Rate Limiting

The Circle faucet enforces rate limits per wallet address. If you see `"rate_limited"` in your logs, wait a few hours before retrying.

The bot will still log the attempt as a failure.

## 📜 License

MIT – Use freely, fork wildly, attribute generously.

## 🧪 Want more?

* Add support for multiple addresses
* Rotate logs weekly or by count
* Send notifications on success or failure
* Run continuously as a daemon or GitHub Action

Pull requests welcome!
