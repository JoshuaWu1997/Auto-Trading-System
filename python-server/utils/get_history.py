'''
@File   :get_history.py
@Author :JohsuaWu1997
@Date   :2020/1/31
'''

import tushare as ts
import pandas as pd

codes = ['sh000016', 'sh600000', 'sh600009', 'sh600016', 'sh600028', 'sh600030', 'sh600031', 'sh600036', 'sh600048',
         'sh600050', 'sh600104', 'sh600196', 'sh600276', 'sh600309', 'sh600340', 'sh600519', 'sh600547', 'sh600585',
         'sh600690', 'sh600703', 'sh600837', 'sh600887', 'sh601012', 'sh601066', 'sh601088', 'sh601111', 'sh601138',
         'sh601166', 'sh601186', 'sh601211', 'sh601236', 'sh601288', 'sh601318', 'sh601319', 'sh601328', 'sh601336',
         'sh601390', 'sh601398', 'sh601601', 'sh601628', 'sh601668', 'sh601688', 'sh601766', 'sh601818', 'sh601857',
         'sh601888', 'sh601939', 'sh601988', 'sh601989', 'sh603259', 'sh603993']
hist = ts.get_hist_data('sh000016')['close']
data = pd.DataFrame(index=hist.index.values, columns=codes)
for code in codes:
    hist = ts.get_hist_data(code)['close']
    data[code].loc[hist.index] = hist.values
    print(data)

data.to_csv('history_5.csv')
