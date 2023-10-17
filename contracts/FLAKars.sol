// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.10;

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
    }

    error NotProfitableArbitrage(uint256 startBalance, uint256 newBalance);
    error TooSmallIncome(uint256 income, uint256 minIncome);
    error CallIsNotFromPool(address msgSender);

    address[] private tokens;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner of this contract can run this function");
        _;
    }

    constructor(address provider) FlashLoanSimpleReceiverBase(IPoolAddressesProvider(provider)) {
        owner = msg.sender;
    }

    function swap(address router, address tokenIn, address tokenOut, uint256 amount) internal {
        if (tokenIn == tokenOut) {
            return;
        }

        IERC20(tokenIn).approve(router, amount);
        if (isV2(router)) {
            address[] memory path = new address[](2);
            path[0] = tokenIn;
            path[1] = tokenOut;

            IUniswapV2Router02(router).swapExactTokensForTokens(amount, 1, path, address(this), block.timestamp + ttl);
        } else {
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
        }
    }

    function arbitrage(address router1, address router2, address token1, address token2, uint256 amount) public onlyOwner returns(uint256) {
        uint256 startBalance = IERC20(token1).balanceOf(address(this));
        uint256 initalToken2Balance = IERC20(token2).balanceOf(address(this));

        swap(router1, token1, token2, amount);
        swap(router2, token2, token1, IERC20(token2).balanceOf(address(this))-initalToken2Balance);

        uint256 newBalance = IERC20(token1).balanceOf(address(this));
        if (newBalance <= startBalance)
            revert NotProfitableArbitrage(startBalance, newBalance);

        return newBalance - startBalance;
    }

    function arbitrageWithMinIncome(address router1, address router2, address token1, address token2, uint256 amount, uint256 minIncome) public onlyOwner returns(uint256) {
        uint256 startBalance = IERC20(token1).balanceOf(address(this));
        uint256 initalToken2Balance = IERC20(token2).balanceOf(address(this));

        swap(router1, token1, token2, amount);
        swap(router2, token2, token1, IERC20(token2).balanceOf(address(this))-initalToken2Balance);

        uint256 newBalance = IERC20(token1).balanceOf(address(this));
        if (newBalance <= startBalance)
            revert NotProfitableArbitrage(startBalance, newBalance);

        uint256 income = newBalance - startBalance;

        if (income < minIncome)
            revert TooSmallIncome(income, minIncome);

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

    function available(address router, address token1, address token2) public view onlyOwner returns (bool) {
        if (isV2(router)) {
		        address pair = IUniswapV2Factory(IUniswapV2Router02(router).factory()).getPair(token1, token2);
            return pair != address(0);
        } else {
            address pool = IUniswapV3Factory(router).getPool(token1, token2, feev3);
            return pool != address(0);
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

    function flashLoanArbitrage(address router1, address router2, address token1, address token2, uint256 amount) external onlyOwner {
        ArbitrageInfo memory info = ArbitrageInfo({
            minIncome: 0,
            token2: token2,
            router1: router1,
            router2: router2
        });

        POOL.flashLoanSimple(
            address(this),
            token1,
            amount,
            abi.encode(info),
            0
        );
    }

    function flashLoanArbitrageWithMinIncome(address router1, address router2, address token1, address token2, uint256 amount, uint256 minIncome) external onlyOwner {
        ArbitrageInfo memory info = ArbitrageInfo({
            minIncome: minIncome,
            token2: token2,
            router1: router1,
            router2: router2
        });

        POOL.flashLoanSimple(
            address(this),
            token1,
            amount,
            abi.encode(info),
            0
        );
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
        if (msg.sender != address(POOL))
            revert CallIsNotFromPool(msg.sender);

        ArbitrageInfo memory info = abi.decode(params, (ArbitrageInfo));

        if (!isTokenAdded(token))
            tokens.push(token);

        if (info.minIncome == 0)
            arbitrage(info.router1, info.router2, token, info.token2, amount);
        else
            arbitrageWithMinIncome(info.router1, info.router2, token, info.token2, amount, minIncome);

        IERC20(token).approve(address(POOL), amount + fee);

        return true;
    }

    function isV2(address router) public view returns (bool) {
        (bool success, ) = router.staticcall(abi.encodeWithSignature("WETH()"));
        return success;
    }
}