from flask import render_template, session, redirect, url_for, Flask, request, flash, jsonify
from numpy.core.multiarray import ndarray

from . import rqalpha
from .forms import StrategyForm
import os
from multiprocessing import Process
from rqalpha import run_code
from .. import db
from ..models import Role, User, Strategy
from flask_login import login_required, current_user
import pickle as pk
import numpy as np
import time
import datetime
name = None


@rqalpha.route('/result/<strategyname>', methods=['GET', 'POST'])
@login_required
def result(strategyname):
    global name
    form = StrategyForm()
    name = None
    if request.method == 'GET':
        form.name.data = strategyname
        strategy = Strategy.query.filter_by(strategyname=strategyname, author=current_user._get_current_object()).first_or_404()
        form.start_date.data = strategy.startdate
        form.end_date.data = strategy.enddate
        form.stock.data = strategy.stock
        form.source_code.data = strategy.code

    else:
        if form.validate_on_submit():
            text = form.source_code.data
            name = form.name.data
            start_date = form.start_date.data
            end_date = form.end_date.data
            stock = form.stock.data

            if form.save_strategy.data == True:
                strategy = Strategy.query.filter_by(strategyname=name, author=current_user._get_current_object()).first()
                if strategy is not None:
                    db.session.delete(strategy)
                    db.session.commit()
                    db.session.add(Strategy(strategyname=name, startdate=start_date, enddate=end_date, stock=stock, code=text, author=current_user._get_current_object()))
                    db.session.commit()
                else:
                    strategy = Strategy(strategyname=name, startdate=start_date, enddate=end_date, stock=stock, code=text, author=current_user._get_current_object())
                    db.session.add(strategy)
                    db.session.commit()
                flash('Your strategy has been saved successfully.')
            for i in range(20):
                my_file = 'C:/Users/wmy_sz/Desktop/uicquant4/app/static/test-result/'+name+str(i-1)
                if os.path.exists(my_file):
                    os.remove(my_file)
            p = Process(target=k_strategy, args=(text, name, datetime.datetime.strftime(start_date, "%Y-%m-%d"), datetime.datetime.strftime(end_date, "%Y-%m-%d"), stock))
            p.start()
    return render_template('rqalpha/result.html', form=form)


@rqalpha.route('/result', methods=['GET', 'POST'])
@login_required
def new_result():
    code = """
# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。

# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    context.s1 = "000001.XSHE"
    # 实时打印日志
    logger.info("Interested at stock: " + str(context.s1))

# before_trading此函数会在每天交易开始前被调用，当天只会被调用一次
def before_trading(context, bar_dict):
    pass


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑javascript:void(0)

    # bar_dict[order_book_id] 可以拿到某个证券的bar信息
    # context.portfolio 可以拿到现在的投资组合状态信息

    # 使用order_shares(id_or_ins, amount)方法进行落单

    # TODO: 开始编写你的算法吧！
    order_shares(context.s1, 1000)
"""
    form = StrategyForm()
    global name
    name = None
    if form.validate_on_submit():
        text = form.source_code.data
        name = form.name.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        stock = form.stock.data

        if form.save_strategy.data == True:
            strategy = Strategy.query.filter_by(strategyname=name, author=current_user._get_current_object()).first()
            if strategy is not None:
                db.session.delete(strategy)
                db.session.commit()
                db.session.add(Strategy(strategyname=name, startdate=start_date, enddate=end_date, stock=stock, code=text, author=current_user._get_current_object()))
                db.session.commit()
            else:
                strategy = Strategy(strategyname=name, startdate=start_date, enddate=end_date, stock=stock, code=text, author=current_user._get_current_object())
                db.session.add(strategy)
                db.session.commit()
            flash('Your strategy has been saved successfully.')
        for i in range(20):
            my_file = 'C:/Users/wmy_sz/Desktop/uicquant4/app/static/test-result/'+name+str(i-1)
            if os.path.exists(my_file):
                os.remove(my_file)
        p = Process(target=k_strategy, args=(text, name, datetime.datetime.strftime(start_date, "%Y-%m-%d"), datetime.datetime.strftime(end_date, "%Y-%m-%d"), stock))
        p.start()
    else:
        form.source_code.data = code
        form.start_date.data = datetime.date(2016,1,4)
        form.end_date.data = datetime.date(2016,10,4)
        form.stock.data = 1000000
    return render_template('rqalpha/result.html', form=form)





def k_strategy(code, filename, start_date, end_date, account_stock, benchmark="000300.XSHG"):
    config = {"base": {"start_date": start_date, "end_date": end_date, "benchmark": benchmark,
                       "accounts": {"stock": account_stock}},
              "extra": {"log_level": "verbose", },
              "mod": {"sys_analyser": {"enabled": True,
                                        "output_file": "C:/Users/wmy_sz/Desktop/uicquant4/app/static/test-result/" + filename }}}
                                       #"plot_save_file": "C:/Users/17600/Desktop/uicquant3/app/static/test-result/" + filename ,


    run_code(code, config)


