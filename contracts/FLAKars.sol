// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.10;

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

    uint256 constant ttl = 10 days;
    address private immutable owner;
    struct ArbitrageInfo {
        address token2;
        address router1;
        address router2;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner of this contract can run this function");
        _;
    }

    constructor(address provider) FlashLoanSimpleReceiverBase(IPoolAddressesProvider(provider)) {
        owner = msg.sender;
    }

    function swap(address router, address tokenIn, address tokenOut, uint256 amount) internal {
        IERC20(tokenIn).approve(router, amount);

        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;

        IUniswapV2Router02(router).swapExactTokensForTokens(amount, 1, path, address(this), block.timestamp + ttl);
    }

    function dexArbitrage(address router1, address router2, address token1, address token2, uint256 amount) external onlyOwner {
        uint256 startBalance = IERC20(token1).balanceOf(address(this));
        uint256 initalToken2Balance = IERC20(token2).balanceOf(address(this));

        swap(router1, token1, token2, amount);
        swap(router2, token2, token1, IERC20(token2).balanceOf(address(this))-initalToken2Balance);

        uint256 newBalance = IERC20(token1).balanceOf(address(this));
        string memory message = "The arbitrage wasnt profitable ";
        message = message.concat(startBalance.toStr()).concat("/").concat(newBalance.toStr());

        require(newBalance > startBalance, message);
    }

    function _dexArbitrage(address router1, address router2, address token1, address token2, uint256 amount) internal {
        uint256 startBalance = IERC20(token1).balanceOf(address(this));
        uint256 initalToken2Balance = IERC20(token2).balanceOf(address(this));

        swap(router1, token1, token2, amount);
        swap(router2, token2, token1, IERC20(token2).balanceOf(address(this))-initalToken2Balance);

        uint256 newBalance = IERC20(token1).balanceOf(address(this));
        string memory message = "The arbitrage wasnt profitable ";
        message = message.concat(startBalance.toStr()).concat("/").concat(newBalance.toStr());

        require(newBalance > startBalance, message);
    }

    function estimateDexArbitrage(address router1, address router2, address token1, address token2, uint256 amount) external onlyOwner view returns(uint256) {
        address pair1 = IUniswapV2Factory(IUniswapV2Router02(router1).factory()).getPair(token1, token2);
        require(pair1 != address(0), "Pair does not exist in router1");
        address pair2 = IUniswapV2Factory(IUniswapV2Router02(router2).factory()).getPair(token2, token1);
        require(pair2 != address(0), "Pair does not exist in router2");

        address[] memory path1 = new address[](2);
        path1[0] = token1;
        path1[1] = token2;

        address[] memory path2 = new address[](2);
        path2[0] = token2;
        path2[1] = token1;

        uint256[] memory amountsOut1 = IUniswapV2Router02(router1).getAmountsOut(amount, path1);
        uint256[] memory amountsOut2 = IUniswapV2Router02(router2).getAmountsOut(amountsOut1[1], path2);

        return amountsOut2[1];
    }

    function balanceOf(address token) external onlyOwner view returns(uint256) {
        return IERC20(token).balanceOf(address(this));
    }

	function withdraw(address tokenAddress, uint256 amount) external onlyOwner {
		IERC20 token = IERC20(tokenAddress);
		token.transfer(owner, amount);
	}

    function flArbitrage(address router1, address router2, address token1, address token2, uint256 amount) external onlyOwner {
        ArbitrageInfo memory info = ArbitrageInfo({
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

    function executeOperation(
        address token,
        uint256 amount,
        uint256 fee,
        address,
        bytes calldata params
    ) external override returns (bool) {
        ArbitrageInfo memory info = abi.decode(params, (ArbitrageInfo));

        _dexArbitrage(info.router1, info.router2, token, info.token2, amount);

        IERC20(token).approve(address(POOL), amount + fee);

        return true;
    }
}