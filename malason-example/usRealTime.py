from datetime import datetime

import numpy as np
import pytz
from terminaltables import AsciiTable
from zipline import run_algorithm
from zipline.api import symbol

np.seterr(divide='ignore', invalid='ignore')

stocks = ['TSLA', 'MU']

def initialize(context):
    context.stocks = stocks


def handle_data(context, data):
    assets = [symbol(code) for code in stocks]
    current = data.current(assets, fields=['high', 'low', 'open', 'price', 'volume'])
    formater = "{0:.02f}".format
    current = current.applymap(formater)
    current.insert(0, 'code', stocks)

    head = [['code', 'high', 'low', 'open', 'price', 'volume']]
    nr = current.values.tolist()
    c = np.vstack((head, nr)).tolist()

    table = AsciiTable(c)
    print(table.table)

if __name__ == '__main__':
    capital_base = 10000
    start = datetime(2015, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2017, 9, 29, 0, 0, 0, 0, pytz.utc)

    # 运行算法
    result = run_algorithm(start=start, end=end, initialize=initialize,
                           capital_base=capital_base, handle_data=handle_data,
                           bundle='quandl')
