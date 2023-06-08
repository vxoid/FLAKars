from web3 import Web3

def balanceOf(contract, pk, token):
    function = contract.functions.balanceOf(
        Web3.to_checksum_address(token)
    )

    return function.call({ "from": pk })

def withdraw(web3: Web3, contract, account, token, amount):
    function = contract.functions.withdraw(
        Web3.to_checksum_address(token),
        amount
    )

    tx = function.build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gas": function.estimate_gas({ "from": account.address }),
        "gasPrice": web3.eth.gas_price
    })
    signed_tx = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return web3.eth.wait_for_transaction_receipt(tx_hash)

def estimateGasFlTribArbitrage(contract, pk, router1, router2, router3, token1, token2, token3, amount):
    function = contract.functions.flTribArbitrage(
        Web3.to_checksum_address(router1),
        Web3.to_checksum_address(router2),
        Web3.to_checksum_address(router3),
        Web3.to_checksum_address(token1),
        Web3.to_checksum_address(token2),
        Web3.to_checksum_address(token3),
        amount
    )
    return function.estimate_gas({ "from": pk })

def estimateGasFlDualArbitrage(contract, pk, router1, router2, token1, token2, amount):
    function = contract.functions.flDualArbitrage(
        Web3.to_checksum_address(router1),
        Web3.to_checksum_address(router2),
        Web3.to_checksum_address(token1),
        Web3.to_checksum_address(token2),
        amount
    )
    return function.estimate_gas({ "from": pk })

def flTribArbitrage(web3: Web3, contract, account, router1, router2, router3, token1, token2, token3, amount):
    function = contract.functions.flTribArbitrage(
        Web3.to_checksum_address(router1),
        Web3.to_checksum_address(router2),
        Web3.to_checksum_address(router3),
        Web3.to_checksum_address(token1),
        Web3.to_checksum_address(token2),
        Web3.to_checksum_address(token3),
        amount
    )
    gas_limit = function.estimate_gas({ "from": account.address }) # even if gas limit was specified i need to test will arbitrage be successful

    tx = function.build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gas": gas_limit,
        "gasPrice": web3.eth.gas_price
    })
    signed_tx = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return web3.eth.wait_for_transaction_receipt(tx_hash)

def flDualArbitrage(web3: Web3, contract, account, router1, router2, token1, token2, amount):
    function = contract.functions.flDualArbitrage(
        Web3.to_checksum_address(router1),
        Web3.to_checksum_address(router2),
        Web3.to_checksum_address(token1),
        Web3.to_checksum_address(token2),
        amount
    )
    gas_limit = function.estimate_gas({ "from": account.address }) # even if gas limit was specified i need to test will arbitrage be successful

    tx = function.build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gas": gas_limit,
        "gasPrice": web3.eth.gas_price
    })
    signed_tx = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return web3.eth.wait_for_transaction_receipt(tx_hash)

def tribDexArbitrage(web3: Web3, contract, account, router1, router2, router3, token1, token2, token3, amount):
    function = contract.functions.tribDexArbitrage(
        Web3.to_checksum_address(router1),
        Web3.to_checksum_address(router2),
        Web3.to_checksum_address(router3),
        Web3.to_checksum_address(token1),
        Web3.to_checksum_address(token2),
        Web3.to_checksum_address(token3),
        amount
    )

    tx = function.build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gas": function.estimate_gas({ "from": account.address }),
        "gasPrice": web3.eth.gas_price
    })
    signed_tx = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return web3.eth.wait_for_transaction_receipt(tx_hash)

def dualDexArbitrage(web3: Web3, contract, account, router1, router2, token1, token2, amount):
    function = contract.functions.dualDexArbitrage(
        Web3.to_checksum_address(router1),
        Web3.to_checksum_address(router2),
        Web3.to_checksum_address(token1),
        Web3.to_checksum_address(token2),
        amount
    )

    tx = function.build_transaction({
        "from": account.address,
        "nonce": web3.eth.get_transaction_count(account.address),
        "gas": function.estimate_gas({ "from": account.address }),
        "gasPrice": web3.eth.gas_price
    })
    signed_tx = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return web3.eth.wait_for_transaction_receipt(tx_hash)

def convert(contract, pk, router, tokenIn, tokenOut, amount):
    function = contract.functions.convert(
        Web3.to_checksum_address(router),
        Web3.to_checksum_address(tokenIn),
        Web3.to_checksum_address(tokenOut),
        amount
    )

    return function.call({ "from": pk })

def available(contract, pk, router, token1, token2):
    function = contract.functions.available(
        Web3.to_checksum_address(router),
        Web3.to_checksum_address(token1),
        Web3.to_checksum_address(token2),
    )

    return function.call({ "from": pk })