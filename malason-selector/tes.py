from datetime import datetime

import numpy as np
import pandas as pd
import pytz
from zipline import run_algorithm
from zipline.api import sid
from zipline.data import bundles
from zipline.pipeline import Pipeline
from zipline.pipeline.data import Column
from zipline.pipeline.data import DataSet
from zipline.pipeline.data import USEquityPricing
from zipline.pipeline.engine import SimplePipelineEngine
from zipline.pipeline.filters import StaticAssets
from zipline.pipeline.loaders import USEquityPricingLoader
from zipline.pipeline.loaders.frame import DataFrameLoader
from zipline.utils.calendars import get_calendar

trading_calendar = get_calendar('NYSE')
bundle_data = bundles.load('quandl')


# Set up Custom Data Source for two sids for DataFrameLoader
class MyDataSet(DataSet):
    column_A = Column(dtype=float)
    column_B = Column(dtype=bool)


def initialize(context):
    dates = pd.date_range('2018-01-01', '2018-09-28')
    # assets = bundle_data.asset_finder.lookup_symbols(['A', 'AAL'], as_of_date=None)
    # assets = bundle_data.asset_finder
    sids = bundle_data.asset_finder.sids
    assets = [sid(item) for item in sids]

    # The values for Column A will just be a 2D array of numbers ranging from 1 -> N.
    column_A_frame = pd.DataFrame(
        data=np.arange(len(dates) * len(assets), dtype=float).reshape(len(dates), len(assets)),
        index=dates,
        columns=sids,
    )

    # Column B will always provide True for 0 and False for 1.
    column_B_frame = pd.DataFrame(data={sids[0]: True, sids[1]: False}, index=dates)

    loaders = {
        MyDataSet.column_A: DataFrameLoader(MyDataSet.column_A, column_A_frame),
        MyDataSet.column_B: DataFrameLoader(MyDataSet.column_B, column_B_frame),
    }

    def my_dispatcher(column):
        return loaders[column]

    # Set up pipeline engine

    # Loader for pricing
    pipeline_loader = USEquityPricingLoader(
        bundle_data.equity_daily_bar_reader,
        bundle_data.adjustment_reader,
    )

    def choose_loader(column):
        if column in USEquityPricing.columns:
            return pipeline_loader
        return my_dispatcher(column)

    engine = SimplePipelineEngine(
        get_loader=choose_loader,
        calendar=trading_calendar.all_sessions,
        asset_finder=bundle_data.asset_finder,
    )

    p = Pipeline(
        columns={
            'price': USEquityPricing.close.latest,
            'col_A': MyDataSet.column_A.latest,
            'col_B': MyDataSet.column_B.latest
        },
        screen=StaticAssets(assets)
    )

    df = engine.run_pipeline(
        p,
        pd.Timestamp('2016-01-07', tz='utc'),
        pd.Timestamp('2016-01-07', tz='utc')
    )

    df = df.sort_values(by=['price'], axis=0, ascending=False)

    print(df)


if __name__ == '__main__':
    capital_base = 10000
    start = datetime(2015, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2018, 9, 29, 0, 0, 0, 0, pytz.utc)

    # 运行算法
    result = run_algorithm(start=start, end=end, initialize=initialize,
                           capital_base=capital_base, bundle='quandl')
