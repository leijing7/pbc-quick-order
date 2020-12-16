
import pandas as pd

# acct
acct_df = pd.read_csv('utils/acct.csv')
Accts = acct_df.reset_index().to_dict(orient='records')
Accts = list(filter(lambda x: x['online'], Accts))

Settings = {
    "app": 'sg1',
    "v": '1.4.2',
    "trading": {
        "order_allowed": True
    },

    'accts': Accts, #账户信息
    "coins": ['BTC','ETH','UNI','LINK','BCH','DOT','LTC','EOS'], #交易币种
    "margin_ratio": ['1%', '2%', '5%', '10%', '15%','20%'], #保证金使用比例
    "levs": [2,5,10,15,20,30],#杠杆倍数
    "close_ratio": ['25%','50%','75%','100%'], #平已有仓位比例
    "slippage": 3e-3, #赢半价格计算是增加的滑点
    "filled_cnt": 15, #打印最近的成交订单数目，最多30笔

    "log_level": "TRACE"
}