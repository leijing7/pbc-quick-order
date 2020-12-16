from utils.logger import Lgr
from broker import brkrs
from utils.tool import get_op
from datetime import datetime
import base62
from utils.cfg import Settings
app = Settings['app']

class Trader():
    def __init__(self): pass

    def _set_lev(self, acct_name, data):
        sym = data['symbol']
        for pos in brkrs.all_trade_pos[acct_name]:
            if pos['symbol'] == sym:
                if data['lev'] and float(pos['leverage']) != data['lev']:
                    brkrs.brokers[acct_name].fapiPrivate_post_leverage({
                        'symbol': sym,
                        'leverage': data['lev']
                    })
                    Lgr.log('gnews',f"账户 {acct_name} {sym} 杠杆从 {pos['leverage']} 变更为 {data['lev']}")
                return

    def create_pos(self, data):
        sym = data['symbol']
        if data['price'] == '市价':
            res = brkrs.fetch_symbol_price(sym)
            price = float(res['price'])
            order_type = 'MARKET'
        else:
            price = float(data['price']) #fix price
            order_type = 'LIMIT'
        for an in data['vas']:
            self._set_lev(an, data)
            acct_equ = brkrs.all_equ[an]
            margin_rate = float(data['mr'][:-1])/100
            margin = acct_equ*margin_rate
            quote = margin*float(data['lev'])
            qp = brkrs.sym_infos[sym]['qp']
            qty = round(quote/price,qp)
            qty = max(qty,1/pow(10,qp))

            rstr = base62.encode(int(datetime.now().timestamp()))
            param = {
                'symbol': sym,
                'side': data['side'],
                'positionSide': data['positionSide'],
                'type': order_type,
                'quantity': qty,
                'newClientOrderId': f"{app}_{data['op']}_{rstr}", 
            }
            if order_type == 'LIMIT': 
                param['price'] = price
                param['timeInForce'] = 'GTC'
            res = brkrs.place_order(an, param)
            if res['orderId']:
                op_ch = get_op(data['op'])
                Lgr.log(data['op'],f"账户:{an} {op_ch}: {param}")
            else:
                Lgr.log('ERROR','place order has error')

    def close_pos(self, data):
        sym = data['symbol']
        if data['price'] == '市价':
            res = brkrs.fetch_symbol_price(sym)
            price = float(res['price'])
            order_type = 'MARKET'
        else:
            price = float(data['price']) #fix price
            order_type = 'LIMIT'
        for an in data['vas']:
            qp = brkrs.sym_infos[sym]['qp']
            close_rate = float(data['cr'][:-1])/100
            pos_amt = 0
            for pos in brkrs.all_valid_pos[an]:
                if pos['symbol'] == sym and pos['positionSide'] == data['positionSide']:
                    pos_amt = float(pos['positionAmt'])
            if not pos_amt:
                Lgr.log('bnews', f'账户 {an} 没有找到对应仓位')
                return
            qty = round(abs(pos_amt)*close_rate,qp)
            qty = max(qty,1/pow(10,qp))
            rstr = base62.encode(int(datetime.now().timestamp()))
            param = {
                'symbol': sym,
                'side': data['side'],
                'positionSide': data['positionSide'],
                'type': order_type,
                'quantity': qty,
                'newClientOrderId': f"{app}_{data['op']}_{rstr}", 
            }
            if order_type == 'LIMIT': 
                param['price'] = price
                param['timeInForce'] = 'GTC'
            res = brkrs.place_order(an, param)
            if res['orderId']:
                op_ch = get_op(data['op'])
                Lgr.log(data['op'],f"账户:{an} {op_ch}: {param}")
            else:
                Lgr.log('ERROR','place order has error')


    def cancel_porders(self, porder_df, idxs):
        for idx in idxs.split(' '):
            order = porder_df.iloc[int(idx)]
            param = {
                "symbol": order['symbol'],
                "orderId": order['orderId']
            }
            res = brkrs.cancel_porder(order['账户'],param)
            if res and res['orderId']:
                Lgr.log('SUCCESS',f"撤销订单 {res['symbol']} {res['clientOrderId']} 成功")


    def create_stop_order(self, data):
        sym = data['symbol']
        for an in data['vas']:
            rstr = base62.encode(int(datetime.now().timestamp()))
            param = {
                'symbol': sym,
                'side': data['side'],
                'positionSide': data['positionSide'],
                'type': 'STOP_MARKET',
                'newClientOrderId': f"{app}_stplos_{rstr}", 
                'stopPrice': data['price'],
                'closePosition': True,
                'workingType': 'MARK_PRICE'
            }
            res = brkrs.place_order(an, param)
            if res['orderId']:
                op_ch = get_op(data['op'])
                Lgr.log(data['op'],f"账户:{an} {op_ch}: {param}")
            else:
                Lgr.log('ERROR','place order has error')

    # 下 LIMIT 止盈单
    def create_pfhl_order(self, data):
        stp_p = float(data['price'])
        sym = data['symbol']
        pside = data['positionSide']
        
        for an in data['vas']:
            pp = brkrs.sym_infos[sym]['pp']
            qp = brkrs.sym_infos[sym]['qp']
            close_rate = 0.5
            pos_amt = 0
            brkrs.fetch_postion(an)
            for pos in brkrs.all_valid_pos[an]:
                if pos['symbol'] == sym and pos['positionSide'] == pside:
                    pos_amt = float(pos['positionAmt'])
                    entry_p = float(pos['entryPrice'])
            if not pos_amt:
                Lgr.log('bnews', f"账户 {an} {sym} 没有 {pside} 仓位")
                continue
            if pside == 'LONG':
                price = round(abs(entry_p-stp_p)+entry_p*(1+Settings['slippage']),pp)
            else:
                price = round(entry_p*(1-Settings['slippage'])-abs(entry_p-stp_p),pp)
            qty = round(abs(pos_amt)*close_rate,qp)
            qty = max(qty,1/pow(10,qp))
            rstr = base62.encode(int(datetime.now().timestamp()))
            param = {
                'symbol': sym,
                'side': data['side'],
                'positionSide': pside,
                'price': price,
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': qty,
                'newClientOrderId': f"{app}_{data['op']}_{rstr}", 
            }
            res = brkrs.place_order(an, param)
            if res['orderId']:
                op_ch = get_op(data['op'])
                Lgr.log(data['op'],f"账户:{an} {op_ch}: {param}")
            else:
                Lgr.log('ERROR','place order has error')



    # def _get_ot(self,param):
    #     if param['side']=='BUY' and param['positionSide']=='LONG':
    #         ot = 'ol'
    #     if param['side']=='SELL' and param['positionSide']=='SHORT':
    #         ot = 'os'
    #     if param['side']=='BUY' and param['positionSide']=='SHORT':
    #         ot = 'cs'
    #     if param['side']=='SELL' and param['positionSide']=='LONG':
    #         ot = 'cl'
    #     return ot