from quantopian.algorithm import attach_pipeline, pipeline_output, order_optimal_portfolio
from quantopian.pipeline import Pipeline
from quantopian.pipeline.factors import CustomFactor
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.data import Fundamentals
import quantopian.optimize as opt
from sklearn import preprocessing
from quantopian.pipeline.experimental import risk_loading_pipeline
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.data.psychsignal import stocktwits

import numpy as np

MAX_GROSS_EXPOSURE = 1.0
MAX_POSITION_SIZE = 0.01


def make_factors():
    class MessageSum(CustomFactor):
        inputs = [USEquityPricing.high, USEquityPricing.low, USEquityPricing.close, stocktwits.bull_scored_messages,
                  stocktwits.bear_scored_messages, stocktwits.total_scanned_messages]
        window_length = 5

        def compute(self, today, assets, out, high, low, close, bull, bear, total):
            v = np.nansum((high - low) / close, axis=0)
            out[:] = preprocess(v * np.nansum(total * (bear - bull), axis=0))

    class fcf(CustomFactor):
        inputs = [Fundamentals.fcf_yield]
        window_length = 1

        def compute(self, today, assets, out, fcf_yield):
            out[:] = preprocess(np.nan_to_num(fcf_yield[-1, :]))

    class Direction(CustomFactor):
        inputs = [USEquityPricing.open, USEquityPricing.close]
        window_length = 21

        def compute(self, today, assets, out, open, close):
            p = (close - open) / close
            out[:] = preprocess(np.nansum(-p, axis=0))

    class mean_rev(CustomFactor):
        inputs = [USEquityPricing.high, USEquityPricing.low, USEquityPricing.close]
        window_length = 30

        def compute(self, today, assets, out, high, low, close):
            p = (high + low + close) / 3

            m = len(close[0, :])
            n = len(close[:, 0])

            b = np.zeros(m)
            a = np.zeros(m)

            for k in range(10, n + 1):
                price_rel = np.nanmean(p[-k:, :], axis=0) / p[-1, :]
                wt = np.nansum(price_rel)
                b += wt * price_rel
                price_rel = 1.0 / price_rel
                wt = np.nansum(price_rel)
                a += wt * price_rel

            out[:] = preprocess(b - a)

    class volatility(CustomFactor):
        inputs = [USEquityPricing.high, USEquityPricing.low, USEquityPricing.close, USEquityPricing.volume]
        window_length = 5

        def compute(self, today, assets, out, high, low, close, volume):
            vol = np.nansum(volume, axis=0) * np.nansum(np.absolute((high - low) / close), axis=0)
            out[:] = preprocess(-vol)

    class growthscore(CustomFactor):
        inputs = [Fundamentals.growth_score]
        window_length = 1

        def compute(self, today, assets, out, growth_score):
            out[:] = preprocess(growth_score[-1, :])

    class peg_ratio(CustomFactor):
        inputs = [Fundamentals.peg_ratio]
        window_length = 1

        def compute(self, today, assets, out, peg_ratio):
            out[:] = preprocess(-1.0 / peg_ratio[-1, :])

    return {
        'MessageSum': MessageSum,
        'FCF': fcf,
        'Direction': Direction,
        'mean_rev': mean_rev,
        'volatility': volatility,
        'GrowthScore': growthscore,
        'PegRatio': peg_ratio,
    }


def make_pipeline():
    universe = QTradableStocksUS()

    factors = make_factors()

    combined_alpha = None
    for name, f in factors.iteritems():
        if combined_alpha == None:
            combined_alpha = f(mask=universe)
        else:
            combined_alpha += f(mask=universe)

    pipe = Pipeline(columns={
        'combined_alpha': combined_alpha,
    },
        screen=universe)
    return pipe


def initialize(context):
    attach_pipeline(make_pipeline(), 'long_short_equity_template')
    attach_pipeline(risk_loading_pipeline(), 'risk_loading_pipeline')

    # Schedule my rebalance function
    schedule_function(func=rebalance,
                      date_rule=date_rules.every_day(),
                      time_rule=time_rules.market_open(minutes=60),
                      half_days=True)
    # record my portfolio variables at the end of day
    schedule_function(func=recording_statements,
                      date_rule=date_rules.every_day(),
                      time_rule=time_rules.market_close(),
                      half_days=True)

    set_commission(commission.PerShare(cost=0, min_trade_cost=0))
    set_slippage(slippage.FixedSlippage(spread=0))


def before_trading_start(context, data):
    context.pipeline_data = pipeline_output('long_short_equity_template')
    context.risk_loading_pipeline = pipeline_output('risk_loading_pipeline')


def recording_statements(context, data):
    record(num_positions=len(context.portfolio.positions))
    record(leverage=context.account.leverage)


def rebalance(context, data):
    pipeline_data = context.pipeline_data

    # demean and normalize
    combined_alpha = pipeline_data.combined_alpha - pipeline_data.combined_alpha.mean()
    combined_alpha = combined_alpha / combined_alpha.abs().sum()

    objective = opt.MaximizeAlpha(combined_alpha)

    constraints = []

    constraints.append(opt.MaxGrossExposure(MAX_GROSS_EXPOSURE))

    constraints.append(opt.DollarNeutral())

    constraints.append(
        opt.PositionConcentration.with_equal_bounds(
            min=-MAX_POSITION_SIZE,
            max=MAX_POSITION_SIZE
        ))

    # risk_model_exposure = opt.experimental.RiskModelExposure(
    #     context.risk_loading_pipeline,
    #     version=opt.Newest,
    # )

    # constraints.append(risk_model_exposure)

    order_optimal_portfolio(
        objective=objective,
        constraints=constraints,
    )


def preprocess(a):
    a = np.nan_to_num(a - np.nanmean(a))

    return preprocessing.scale(a)