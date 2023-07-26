// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.10;

import "./uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
import "./uniswap/v3-periphery/contracts/interfaces/IQuoter.sol";
import "./uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";

import "./uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
import "./uniswap/v2-core/contracts/interfaces/IUniswapV2Factory.sol";
import "./uniswap/v2-core/contracts/interfaces/IUniswapV2Pair.sol";
import "./uniswap/v2-core/contracts/interfaces/IERC20.sol";

import "./aave/v3-core/contracts/flashloan/base/FlashLoanSimpleReceiverBase.sol";
import "./aave/v3-core/contracts/interfaces/IPoolAddressesProvider.sol";

import "./su.sol";

contract FLAKars is FlashLoanSimpleReceiverBase {
    using StringUtil for string;
    using StringUtil for uint256;

    uint256 private constant ttl = 10 days;
    uint24 private constant feev3 = 3000; // 0.3 %
    address private immutable owner;
    struct ArbitrageInfo {
        bool dual; // true for dual false for trible
        address token2;
        address token3;
        address router1;
        address router2;
        address router3;
    }

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

    function tribDexArbitrage(address router1, address router2, address router3, address token1, address token2, address token3, uint256 amount) external onlyOwner returns(uint256) {
        return _tribDexArbitrage(router1, router2, router3, token1, token2, token3, amount);
    }

    function _tribDexArbitrage(address router1, address router2, address router3, address token1, address token2, address token3, uint256 amount) internal returns(uint256) {
        uint256 startBalance = IERC20(token1).balanceOf(address(this));
        uint256 initalToken2Balance = IERC20(token2).balanceOf(address(this));
        uint256 initalToken3Balance = IERC20(token3).balanceOf(address(this));

        swap(router1, token1, token2, amount);
        swap(router2, token2, token3, IERC20(token2).balanceOf(address(this))-initalToken2Balance);
        swap(router3, token3, token1, IERC20(token3).balanceOf(address(this))-initalToken3Balance);

        uint256 newBalance = IERC20(token1).balanceOf(address(this));
        string memory message = "The arbitrage wasnt profitable ";
        message = message
            .concat(newBalance.toStr())
            .concat("/")
            .concat(startBalance.toStr())
            .concat(" (")
            .concat(((newBalance*100)/startBalance).toStr())
            .concat("%)");

        require(newBalance > startBalance, message);

        return newBalance;
    }

    function dualDexArbitrage(address router1, address router2, address token1, address token2, uint256 amount) external onlyOwner returns(uint256) {
        return _dualDexArbitrage(router1, router2, token1, token2, amount);
    }

    function _dualDexArbitrage(address router1, address router2, address token1, address token2, uint256 amount) internal returns(uint256) {
        uint256 startBalance = IERC20(token1).balanceOf(address(this));
        uint256 initalToken2Balance = IERC20(token2).balanceOf(address(this));

        swap(router1, token1, token2, amount);
        swap(router2, token2, token1, IERC20(token2).balanceOf(address(this))-initalToken2Balance);

        uint256 newBalance = IERC20(token1).balanceOf(address(this));
        string memory message = "The arbitrage wasnt profitable ";
        message = message
            .concat(newBalance.toStr())
            .concat("/")
            .concat(startBalance.toStr())
            .concat(" (")
            .concat(((newBalance*100)/startBalance).toStr())
            .concat("%)");

        require(newBalance > startBalance, message);

        return newBalance;
    }

    function convert(address router, address tokenIn, address tokenOut, uint256 amount) external onlyOwner returns (uint256) {
        return _convert(router, tokenIn, tokenOut, amount);
	  }

    function _convert(address router, address tokenIn, address tokenOut, uint256 amount) internal returns (uint256) {
        if (tokenIn == tokenOut) {
            return amount;
        }

        if (isV2(router)) {
            address[] memory path;
            path = new address[](2);
            path[0] = tokenIn;
            path[1] = tokenOut;
            uint256[] memory amountOutMins = IUniswapV2Router02(router).getAmountsOut(amount, path);
            return amountOutMins[path.length - 1];
        } else {
            IQuoter qouter = IQuoter(router);
            return qouter.quoteExactInputSingle(tokenIn, tokenOut, feev3, amount, 0);
        }
	  }

    function available(address router, address token1, address token2) external view onlyOwner returns (bool) {
        if (isV2(router)) {
		    address pair = IUniswapV2Factory(IUniswapV2Router02(router).factory()).getPair(token1, token2);
            return pair != address(0);
        } else {
            address pool = IUniswapV3Factory(router).getPool(token1, token2, feev3);
            return pool != address(0);
        }
    }

    function balanceOf(address token) external view returns(uint256) {
        return IERC20(token).balanceOf(address(this));
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

    function flTribArbitrage(address router1, address router2, address router3, address token1, address token2, address token3, uint256 amount) external onlyOwner {
        ArbitrageInfo memory info = ArbitrageInfo({
            dual: false,
            token2: token2,
            token3: token3,
            router1: router1,
            router2: router2,
            router3: router3
        });

        POOL.flashLoanSimple(
            address(this),
            token1,
            amount,
            abi.encode(info),
            0
        );
    }

    function flDualArbitrage(address router1, address router2, address token1, address token2, uint256 amount) external onlyOwner {
        ArbitrageInfo memory info = ArbitrageInfo({
            dual: true,
            token2: token2,
            token3: address(0),
            router1: router1,
            router2: router2,
            router3: address(0)
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
            if (tokens[i] == token) {
                return true;
            }
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
        ArbitrageInfo memory info = abi.decode(params, (ArbitrageInfo));

        if (!isTokenAdded(token)) {
            tokens.push(token);
        }

        if (info.dual) {
            _dualDexArbitrage(info.router1, info.router2, token, info.token2, amount);
        } else {
            _tribDexArbitrage(info.router1, info.router2, info.router3, token, info.token2, info.token3, amount);
        }

        IERC20(token).approve(address(POOL), amount + fee);

        return true;
    }

    function isV2(address router) internal view returns (bool) {
        (bool success, ) = router.staticcall(abi.encodeWithSignature("WETH()"));
        return success;
    }
}