// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.10; // 0.8.10

import "./uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
import "./uniswap/v3-periphery/contracts/interfaces/IQuoter.sol";
import "./uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";
import "./uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

import "./uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
import "./uniswap/v2-core/contracts/interfaces/IUniswapV2Factory.sol";
import "./uniswap/v2-core/contracts/interfaces/IUniswapV2Pair.sol";
import "./uniswap/v2-core/contracts/interfaces/IERC20.sol";

import "./aave/v3-core/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "./aave/v3-core/contracts/interfaces/IPoolAddressesProvider.sol";

contract FLAKars is FlashLoanSimpleReceiverBase {
    uint256 private constant ttl = 10 days;
    uint24 private constant feev3 = 3000; // 0.3 %
    address private immutable owner;
    struct ArbitrageInfo {
        uint256 minIncome;
        address token2;
        address router1;
        address router2;
        UniswapVersion version1;
        UniswapVersion version2;
    }

    enum UniswapVersion {
      V2,
      V3
    }

    address[] private tokens;

    modifier onlyOwner() {
        require(msg.sender == owner, "Access resticted)");
        _;
    }

    constructor(address provider) FlashLoanSimpleReceiverBase(IPoolAddressesProvider(provider)) {
        owner = msg.sender;
    }

    function swap(address router, address tokenIn, address tokenOut, uint256 amount, UniswapVersion version) internal {
        if (tokenIn == tokenOut) {
            return;
        }

        if (version == UniswapVersion.V2) {
            IERC20(tokenIn).approve(router, amount);
            address[] memory path = new address[](2);
            path[0] = tokenIn;
            path[1] = tokenOut;

            IUniswapV2Router02(router).swapExactTokensForTokens(amount, 1, path, address(this), block.timestamp + ttl);
        } else if (version == UniswapVersion.V3) {
            IERC20(tokenIn).approve(router, amount);
            ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
                tokenIn: tokenIn,
                tokenOut: tokenOut,
                fee: feev3,
                recipient: address(this),
                deadline: block.timestamp + ttl,
                amountIn: amount,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: 0
            });

            ISwapRouter(router).exactInputSingle(params);
        } else {
            revert("Invalid Version Passed");
        }
    }

    function arbitrage(address router1, address router2, address token1, address token2, uint256 amount, UniswapVersion version1, UniswapVersion version2) public onlyOwner returns(uint256) {
        return _arbitrage(router1, router2, token1, token2, amount, version1, version2);
    }
    
    function arbitrageWithMinIncome(address router1, address router2, address token1, address token2, uint256 amount, uint256 minIncome, UniswapVersion version1, UniswapVersion version2) public onlyOwner returns(uint256) {
        return _arbitrageWithMinIncome(router1, router2, token1, token2, amount, minIncome, version1, version2);
    }
  
    function _arbitrage(address router1, address router2, address token1, address token2, uint256 amount, UniswapVersion version1, UniswapVersion version2) private returns(uint256) {
        uint256 startBalance = IERC20(token1).balanceOf(address(this));
        uint256 initalToken2Balance = IERC20(token2).balanceOf(address(this));

        swap(router1, token1, token2, amount, version1);
        swap(router2, token2, token1, IERC20(token2).balanceOf(address(this))-initalToken2Balance, version2);

        uint256 newBalance = IERC20(token1).balanceOf(address(this));
        require(newBalance > startBalance, "Not profitable arbitrage");

        return newBalance - startBalance;
    }

    function _arbitrageWithMinIncome(address router1, address router2, address token1, address token2, uint256 amount, uint256 minIncome, UniswapVersion version1, UniswapVersion version2) private returns(uint256) {
        uint256 income = _arbitrage(router1, router2, token1, token2, amount, version1, version2);

        require(income >= minIncome, "Income is too small");

        return income;
    }

    function convert(address uniswapV2Router, address tokenIn, address tokenOut, uint256 amount) public view onlyOwner returns(uint256) {
        if (tokenIn == tokenOut)
            return amount;

        address[] memory path;
        path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;
        uint256[] memory amountOutMins = IUniswapV2Router02(uniswapV2Router).getAmountsOut(amount, path);
        return amountOutMins[path.length - 1];
    }

    function available(address router, address token1, address token2, UniswapVersion version) public view onlyOwner returns (bool) {
        if (version == UniswapVersion.V2) {
		        address pair = IUniswapV2Factory(IUniswapV2Router02(router).factory()).getPair(token1, token2);
            return pair != address(0);
        } else if (version == UniswapVersion.V3) {
            address pool = IUniswapV3Factory(router).getPool(token1, token2, feev3);
            return pool != address(0);
        } else {
            revert("Invalid Version Passed");
        }
    }

    function withdraw(address tokenAddress, uint256 amount) external onlyOwner {
        IERC20 token = IERC20(tokenAddress);
        token.transfer(owner, amount);
    }

    function withdrawAll() external onlyOwner {
        for (uint256 i = 0; i < tokens.length; i++) {
            IERC20 token = IERC20(tokens[i]);

            token.transfer(owner, token.balanceOf(address(this)));
        }
    }

    function flashLoanArbitrage(address router1, address router2, address token1, address token2, uint256 amount, UniswapVersion version1, UniswapVersion version2) external onlyOwner {
        ArbitrageInfo memory info = ArbitrageInfo({
            minIncome: 0,
            token2: token2,
            router1: router1,
            router2: router2,
            version1: version1,
            version2: version2
        });

        POOL.flashLoanSimple(
            address(this),
            token1,
            amount,
            abi.encode(info),
            0
        );
    }

    function flashLoanArbitrageWithMinIncome(address router1, address router2, address token1, address token2, uint256 amount, uint256 minIncome, UniswapVersion version1, UniswapVersion version2) external onlyOwner {
        ArbitrageInfo memory info = ArbitrageInfo({
            minIncome: minIncome,
            token2: token2,
            router1: router1,
            router2: router2,
            version1: version1,
            version2: version2
        });

        POOL.flashLoanSimple(
            address(this),
            token1,
            amount,
            abi.encode(info),
            0
        );
    }

    function decimalsOf(address token) public view returns (uint8) {
      return IERC20(token).decimals();
    }

    function isTokenAdded(address token) internal view returns (bool) {
        for (uint256 i = 0; i < tokens.length; i++) {
            if (tokens[i] == token)
                return true;
        }
        return false;
    }

    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        address,
        bytes calldata params
    ) external override returns (bool) {
        require(msg.sender == address(POOL), "Access restricted)");

        ArbitrageInfo memory info = abi.decode(params, (ArbitrageInfo));

        if (!isTokenAdded(token))
            tokens.push(token);

        if (info.minIncome == 0)
            _arbitrage(info.router1, info.router2, token, info.token2, amount, info.version1, info.version2);
        else
            _arbitrageWithMinIncome(info.router1, info.router2, token, info.token2, amount, info.minIncome, info.version1, info.version2);

        IERC20(token).approve(address(POOL), amount + fee);

        return true;
    }
}