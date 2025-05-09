
import ccxt
import logging
from typing import List, Dict
import asyncio

class ArbitrageService:
    def __init__(self):
        self.exchanges = {}
        self.logger = logging.getLogger(__name__)
        self.supported_exchanges = ['coinex', 'mexc', 'bitget']
    
    def add_exchange(self, name: str, api_key: str, secret: str) -> bool:
        try:
            if name.lower() not in self.supported_exchanges:
                return False
            exchange_class = getattr(ccxt, name.lower())
            self.exchanges[name] = exchange_class({
                'apiKey': api_key,
                'secret': secret,
                'enableRateLimit': True
            })
            return True
        except Exception as e:
            self.logger.error(f"Error adding exchange: {e}")
            return False

    async def detect_opportunities(self, symbol: str) -> List[Dict]:
        opportunities = []
        prices = {}
        
        for name, exchange in self.exchanges.items():
            try:
                ticker = await exchange.fetch_ticker(symbol)
                prices[name] = {
                    'bid': ticker['bid'],
                    'ask': ticker['ask']
                }
            except Exception as e:
                self.logger.error(f"Error fetching price from {name}: {e}")
                continue

        for buy_ex in prices:
            for sell_ex in prices:
                if buy_ex != sell_ex:
                    buy_price = prices[buy_ex]['ask']
                    sell_price = prices[sell_ex]['bid']
                    profit = (sell_price - buy_price) / buy_price * 100
                    
                    if profit > 0.5:  # Min 0.5% profit
                        opportunities.append({
                            'symbol': symbol,
                            'buy_exchange': buy_ex,
                            'sell_exchange': sell_ex,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'profit_percent': profit
                        })
        
        return opportunities

    async def validate_trade(self, opportunity: Dict) -> Dict:
        try:
            buy_ex = self.exchanges[opportunity['buy_exchange']]
            sell_ex = self.exchanges[opportunity['sell_exchange']]
            
            # Verificar depósitos y retiros
            currency = opportunity['symbol'].split('/')[0]
            
            buy_currencies = await buy_ex.fetch_currencies()
            sell_currencies = await sell_ex.fetch_currencies()
            
            if currency not in buy_currencies or currency not in sell_currencies:
                return {'valid': False, 'reason': 'Currency not supported'}
                
            if not buy_currencies[currency].get('deposit', True):
                return {'valid': False, 'reason': f'Deposits disabled on {buy_ex.id}'}
                
            if not sell_currencies[currency].get('withdraw', True):
                return {'valid': False, 'reason': f'Withdrawals disabled on {sell_ex.id}'}
            
            # Verificar tarifas
            buy_fees = buy_ex.fees.get('trading', {}).get('maker', 0.1) / 100
            sell_fees = sell_ex.fees.get('trading', {}).get('taker', 0.1) / 100
            withdrawal_fee = sell_currencies[currency].get('fee', 0)
            
            total_fees = (buy_fees + sell_fees + withdrawal_fee)
            expected_profit = opportunity['profit_percent'] / 100
            
            if total_fees >= expected_profit:
                return {'valid': False, 'reason': 'Fees exceed potential profit'}
            
            # Check balances and limits
            buy_balance = await buy_ex.fetch_balance()
            sell_balance = await sell_ex.fetch_balance()
            
            return buy_balance['free']['USDT'] > 10 and sell_balance['free'][opportunity['symbol'].split('/')[0]] > 0
        except Exception as e:
            self.logger.error(f"Error validating trade: {e}")
            return False

    async def execute_trade(self, opportunity: Dict) -> bool:
        try:
            buy_ex = self.exchanges[opportunity['buy_exchange']]
            sell_ex = self.exchanges[opportunity['sell_exchange']]
            
            # Execute trades
            buy_order = await buy_ex.create_market_buy_order(
                opportunity['symbol'],
                10/opportunity['buy_price']  # Buy $10 worth
            )
            
            if buy_order['status'] == 'closed':
                sell_order = await sell_ex.create_market_sell_order(
                    opportunity['symbol'],
                    buy_order['amount']
                )
                return sell_order['status'] == 'closed'
            
            return False
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return False