def query_db(p):
    try:
        with open('C:/Users/wmy_sz/Desktop/uicquant4/app/static/test-result/'+name+str(p), 'rb') as f:
            m = pk.load(f)
    except FileNotFoundError:
        with open('C:/Users/wmy_sz/Desktop/uicquant4/app/static/test-result/'+name+str(p-1), 'rb') as f:
            m = pk.load(f)
    return m


# noinspection PyGlobalUndefined
@rqalpha.route("/result/weather", methods=["GET", "POST"])
def weather():
    if name != None:
        if request.method == "GET":
            time.sleep(2)
            form = StrategyForm()
            print(form.name.data)
            m = query_db(p=1)
            summary = m['summary']
            total_returns = summary['total_returns']
            annualized_returns = summary['annualized_returns']
            benchmark_total_returns = summary['benchmark_total_returns']
            benchmark_annualized_returns = summary['benchmark_annualized_returns']
            sharpe = summary['sharpe']

            portfolio_1 = m['portfolio'][0:300]
            benchmark_portfolio = m['benchmark_portfolio'][0:300]
            date = [i for i in portfolio_1.unit_net_value.index]
            v1 = [i for i in portfolio_1.unit_net_value.values - 1]
            v2 = [i for i in benchmark_portfolio.unit_net_value.values - 1]

            portfolio = m['portfolio'][:300]
            index = portfolio.index
            portfolio_value = portfolio.unit_net_value * portfolio.units
            xs = portfolio_value.values
            rt = portfolio.unit_net_value.values
            xs_max_accum = np.maximum.accumulate(xs)
            max_dd_end = np.argmax(xs_max_accum / xs)
            if max_dd_end == 0:
                max_dd_end = len(xs) - 1
            tmp = (xs - xs_max_accum)[max_dd_end:]
            max_dd_start = np.argmax(xs[:max_dd_end]) if max_dd_end > 0 else 0
            max_ddd_start_day = max_dd_start
            max_ddd_end_day = len(xs) - 1 if tmp.max() < 0 else np.argmax(tmp) + max_dd_end

            max_dd_info = "MaxDD  {}~{}, {} days".format(str(index[max_dd_start]), str(index[max_dd_end]),
                                                         (index[max_dd_end] - index[max_dd_start]).days)
            max_ddd_info = "MaxDDD {}~{}, {} days".format(str(index[max_ddd_start_day]), str(index[max_ddd_end_day]),
                                                          (index[max_ddd_end_day] - index[max_ddd_start_day]).days)

        if request.method == "POST":
            
            p = int(request.form['nm'])
            print(p)
            m = query_db(p)
            i = (int(request.form['id']))
            print(i)
            summary = m['summary']
            total_returns = summary['total_returns']
            annualized_returns = summary['annualized_returns']
            benchmark_total_returns = summary['benchmark_total_returns']
            benchmark_annualized_returns = summary['benchmark_annualized_returns']
            sharpe = summary['sharpe']

            portfolio_1 = m['portfolio'][i:i + 300]
            benchmark_portfolio = m['benchmark_portfolio'][i:i + 300]
            date = [i for i in portfolio_1.unit_net_value.index]
            v1 = [i for i in portfolio_1.unit_net_value.values - 1]
            v2 = [i for i in benchmark_portfolio.unit_net_value.values - 1]

            portfolio = m['portfolio'][:i + 300]
            index = portfolio.index
            portfolio_value = portfolio.unit_net_value * portfolio.units
            xs = portfolio_value.values
            rt = portfolio.unit_net_value.values
            xs_max_accum = np.maximum.accumulate(xs)
            max_dd_end = np.argmax(xs_max_accum / xs)
            if max_dd_end == 0:
                max_dd_end = len(xs) - 1
            tmp = (xs - xs_max_accum)[max_dd_end:]
            max_dd_start = np.argmax(xs[:max_dd_end]) if max_dd_end > 0 else 0
            max_ddd_start_day = max_dd_start
            max_ddd_end_day = len(xs) - 1 if tmp.max() < 0 else np.argmax(tmp) + max_dd_end

            max_dd_info = "MaxDD  {}~{}, {} days".format(str(index[max_dd_start]), str(index[max_dd_end]),
                                                         (index[max_dd_end] - index[max_dd_start]).days)
            max_ddd_info = "MaxDDD {}~{}, {} days".format(str(index[max_ddd_start_day]), str(index[max_ddd_end_day]),
                                                          (index[max_ddd_end_day] - index[max_ddd_start_day]).days)
            my_file = 'C:/Users/wmy_sz/Desktop/uicquant4/app/static/test-result/'+name+str(p-1)
            if os.path.exists(my_file):
                os.remove(my_file)
    else:
        date = []
        v1 = []
        v2 = []
        total_returns = ""
        annualized_returns = ""
        benchmark_total_returns = ""
        benchmark_annualized_returns = ""
        sharpe = ""
        max_dd_info = ""
        max_ddd_info = ""

    return jsonify(month=date,
                   evaporation=v1,
                   precipitation=v2,
                   total_returns = total_returns,
                   annualized_returns = annualized_returns,
                   benchmark_total_returns = benchmark_total_returns,
                   benchmark_annualized_returns = benchmark_annualized_returns,
                   sharpe = sharpe,
                   maxDD=max_dd_info,
                   maxDDD=max_ddd_info)  # 返回json格式
