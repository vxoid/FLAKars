# FLAKars v0.1.5 | etherium network arbitrage bot
## Changelog
- + TG Logger & Fixes
## Technologies (Libraries)
- <a href="https://aave.com">Flashloans</a>
- <a href="https://uniswap.org">Uniswap V2 | V3 Interfaces</a>
## Usage
- `python scripts/publish.py <config.json>` - deploys the contract
- `python scripts/arbitrage.py <config.json>` - runs arbitrage on deployed contract
## Setup
- Clone this repository
- Deploy the contract using `scripts/publish.py` script
- Create a config file
- Replace `<your-infura-token>` with your infura token, `<deployed-contract-address>` with deployed contract address and `<your-wallet-sk>` with your ethereum wallet private address
## Example config file
```json
{
  "weth": "wMATIC",
  "weth-dex": "uniswap v2",
  "amount": 1000,
  "min_income": 0.1,
  "address": "0x3c36cC5b01149d29a7057eDBe3712dc8072A4C76",
  "LPA": "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb",
  "node": "https://polygon-mainnet.infura.io/v3/<token>",
  "abi": "build/FLAKars.abi",
  "bytecode": "build/FLAKars.bin",
  "private_key": "<pk>",
  "routers": [
    {
      "name": "uniswap v3",
      "router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
      "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
      "factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984"
    },
    { "name": "uniswap v2", "router": "0xedf6066a2b290C185783862C7F4776A2C8077AD1" },
    { "name": "sushiswap", "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506" },
    { "name": "quickswap", "router": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff" }
  ],
  "fl": [
    "USDC",
    "EURS",
    "wETH",
    "wBTC",
    "DAI",
    "USDT",
    "LINK"
  ],
  "tokens": [
    { "symbol": "wMATIC", "address": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270" },
    { "symbol": "USDC", "address": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174" },
    { "symbol": "EURS", "address": "0xe111178a87a3bff0c8d18decba5798827539ae99" },
    { "symbol": "wETH", "address": "0x7ceb23fd6bc0add59e62ac25578270cff1b9f619" },
    { "symbol": "wBTC", "address": "0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6" },
    { "symbol": "DAI", "address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063" },
    { "symbol": "USDT", "address": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f" },
    { "symbol": "AAVE", "address": "0xd6df932a45c0f255f85145f286ea0b292b21c90b" },
    { "symbol": "LINK", "address": "0x53e0bca35ec356bd5dddfebbd1fc0fd03fabad39" },
    { "symbol": "UNI", "address": "0xb33eaad8d922b1083446dc23f610c2567fb5180f" },
    { "symbol": "BAT", "address": "0x3cef98bb43d732e2f285ee605a8158cde967d219" },
    { "symbol": "CTSI", "address": "0x2727ab1c2d22170abc9b595177b2d5c6e1ab7b7b" },
    { "symbol": "SHIB", "address": "0x6f8a06447Ff6FcF75d803135a7de15CE88C1d4ec" }
  ],
  "telegram_loggers": [
    {
      "token": "<token>",
      "chat_id": "<chatid>"
    }
  ]
}
``` 