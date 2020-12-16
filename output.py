import pandas as pd
from broker import brkrs
from utils.logger import Lgr
from utils.cfg import Settings

####### 打印输出账户信息 #######
class Output():
    def __init__(self):
        self.curr_showing_porder_df = pd.DataFrame()
        self.levs = {}

    def print_bal(self):
        brkrs.fetch_all_equ()
        Lgr.log('status',f"账户资金: {brkrs.all_equ}")
        print('-------------------------------------------------------------------------------')

    def print_pos(self):
        Lgr.log('alert','获取所有账户仓位:')
        all_valid_pos = []
        for acct in Settings['accts']:
            all_valid_pos += brkrs.fetch_postion(acct['name'])
        pos_df = pd.DataFrame(all_valid_pos)
        print(pos_df)
        print('-------------------------------------------------------------------------------')

    def print_lev(self):
        for acct in Settings['accts']:
            an = acct['name']
            self.levs[an] = {}
            all_pos = brkrs.all_trade_pos[an]
            for pos in all_pos:
                self.levs[an][pos['symbol']] = pos['leverage']
            Lgr.log('status',f"{an} 杠杆: {self.levs[an]}")
        print('-------------------------------------------------------------------------------')

    def print_porders(self):
        Lgr.log('ol','获取所有账户挂单:')
        all_porders = []
        for acct in Settings['accts']:
            all_porders += brkrs.fetch_porders(acct['name'])
        self.curr_showing_porder_df = pd.DataFrame(all_porders)
        print(self.curr_showing_porder_df)
        print('********************************************************************************')

    def print_sym_porders(self,sym):
        Lgr.log('ol',f'获取所有账户 {sym} 挂单:')
        all_porders = []
        for acct in Settings['accts']:
            porders = brkrs.brokers[acct['name']].fapiPrivate_get_openorders({'symbol':sym})
            for order in porders:
                del order['workingType']
                del order['priceProtect']
                del order['time']
                del order['updateTime']
                del order['timeInForce']
                del order['cumQuote']
                del order['closePosition']
                order['账户'] = acct['name']
                all_porders.append(order)
        self.curr_showing_porder_df = pd.DataFrame(all_porders)
        print(self.curr_showing_porder_df)
        print('********************************************************************************')

    def print_forders(self):
        Lgr.log('os',f"获取所有账户最近{Settings['filled_cnt']}笔成交单:")
        all_forders = []
        for acct in Settings['accts']:
            all_forders += brkrs.fetch_forders(acct['name'])
        forder_df = pd.DataFrame(all_forders)
        
        forder_df = forder_df.sort_values(by=['updateTime'],ascending=False)
        forder_df = forder_df.drop(columns=['orderId','updateTime','status'])
        print(forder_df.head(Settings['filled_cnt']))

output = Output()