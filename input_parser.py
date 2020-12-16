from utils.cfg import Settings
from utils.logger import Lgr
from utils.tool import get_op
from output import output

### 界面 事件，输入值 解析
def get_valid_accts(values):
    valid_accts = []
    for acct in Settings['accts']:
        if values['acct-'+acct['name']]:
            valid_accts.append(acct['name'])
    return valid_accts

def get_mr(values):
    for mr in Settings['margin_ratio']:
        if values['mr-'+mr]:
            return mr
def get_lev(values):
    for lev in Settings['levs']:
        if values[f'lev-{lev}']:
            return lev
        elif values[f'lev-0']:
            return 0
def get_cr(values):
    for cr in Settings['close_ratio']:
        if values[f'cr-{cr}']:
            return cr
def get_order_param(event,values):
    estrs = event.split('-')
    coin = estrs[1]
    op_ch = get_op(estrs[2]) # operation: ol,os,cl,cs
    vas = get_valid_accts(values) # acct list
    mr = get_mr(values)
    lev = get_lev(values)
    sym = f"{coin}USDT"
    if lev == 0: 
        lev_str = ''
        for v in vas:
            lev_str += f"{v}-{output.levs[v][sym]}; "
    else:
        lev_str = lev
    cr = get_cr(values) # close position ratio
    price_str = '市价' if not values[f"{coin}-p"] else values[f"{coin}-p"]
    if event[-2] == 'o':
        pstr1 = f"操作账户: {vas} \n\n交易对: {sym} \n\n方向: {op_ch} \n\n保证金使用比例: {mr}"
        pstr2 = f" \n\n杠杆倍数: {lev_str}\n\n价格: {price_str}\n"
        pstr = pstr1+pstr2
        param = {
            'symbol': sym,
            'side': 'BUY' if event[-1]=='l' else 'SELL',
            'positionSide': 'LONG' if event[-1]=='l' else 'SHORT',
            'vas': vas,
            'mr': mr,
            'lev': lev,
            'op': estrs[2],
            'price': price_str
        }
    if event[-2] == 'c':
        pstr = f"操作账户: {vas} \n\n交易对: {sym} \n\n方向: {op_ch} \n\n关仓比例: {cr}\n\n价格: {price_str}\n"
        param = {
            'symbol': sym,
            'side': 'SELL' if event[-1]=='l' else 'BUY',
            'positionSide': 'LONG' if event[-1]=='l' else 'SHORT',
            'vas': vas,
            'cr': cr,
            'op': estrs[2],
            'price': price_str
        }
    return pstr,param

def get_plan_order_param(event,values):
    estrs = event.split('-')
    coin = estrs[1]
    op_ch = get_op(estrs[2]) # operation: ol,os,cl,cs
    vas = get_valid_accts(values) # acct list

    price = values[f"{coin}-stp"]
    if not price:
        Lgr.log('bnews','必须设置止损价')
        return None,None

    pstr = f"操作账户: {vas} \n\n币: {coin} \n\n方向: {op_ch} \n\n止损价格: {price}\n"
    param = {
        'symbol': f"{coin}USDT",
        'side': 'SELL' if event[-1]=='l' else 'BUY',
        'positionSide': 'LONG' if event[-1]=='l' else 'SHORT',
        'vas': vas,
        'op': estrs[2],
        'price': price
    }

    return pstr,param