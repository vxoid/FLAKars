# FLAKars v0.1.4 | etherium network arbitrage bot
## Changelog
- Completely rewrited the bot
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
    "address": "<deployed-contract-address>",
    "LPA": "0xC911B590248d127aD18546B186cC6B324e99F02c",
    "node": "https://goerli.infura.io/v3/<your-infura-token>",
    "abi": "build/FLAKars.abi",
    "bytecode": "build/FLAKars.bin",
    "private_key": "<your-wallet-sk>",
    "weth": "wETH",
    "eth-dex": "uniswap v2",
    "routers": [
        {
            "name": "uniswap v3",
            "router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
            "factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984"
        },
        { "name": "uniswap v2", "router": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D" },
        { "name": "sushiswap", "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506" },
        { "name": "pancakeswap v2", "router": "0xeff92a263d31888d860bd50809a8d171709b7b1c" },
        {
            "name": "pancakeswap v3",
            "router": "0x1b81D678ffb9C0263b24A97847620C99d213eB14",
            "quoter": "0xbC203d7f83677c7ed3F7acEc959963E7F4ECC5C2",
            "factory": "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865"
        }
    ],
    "tokens": [
        { "symbol": "USDC", "address": "0x07865c6e87b9f70255377e024ace6630c1eaa37f" },
        { "symbol": "wETH", "address": "0xb4fbf271143f4fbf7b91a5ded31805e42b2208d6" },
        { "symbol": "wBTC", "address": "0xc04b0d3107736c32e19f1c62b2af67be61d63a05" },
        { "symbol": "DAI", "address": "0xdc31Ee1784292379Fbb2964b3B9C4124D8F89C60" },
        { "symbol": "USDT", "address": "0xc2c527c0cacf457746bd31b2a698fe89de2b6d49" },
        { "symbol": "LINK", "address": "0x326C977E6efc84E512bB9C30f76E30c160eD06FB" },
        { "symbol": "UNI", "address": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984" },
        { "symbol": "USDC aave", "address": "0x65aFADD39029741B3b8f0756952C74678c9cEC93" },
        { "symbol": "wETH aave", "address": "0xCCB14936C2E000ED8393A571D15A2672537838Ad" },
        { "symbol": "wBTC aave", "address": "0x45AC379F019E48ca5dAC02E54F406F99F5088099" },
        { "symbol": "DAI aave", "address": "0xBa8DCeD3512925e52FE67b1b5329187589072A55" },
        { "symbol": "USDT aave", "address": "0x2E8D98fd126a32362F2Bd8aA427E59a1ec63F780" },
        { "symbol": "LINK aave", "address": "0xe9c4393a23246293a8D31BF7ab68c17d4CF90A29" }
    ],
    "fl": [
      "USDC aave",
      "wETH aave",
      "wBTC aave",
      "DAI aave",
      "USDT aave",
      "LINK aave"
    ]
}
``` 