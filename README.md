## 1. zipline安装

1. 安装anconda，选择python版本为3.5的anconda（安装路径不要有space）

2. 创建python3.5环境（如果基础python为3.5，可以步骤可以省略，如果不是3.5，就必须执行2步骤，再执行3步骤）
	conda create -n env_zipline python=3.5
	
3. 安装zipline，conda install -c Quantopian zipline

## 2. 下载数据包

	export QUANDL_API_KEY=4ciBEtymVGPThfvdJvuJ  
	# Key从www.quandl.com注册获取
	 
	zipline ingest -b csvdir
	zipline ingest -b quandl
	zipline ingest -b quantopian-quandl
	
	zipline bundles
	# 检查是否安装成功
    csvdir 2018-09-29 12:12:12.707336
    quandl 2018-09-29 11:58:27.612201
    quantopian-quandl 2018-09-30 06:30:56.953876
	
### 3. 检查工具包

	conda list zipline  
    conda list ta-lib 
    # 可能需要手动安装ta-lib: conda install -c quantopian ta-lib  
    conda list pandas 
    conda list seaborn

	# 安装tushare，可选
	#conda install -c waditu tushare
	# 检验安装是否成功  
	# conda list tushare  

### 4. 运行zipline

#### 4.1. Pycharm运行
1. Pycharm中使用Anaconda如果存在多个版本的python，需要点击Add local选择具体的python解析器

2. 运行实例

		from datetime import datetime
		import pandas as pd
		from zipline import run_algorithm

		start = pd.Timestamp(datetime(2018, 1, 1, tzinfo=pytz.UTC))
		end = pd.Timestamp(datetime(2018, 7, 25, tzinfo=pytz.UTC))

		run_algorithm(start=start,
					  end=end,
					  initialize=initialize,
					  capital_base=100000,
					  handle_data=handle_data,
					  before_trading_start=before_trading_start,
					  data_frequency='daily')
					  
3. 如果直接在源码内写代码，ide工程内根路径要到zipline这一级

4. 运行实例时，zipline会自动检查数据是否为最新，存在可更新数据会自动更新
			  
#### 5. 脚本运行
		
		zipline run -f ../../zipline/examples/buyapple.py --start 2000-1-1 --end 2014-1-1 -o buyapple_out.pickle
		
### 6. 运行架构
    
    python + mongodb/HDF5) + tensorflow

### 7. 其他开源框架

| 项目名称   |      项目用途      |  
|:----------:|:-------------:|
| zipline |  量化回测框架 | 
| tushare |  财经数据接口包   | 
| vn.py | 交易平台开发框架 |   
| rqalpha |  量化交易框架 | 
| abu |    量化交易框架   |   
| easytrader | 交易平台开发框架 | 
| pyecharts | 图表框架 |