from web3.contract.contract import Contract as Web3Contract
from eth_account.signers.local import LocalAccount
from attrs import define, field
from typing import Tuple, List
from .token import Token
from .pair import Pair
from web3 import Web3

@define(kw_only=True)
class Contract:
  web3: Web3 = field()
  address: str = field()
  contract: Web3Contract = field()
  owner_wallet: LocalAccount = field()

  @staticmethod
  def new(node: str, owner_sk: str, address: str, abi) -> "Contract":
    web3 = Web3(Web3.HTTPProvider(node))
    owner_wallet = web3.eth.account.from_key(owner_sk)
    contract = web3.eth.contract(address=address, abi=abi)

    return Contract(web3=web3, address=address, contract=contract, owner_wallet=owner_wallet)
  
  @staticmethod
  def publish(node: str, owner_sk: str, provider: str, abi, bytecode: str) -> Tuple["Contract", str]:
    web3 = Web3(Web3.HTTPProvider(node))
    owner_wallet = web3.eth.account.from_key(owner_sk)
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)

    constructor = contract.constructor(Web3.to_checksum_address(provider))

    estimated_gas = constructor.estimate_gas()
    tx = constructor.build_transaction({
      "gas": estimated_gas,
      "gasPrice": web3.eth.gas_price,
      "nonce": web3.eth.get_transaction_count(owner_wallet.address)
    })

    signed_tx = web3.eth.account.sign_transaction(tx, owner_wallet._private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    address = str(tx_receipt["contractAddress"])

    contract = web3.eth.contract(address=address, abi=abi)

    return (Contract(web3=web3, address=address, contract=contract, owner_wallet=owner_wallet), tx_hash.hex())
  
  def swap(self, pair: Pair, amount: int):
    function = self.contract.functions.swap(
      Web3.to_checksum_address(pair.router.get_arbitrage_address()),
      Web3.to_checksum_address(pair.token_in.address),
      Web3.to_checksum_address(pair.token_out.address),
      amount
    )

    gas_limit = function.estimate_gas({ "from": self.owner_wallet.address })

    tx = function.build_transaction({
      "from": self.owner_wallet.address,
      "nonce": self.web3.eth.get_transaction_count(self.owner_wallet.address),
      "gas": gas_limit,
      "gasPrice": self.web3.eth.gas_price
    })

    tx_hash = self.web3.eth.send_raw_transaction(self.owner_wallet.sign_transaction(tx).rawTransaction)

    self.web3.eth.wait_for_transaction_receipt(tx_hash)

  def arbitrage(self, pair_in: Pair, pair_out: Pair, amount: int):
    function = self.contract.functions.arbitrage(
      Web3.to_checksum_address(pair_in.router.get_arbitrage_address()),
      Web3.to_checksum_address(pair_out.router.get_arbitrage_address()),
      Web3.to_checksum_address(pair_in.token_in.address),
      Web3.to_checksum_address(pair_out.token_in.address),
      amount
    )

    gas_limit = function.estimate_gas({ "from": self.owner_wallet.address })

    tx = function.build_transaction({
      "from": self.owner_wallet.address,
      "nonce": self.web3.eth.get_transaction_count(self.owner_wallet.address),
      "gas": gas_limit,
      "gasPrice": self.web3.eth.gas_price
    })

    tx_hash = self.web3.eth.send_raw_transaction(self.owner_wallet.sign_transaction(tx).rawTransaction)

    self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
  def arbitrage_with_min_income(self, pair_in: Pair, pair_out: Pair, amount: int, min_income: int):
    function = self.contract.functions.arbitregeWithMinIncome(
      Web3.to_checksum_address(pair_in.router.get_arbitrage_address()),
      Web3.to_checksum_address(pair_out.router.get_arbitrage_address()),
      Web3.to_checksum_address(pair_in.token_in.address),
      Web3.to_checksum_address(pair_out.token_in.address),
      amount,
      min_income
    )

    gas_limit = function.estimate_gas({ "from": self.owner_wallet.address })

    tx = function.build_transaction({
      "from": self.owner_wallet.address,
      "nonce": self.web3.eth.get_transaction_count(self.owner_wallet.address),
      "gas": gas_limit,
      "gasPrice": self.web3.eth.gas_price
    })

    tx_hash = self.web3.eth.send_raw_transaction(self.owner_wallet.sign_transaction(tx).rawTransaction)

    self.web3.eth.wait_for_transaction_receipt(tx_hash)

  def convert(self, pair: Pair, amount: int) -> int:
    function = self.contract.functions.convert(
      Web3.to_checksum_address(pair.router.get_convert_address()),
      Web3.to_checksum_address(pair.token_in.address),
      Web3.to_checksum_address(pair.token_out.address),
      amount
    )

    return function.call({ "from": self.owner_wallet.address })

  def available(self, pair: Pair) -> bool:
    function = self.contract.functions.available(
      Web3.to_checksum_address(pair.router.get_available_address()),
      Web3.to_checksum_address(pair.token_in.address),
      Web3.to_checksum_address(pair.token_out.address)
    )

    available = function.call({ "from": self.owner_wallet.address })
    
    if not available:
      print(f"{str(pair)} is not available")

    return available
  
  def withdraw(self, token: Token, amount: int):
    function = self.contract.functions.withdraw(
      Web3.to_checksum_address(token.address),
      amount
    )

    gas_limit = function.estimate_gas({ "from": self.owner_wallet.address })

    tx = function.build_transaction({
      "from": self.owner_wallet.address,
      "nonce": self.web3.eth.get_transaction_count(self.owner_wallet.address),
      "gas": gas_limit,
      "gasPrice": self.web3.eth.gas_price
    })

    tx_hash = self.web3.eth.send_raw_transaction(self.owner_wallet.sign_transaction(tx).rawTransaction)

    self.web3.eth.wait_for_transaction_receipt(tx_hash)

  def withdraw_all(self):
    function = self.contract.functions.withdrawAll()

    gas_limit = function.estimate_gas({ "from": self.owner_wallet.address })

    tx = function.build_transaction({
      "from": self.owner_wallet.address,
      "nonce": self.web3.eth.get_transaction_count(self.owner_wallet.address),
      "gas": gas_limit,
      "gasPrice": self.web3.eth.gas_price
    })

    tx_hash = self.web3.eth.send_raw_transaction(self.owner_wallet.sign_transaction(tx).rawTransaction)

    self.web3.eth.wait_for_transaction_receipt(tx_hash)

  def flash_loan_arbitrage(self, pair_in: Pair, pair_out: Pair, amount: int):
    function = self.contract.functions.flashLoanArbitrage(
      Web3.to_checksum_address(pair_in.router.get_arbitrage_address()),
      Web3.to_checksum_address(pair_out.router.get_arbitrage_address()),
      Web3.to_checksum_address(pair_in.token_in.address),
      Web3.to_checksum_address(pair_out.token_in.address),
      amount
    )

    gas_limit = function.estimate_gas({ "from": self.owner_wallet.address })

    tx = function.build_transaction({
      "from": self.owner_wallet.address,
      "nonce": self.web3.eth.get_transaction_count(self.owner_wallet.address),
      "gas": gas_limit,
      "gasPrice": self.web3.eth.gas_price
    })

    tx_hash = self.web3.eth.send_raw_transaction(self.owner_wallet.sign_transaction(tx).rawTransaction)

    self.web3.eth.wait_for_transaction_receipt(tx_hash)

  def flash_loan_arbitrage_with_min_income(self, pair_in: Pair, pair_out: Pair, amount: int, min_income: int):
    function = self.contract.functions.flashLoanArbitrageWithMinIncome(
      Web3.to_checksum_address(pair_in.router.get_arbitrage_address()),
      Web3.to_checksum_address(pair_out.router.get_arbitrage_address()),
      Web3.to_checksum_address(pair_in.token_in.address),
      Web3.to_checksum_address(pair_out.token_in.address),
      amount,
      min_income
    )

    gas_limit = function.estimate_gas({ "from": self.owner_wallet.address })

    tx = function.build_transaction({
      "from": self.owner_wallet.address,
      "nonce": self.web3.eth.get_transaction_count(self.owner_wallet.address),
      "gas": gas_limit,
      "gasPrice": self.web3.eth.gas_price
    })

    tx_hash = self.web3.eth.send_raw_transaction(self.owner_wallet.sign_transaction(tx).rawTransaction)

    self.web3.eth.wait_for_transaction_receipt(tx_hash)

  def get_gas_fees_of_flash_loan_arbitrage_with_min_income(self, pair_in: Pair, pair_out: Pair, amount: int, min_income: int) -> int:
    function = self.contract.functions.flashLoanArbitrageWithMinIncome(
      Web3.to_checksum_address(pair_in.router.get_arbitrage_address()),
      Web3.to_checksum_address(pair_out.router.get_arbitrage_address()),
      Web3.to_checksum_address(pair_in.token_in.address),
      Web3.to_checksum_address(pair_out.token_in.address),
      amount,
      min_income
    )

    gas_limit = function.estimate_gas({ "from": self.owner_wallet.address })

    return self.web3.eth.gas_price * gas_limit

  def decimals_of(self, token: Token) -> int:
    function = self.contract.functions.decimalsOf(
      Web3.to_checksum_address(token.address)
    )
    
    return function.call({ "from": self.owner_wallet.address })