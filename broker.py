# import PySimpleGUI as sg
import ccxt,time
import pandas as pd
from utils.cfg import Settings
from utils.logger import Lgr
from datetime import datetime
tfmt = '%m.%d %H:%M:%S'


class Broker():
    def __init__(self):
        self._bn = ccxt.binance({
            'timeout': 6000,
            'enableRateLimit': True
        })
        self.sym_infos = {} # sym format: BTCUSDT 
        self.all_equ = {}
        self.all_valid_pos = {}
        self.all_trade_pos = {}
        self.brokers = {}
        self._fetch_symbol_info()
        for acct in Settings['accts']:
            self.brokers[acct['name']] = ccxt.binance({
                'apiKey': acct['apiKey'],
                'secret': acct['secret'],
                'timeout': 6000,
                'enableRateLimit': True
            })
        Lgr.log('update','bn brokers inited')

    def fetch_symbol_price(self,symbol):
        try:
            return self._bn.fapiPublic_get_ticker_price({'symbol':symbol})
        except Exception as e:
            Lgr.log('ERROR', f"fetch price err:{e}")
    
    def _fetch_symbol_info(self):        
        ex_infos = self._bn.fapiPublic_get_exchangeinfo()
        for info in ex_infos['symbols']:
            self.sym_infos[info['symbol']] = {
                'pp': int(info['pricePrecision']),
                'qp': int(info['quantityPrecision'])
            }

    def fetch_all_equ(self):
        for acct in Settings['accts']:
            broker = self.brokers[acct['name']]
            balance = broker.fapiPrivate_get_balance()
            balance = pd.DataFrame(balance)
            acct_equ = float(balance[balance['asset'] == 'USDT']['balance'])
            self.all_equ[acct['name']] = round(acct_equ,2)
        
    def fetch_porders(self,acct_name):
        all_porders = []
        for coin in Settings['coins']:
            sym = coin+'USDT'
            porders = self.brokers[acct_name].fapiPrivate_get_openorders({'symbol':sym})
            all_porders += porders
            time.sleep(0.2)
        for order in all_porders:
            del order['workingType']
            del order['priceProtect']
            del order['time']
            del order['updateTime']
            del order['timeInForce']
            del order['cumQuote']
            del order['closePosition']
            order['账户'] = acct_name
            # order['clientOrderId'] = order['clientOrderId'][:12]
        return all_porders

    def fetch_forders(self,acct_name,limit=30):
        all_forders = []
        for coin in Settings['coins']:
            sym = coin+'USDT'
            porders = self.brokers[acct_name].fapiPrivate_get_allorders(
                {'symbol':sym,"limit":limit}
            )
            all_forders += porders
            time.sleep(0.2)
        valid_forders = []
        for order in all_forders:
            if order['status'] != 'FILLED': continue
            del order['workingType']
            del order['priceProtect']
            del order['time']
            # del order['updateTime']
            del order['timeInForce']
            del order['cumQuote']
            del order['closePosition']
            ts = order['updateTime']/1000
            order['成交时间'] = datetime.fromtimestamp(ts).strftime(tfmt)
            order['账户'] = acct_name
            valid_forders.append(order)
            # order['clientOrderId'] = order['clientOrderId'][:12]
        return valid_forders

    def fetch_postion(self,acct_name):
        all_pos = self.brokers[acct_name].fapiPrivate_get_positionrisk()
        all_trade_pos = []
        valid_pos = []
        for pos in all_pos:
            bn_syms = [coin+'USDT' for coin in Settings['coins']]
            if pos['symbol'] in bn_syms:
                all_trade_pos.append(pos)
            psd = pos['positionSide']
            amt = float(pos['positionAmt'])
            if pos['symbol'] in bn_syms and psd!='BOTH' and amt!=0: 
                if pos['marginType'] == 'cross':
                    Lgr.log('bnews',f"账户: {acct_name}, {pos['symbol']} 是全仓模式")
                    print(pos)
                    continue
                del pos['markPrice']
                del pos['liquidationPrice']
                del pos['maxNotionalValue']
                del pos['isAutoAddMargin']
                pnlr = float(pos['unRealizedProfit'])/float(pos['isolatedMargin'])
                pos['浮盈'] = f'{round(pnlr*100,2)}%'
                pos['账户'] = acct_name
                valid_pos.append(pos)
        self.all_valid_pos[acct_name] = valid_pos
        self.all_trade_pos[acct_name] = all_trade_pos
        return valid_pos

    ############################### 
    def place_order(self, acct_name, param):
        try:
            if not Settings['trading']['order_allowed']: 
                msg = f'({data}) bn order is not allowed in config.'
                Lgr.log('bnews',msg)
                return {
                    'clientOrderId': None,
                    'orderId': None
                }

            brkr = self.brokers[acct_name]
            return brkr.fapiPrivate_post_order(param)
        except Exception as e:
            Lgr.log('ERROR',e)
            return {
                'clientOrderId': None,
                'orderId': None
            }

    #####################################################################
    def cancel_porder(self,acct_name,param):
        brkr = self.brokers[acct_name]
        try:
            return brkr.fapiPrivate_delete_order(param)
        except Exception as e:
            Lgr.log('ERROR',e)
brkrs = Broker()

