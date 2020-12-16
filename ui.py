import PySimpleGUI as sg
from utils.cfg import Settings
from trader import Trader
trader = Trader()
from utils.logger import Lgr
from output import output
from input_parser import get_order_param
from input_parser import get_plan_order_param

sg.theme('DarkAmber')   
big_font = "Helvetica 25"
mid_font = "Helvetica 20"
sml_font = "Helvetica 15"


########################################################################################################
############## 界面元素 #############

# 账户信息
acct_cb_list = [sg.Text('账号:', font=mid_font)]
for acct in Settings['accts']:
    item = sg.Checkbox(f"{acct['name']}", default=True, key=f"acct-{acct['name']}", font=mid_font)
    acct_cb_list.append(item)

# 下单参数设置
# 开仓数值比例
mr_radios = [sg.Text('开仓保证金比:')]
for mr in Settings['margin_ratio']:
    dft = True if mr=='5%' else False
    mr_radios.append(sg.Radio(mr, 'mr', default=dft, font=mid_font, key=f'mr-{mr}'))

# 杠杆设置
lv_radios = [sg.Text('开仓杠杆倍数:')]
for lev in Settings['levs']:
    # dft = True if lev==10 else False
    lv_radios.append(sg.Radio(lev, 'lev', default=False, font=mid_font, key=f"lev-{lev}"))
lv_radios.append(sg.Radio('现有', 'lev', default=True, font=mid_font, key="lev-0"))

# 平仓比例
cr_radios = [sg.Text('平当前仓比例:')]
for cr in Settings['close_ratio']:
    dft = True if cr=='50%' else False
    cr_radios.append(sg.Radio(cr, 'cr', default=dft, font=mid_font, key=f"cr-{cr}"))

# 开关仓位按钮
open_btn_list = []
for coin in Settings['coins']:
    item = [
        sg.Input(key=f'{coin}-p',size=(9,1),font=sml_font),
        sg.Text('     ',font=sml_font),
        sg.B(f'{coin} 开多',border_width=2,size=(8,1),button_color=("white","green"),font=sml_font,key=f'oc-{coin}-ol'), 
        sg.B(f'{coin} 开空',border_width=2,size=(8,1),button_color=("white","darkmagenta"),font=sml_font,key=f'oc-{coin}-os'), 
        sg.Text('     ',font=sml_font),
        sg.B(f'{coin} 平多',border_width=2,size=(8,1),button_color=("red",sg.theme_background_color()), font=sml_font, key=f'oc-{coin}-cl'), 
        sg.B(f'{coin} 平空',size=(8,1),button_color=("green",sg.theme_background_color()),font=sml_font, key=f'oc-{coin}-cs'), 
        sg.Text('     ',font=sml_font),
        sg.B('挂单',size=(4,1),button_color=("orange",sg.theme_background_color()),font=sml_font,key=f'print_porders_{coin}'),
    ]
    open_btn_list.append(item)

# 止盈止损按钮
close_btn_list = []
for coin in Settings['coins']:
    item = [
        sg.Input(key=f'{coin}-stp',size=(9,1),font=sml_font),sg.Text('     ',font=sml_font),
        sg.B(f'{coin}(多) 止盈止损',border_width=2,size=(14,1),button_color=("white","brown"),font=sml_font,key=f'plan1-{coin}-cl'),
        sg.Button(f'(多) 止损', size=(8,1),button_color=("pink",sg.theme_background_color()),font=sml_font,key=f'plan2-{coin}-cl'),
        sg.B(f'{coin}(空) 止盈止损',border_width=2,size=(14,1),button_color=("white","teal"),font=sml_font,key=f'plan1-{coin}-cs'),
        sg.Button(f'(空) 止损', size=(8,1),button_color=("lightgreen",sg.theme_background_color()),font=sml_font,key=f'plan2-{coin}-cs'),
    ]
    close_btn_list.append(item)

