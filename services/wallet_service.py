
from web3 import Web3
from eth_account import Account
import ccxt
import logging
from typing import Dict

class WalletService:
    def __init__(self):
        # Multiple network support
        self.networks = {
            'eth': Web3(Web3.HTTPProvider('https://eth.llamarpc.com')),
            'bsc': Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org')),
            'polygon': Web3(Web3.HTTPProvider('https://polygon-rpc.com'))
        }
        self.logger = logging.getLogger(__name__)
        self.wallets = {}
        
    def get_network_fees(self, network: str) -> Dict:
        try:
            w3 = self.networks[network]
            gas_price = w3.eth.gas_price
            base_fee = w3.eth.get_block('latest').base_fee_per_gas
            return {
                'network': network,
                'gas_price': w3.from_wei(gas_price, 'gwei'),
                'base_fee': w3.from_wei(base_fee, 'gwei') if base_fee else 0,
                'estimated_transfer_cost': w3.from_wei(gas_price * 21000, 'ether')
            }
        except Exception as e:
            return {'error': str(e)}

    def get_token_info(self, token_address: str, network: str) -> Dict:
        try:
            w3 = self.networks[network]
            erc20_abi = [{"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},
                        {"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]
            contract = w3.eth.contract(address=token_address, abi=erc20_abi)
            return {
                'symbol': contract.functions.symbol().call(),
                'decimals': contract.functions.decimals().call()
            }
        except Exception as e:
            return {'error': str(e)}
        
    def add_dex_wallet(self, private_key: str) -> Dict:
        try:
            account = Account.from_key(private_key)
            address = account.address
            self.wallets[address] = {
                'type': 'dex',
                'private_key': private_key,
                'address': address
            }
            return {'address': address, 'success': True}
        except Exception as e:
            self.logger.error(f"Error adding DEX wallet: {e}")
            return {'success': False, 'error': str(e)}
            
    def add_cex_wallet(self, exchange: str, api_key: str, secret: str) -> Dict:
        try:
            if exchange.lower() not in ccxt.exchanges:
                return {'success': False, 'error': 'Exchange not supported'}
                
            exchange_class = getattr(ccxt, exchange.lower())
            exchange_instance = exchange_class({
                'apiKey': api_key,
                'secret': secret
            })
            
            self.wallets[f"{exchange}_{api_key[:8]}"] = {
                'type': 'cex',
                'exchange': exchange_instance,
                'api_key': api_key
            }
            return {'success': True, 'exchange': exchange}
        except Exception as e:
            self.logger.error(f"Error adding CEX wallet: {e}")
            return {'success': False, 'error': str(e)}
            
    def get_dex_balance(self, address: str) -> Dict:
        try:
            if address not in self.wallets or self.wallets[address]['type'] != 'dex':
                return {'success': False, 'error': 'Wallet not found'}
                
            balance = self.w3.eth.get_balance(address)
            return {
                'success': True,
                'balance': self.w3.from_wei(balance, 'ether'),
                'address': address
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def get_cex_balance(self, wallet_id: str) -> Dict:
        try:
            if wallet_id not in self.wallets or self.wallets[wallet_id]['type'] != 'cex':
                return {'success': False, 'error': 'Wallet not found'}
                
            exchange = self.wallets[wallet_id]['exchange']
            balance = exchange.fetch_balance()
            return {
                'success': True,
                'balance': balance['total'],
                'exchange': exchange.id
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
