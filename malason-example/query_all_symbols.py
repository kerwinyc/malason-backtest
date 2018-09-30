from datetime import datetime

import pytz
from zipline import run_algorithm
from zipline.api import sid
from zipline.data import bundles


# query NYSE exchange all symbols. if you want other exchange stocks ,you can change the default exchange
def initialize(context):
    bundle_data = bundles.load('quandl')
    sids = bundle_data.asset_finder.sids
    symbols = [sid(item) for item in sids]


if __name__ == '__main__':
    capital_base = 10000
    start = datetime(2015, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2018, 9, 29, 0, 0, 0, 0, pytz.utc)

    # 运行算法
    result = run_algorithm(start=start, end=end, initialize=initialize,
                           capital_base=capital_base, bundle='quandl')