# 总体界面布局
layout = [  
    acct_cb_list,
    [sg.Text('_'*100)],
    mr_radios,
    [sg.Text('经常变动某个币种的杠杆会影响少许下单效率',text_color='teal')],
    lv_radios, 
    cr_radios,
    [sg.Text('_'*100)],
    [sg.T('不填价格即为市价单',text_color='teal')],
    *open_btn_list,
    [sg.T('_'*100)],
    *close_btn_list,
    [sg.Text('_'*100)],
    [
        sg.Input(key=f'cancel_idxs',size=(12,1),font=sml_font),
        sg.Text('     ',font=sml_font),
        sg.B('取消当前订单',size=(10,1),font=sml_font,key='cancel_porders'),
        sg.Text('多个索引号请用空格隔开     ',text_color='teal'),
    ],
    [sg.Text('_'*100)],
    [sg.Text('打印所有账号的信息，其中打印两类订单耗时较久',text_color='teal')],
    [
        sg.B('打印余额',size=(8,1),font=sml_font,key='print_bal'),
        sg.Text('     ',font=sml_font),
        sg.B('打印仓位',size=(8,1),font=sml_font,key='print_pos'),
        sg.Text('     ',font=sml_font),
        sg.B('仓位&杠杆',size=(9,1),font=sml_font,key='print_lev'),
        sg.Text('     ',font=sml_font),
        sg.B('打印挂单',size=(8,1),font=sml_font,key='print_porders'),
        sg.Text('     ',font=sml_font),
        sg.B('打印已成交单',size=(10,1),font=sml_font,key='print_forders')
    ],
    [sg.Text('     ',font=sml_font)]
]

####################################################################################
# 主线程循环
Lgr.log('status', f"version: {Settings['v']}")
output.print_bal()
output.print_pos()
output.print_lev()
window = sg.Window('超级下单王', layout)
while True:
    event, values = window.read()
    ########## print info #########
    if event == 'print_bal':
        output.print_bal()
    if event == 'print_pos':
        output.print_pos()
    if event == 'print_lev':
        output.print_pos()
        output.print_lev()
    if event == 'print_porders':
        output.print_porders()
    if event == 'print_forders':
        output.print_forders()
    if event and 'print_porders_' in event:
        coin = event.split('_')[-1]
        sym = f"{coin}USDT"
        output.print_sym_porders(sym)
    ###############################

    # 开关仓单
    if event and 'oc' in event: 
        pstr,param  = get_order_param(event, values)
        res = sg.popup_yes_no(pstr, title='开关仓', font=sml_font)
        if res == 'Yes' and param['op'] in ['ol','os']:  
            trader.create_pos(param)
        if res == 'Yes' and param['op'] in ['cl','cs']:
            trader.close_pos(param)

    # 止盈止损单
    if event and 'plan' in event: 
        pstr,param  = get_plan_order_param(event, values)
        # 止损only
        if pstr and 'plan2' in event:
            res = sg.popup_yes_no(pstr, title='只执行止损', font=sml_font)
            if res == 'Yes':  
                trader.create_stop_order(param)
                Lgr.log('update',"止损单发送完成！(plan2)")
        # 止盈止损
        if pstr and 'plan1' in event: 
            res = sg.popup_yes_no(pstr, title='止盈止损', font=sml_font)
            if res == 'Yes':  
                trader.create_stop_order(param)
                trader.create_pfhl_order(param)
                Lgr.log('update',"止盈止损单发送完成！(plan1)")
    
    # 按索引号取消挂单
    if event and event == 'cancel_porders':
        if output.curr_showing_porder_df.empty:
            Lgr.log('bnews','必须先打印账户信息')   
        elif not values['cancel_idxs']:
            Lgr.log('bnews','没有输入索引号')
        else:
            trader.cancel_porders(output.curr_showing_porder_df, values['cancel_idxs'])
            Lgr.log('update',f"取消挂单的索引号: {values['cancel_idxs']}")

    # if user closes window
    if event == sg.WIN_CLOSED:
        break
window.close()
