import pandas as pd
from zipline.data import bundles
from zipline.pipeline import Pipeline, USEquityPricingLoader, SimplePipelineEngine
from zipline.pipeline.data import USEquityPricing
from zipline.utils.events import calendars

# if you want to run this script in the quantopian ipython env, you should run these follow code.The zipline do not
# open source the pipeline code, so we must use the SimplePipelineEngine replace pipeline

# from quantopian.pipeline import Pipeline
# from quantopian.pipeline.data import USEquityPricing
# from quantopian.pipeline.factors import SimpleMovingAverage
# from quantopian.research import run_pipeline
#
#
# def make_pipeline():
#     latest = USEquityPricing.close.latest
#     return Pipeline(columns={'latest': latest})
#
#
# pipe = make_pipeline()
# result = run_pipeline(pipe, '2017-01-01', '2017-01-01')
# df = result.sort_values(by = ['latest'],axis = 0, ascending = False)

bundle_data = bundles.load('quandl')

pipeline_loader = USEquityPricingLoader(
    bundle_data.equity_daily_bar_reader,
    bundle_data.adjustment_reader,
)

engine = SimplePipelineEngine(
    get_loader=pipeline_loader,
    calendar=bundle_data.equity_daily_bar_reader.trading_calendar.all_sessions,
    asset_finder=bundle_data.asset_finder,
)

# the pipe get all symbols close price
pipe = Pipeline(
    columns={
        'price': USEquityPricing.close.latest,
    }
)

result = engine.run_pipeline(
    pipe,
    pd.Timestamp('2018-09-28', tz='utc'),
    pd.Timestamp('2018-09-28', tz='utc')
)

df = result.sort_values(by=['close'], axis=0, ascending=False)
print(df)
