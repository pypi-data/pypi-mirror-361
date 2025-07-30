import tushare as ts
import pandas as pd
import akshare as ak
import re

 
class stockAPIAkShare:
    def __init__(self):
        pass
    # 板块
    def get_board_list(self):
        """_获取板块概念列表
        排名	int64	-
        板块名称	object	-
        板块代码	object	-
        最新价	float64	-
        涨跌额	float64	-
        涨跌幅	float64	注意单位：%
        总市值	int64	-
        换手率	float64	注意单位：%
        上涨家数	int64	-
        下跌家数	int64	-
        领涨股票	object	-
        领涨股票-涨跌幅	float64	注意单位：%
        """
        stock_board_concept = ak.stock_board_concept_name_em()
        stock_board_industry = ak.stock_board_industry_name_em()
        return pd.concat([stock_board_concept, stock_board_industry], axis=0)
    
    def get_board_pe_ratio(self,board_name,date ):
        """_行业市盈率
        变动日期          行业分类  行业层级  ... 静态市盈率-加权平均 静态市盈率-中位数  静态市盈率-算术平均
        """
        return  ak.stock_industry_pe_ratio_cninfo(symbol= board_name, date=date)
    
    def get_board_contain_stock(self,board_name):
        """_获取板块成分股列表
        名称	类型	描述
        序号	int64	-
        代码	object	-
        名称	object	-
        最新价	float64	-
        涨跌幅	float64	注意单位: %
        涨跌额	float64	-
        成交量	float64	注意单位: 手
        成交额	float64	-
        振幅	float64	注意单位: %
        最高	float64	-
        最低	float64	-
        今开	float64	-
        昨收	float64	-
        换手率	float64	注意单位: %
        市盈率-动态	float64	-
        市净率	float64	-
      """
    # 板块成分
        stock_board_concept  = ak.stock_board_concept_cons_em(symbol=board_name)
        if stock_board_concept is not None:
            return stock_board_concept
        stock_board_industry  = ak.stock_board_industry_cons_em(symbol=board_name)
        return stock_board_industry
    
    def get_ticket(self,ts_code):
    # 盘口
        stock_bid = ak.stock_bid_ask_em(symbol=ts_code)
        return stock_bid
    
    def get_minute_history(self,ts_code,start_date,end_date,period='1'):
        # 分时数据
        # period='1'; 获取 1, 5, 15, 30, 60 分钟的数据频率
        # "2024-03-20 09:30:00"
        stock_zh_a_hist_min = ak.stock_zh_a_hist_min_em(symbol=ts_code, start_date=start_date, end_date=end_date, period="1", adjust="qfq")
        return stock_zh_a_hist_min

    # 分时数据-新浪
    # period='1'; 获取 1, 5, 15, 30, 60 分钟的数据频率
    # stock_zh_a_minute_df = ak.stock_zh_a_minute(symbol='sh600751', period='1', adjust="qfq")
    # 分时数据-东财
    # 注意：该接口返回的数据只有最近一个交易日的有开盘价，其他日期开盘价为 0
    def get_minute(self,ts_code,period='1'):
    # 日内分时数据-东财
        stock_intraday = ak.stock_intraday_em(symbol=ts_code)
        return stock_intraday
    
    def get_today_list(self):
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        return stock_zh_a_spot_em_df
    
    def get_daily_by_code_list(self,ts_codes,start_date='', end_date=''):
        retdata =None
        #根据回车或换行符切割
        codelist = re.split(',|;',ts_codes)
        for code in codelist:
            if code.strip():
                data = self.get_daily_by_code(code.strip(),start_date, end_date)
                if data is not None:
                    if retdata is None:
                        retdata = data
                    else:
                        retdata =pd.concat([retdata,data],axis=0)
        return retdata
 
        
    def get_daily_by_code(self,ts_code,start_date='', end_date=''):
        columns = { '日期':'date',
                    '股票代码':'code',
                    '开盘':'open',
                    '收盘':'close',
                    '最高':'high',
                    '最低':'low',
                    '成交量':'volume',
                    '成交额':'amount',
                    # '振幅':'pct_chg',
                    # '涨跌幅',
                    # '涨跌额',
                    # '换手率'
                    }
        # period='daily'; choice of {'daily', 'weekly', 'monthly'}
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=ts_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        stock_zh_a_hist_df.rename(columns=columns, inplace=True)
        return stock_zh_a_hist_df

    def get_code_list(self):
        """_获取股票列表

        Returns:
            code	object	-
         name	object
        """
        stock_info = ak.stock_info_a_code_name()
        return stock_info
    
    def get_basic_data(self,tscode):
        """_获取股票基本信息
        Returns:
            code	object	-
         name	object
        """
        stock_a_indicator = ak.stock_a_indicator_lg(symbol=tscode)
        # stock_a_indicator = ak.stock_value_em(symbol=tscode)
        return stock_a_indicator
    
    
    def get_basic_gdhs_by_date(self,date):
        """股东户数，按日期"""
        stock_zh_a_gdhs_df = ak.stock_zh_a_gdhs(symbol=date) #每个季度末最后一天
        return stock_zh_a_gdhs_df
        
    def get_basic_gdhs_by_code(self,tscode):
        """股东户数，按股票代码,包含历史数据"""
        stock_zh_a_gdhs_detail_em_df = ak.stock_zh_a_gdhs_detail_em(symbol=tscode)
        return stock_zh_a_gdhs_detail_em_df
    
        
    def get_basic_holders_top10_by_date(self,date):
        """股东持股分析-十大股东"""
        stock_gdfx_holding_analyse_em_df = ak.stock_gdfx_holding_analyse_em(date=date)
        return stock_gdfx_holding_analyse_em_df
    
    def get_basic_holders_top10_by_code(self,tscodde,date):
        """十大股东(个股)"""
        stock_gdfx_top_10_em_df = ak.stock_gdfx_top_10_em(symbol=tscodde, date=date)
        return stock_gdfx_top_10_em_df
    
      
    # 财务指标
#     stock_financial_analysis_indicator_df = ak.stock_financial_analysis_indicator(symbol="600004", start_year="2020")
    def get_basic_institute_hold_list(self,quarter):
        """_获取机构持股列表
        Args:
            quarter (str): 季度如：20201 年+季度
        Returns:
        证券代码  证券简称 机构数  机构数变化   持股比例  持股比例增幅  占流通股比例  占流通股比例增幅
            _type_: _description_dataframe
        """
        stock_institute_hold_df = ak.stock_institute_hold(symbol=quarter)
        return stock_institute_hold_df
    def get_basic_institute_hold_detail_by_stock(self,stock,quarter):
        """_获取机构持股详情
        Args:
            stock (str): 股票代码如：300033
            quarter (str): 季度如：20201 年+季度
        Returns:
        持股机构类型  持股机构代码      持股机构简称  ... 最新占流通股比例  持股比例增幅  占流通股比例增幅
            _type_: _description_dataframe
        """
        stock_institute_hold_detail_df = ak.stock_institute_hold_detail(stock=stock, quarter=quarter)
        return stock_institute_hold_detail_df
    

    def get_daily_list(self,start_date='', end_date=''):
        """_获取日期列表
        Args:
        """
        retdata =None
        #根据回车或换行符切割
        codelist=self.get_code_list()
        for code in codelist:
            if code.get('code'):
                data = self.get_daily_by_code(code.get('code'),start_date, end_date)
                if data is not None:
                    if retdata is None:
                        retdata = data
                    else:
                        retdata =pd.concat([retdata,data],axis=0)
        return retdata
    

            
        
class stockAPITuShare:
    def __init__(self,apitoken):
        self.API = ts.pro_api(apitoken)
    
    def get_daily_by_code(self,ts_code,start_date='', end_date=''):
        """_summary_

        Args:
            ts_code (_type_): 股票代码如：300033.SZ '688362.SH,600203.SH,300223.SZ,300346.SZ'
            start_date (str, optional): 开始日期：'20200102'.
            end_date (str, optional):  开始日期：'20200202'.

        Returns:
            _type_  : _description_dataframe:
            code ：代码
            date  ：交易日期 
            open   ：开盘价
            high   ：最高价 
            low    ：最低价 
            close  ：收盘价 
            pre_close ：昨收价 
            previous_close ：前收价
            change  ：涨跌额 
            pct_chg ：涨跌幅 
            volume: 成交量 
            amount ：成交额 
            
        """
        columns_en_std = {'trade_date':'date',
              'ts_code': 'code',  
              'open': 'open',
              'close': 'close', 
              'high': 'high', 
              'low': 'low', 
              'pre_close': 'pre_close',
              'change': 'change',
              'pct_chg': 'pct_chg',
              'vol': 'volume', 
              'amount': 'amount',}
        df =  self.API.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df.rename(columns=columns_en_std, inplace=True)
        # df['volume'] = df['vol'] 
        # df['amount'] = df['amount'] / 10
        # df.drop(columns=['vol'], inplace=True)
        return df
    
    def get_basic_data(self):
        """_获取股票列表

        Returns:
            _type_: _description_dataframe
        """
        df = self.API.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        return df
    
    def get_daily_list(self,start_date='', end_date=''):
        '''获取日期列表 
        '''
        data = pd.DataFrame()
        df = self.API.trade_cal(exchange='SSE', 
                                is_open='1', 
                                start_date=start_date,   #"'20200101'"
                                end_date=end_date, 
                                fields='cal_date')
        # print(df)
        for date in df['cal_date'].values:
            df1 = self.API.daily(trade_date=date) #  self.get_daily(date)
            # print(df1)
            data = pd.concat([data,df1],axis=0) # data .concat(df1)
            # print(data)
        return data
 
    @staticmethod
    def get_open_price_by_close(lastPrice,percent):
        '''
        lastPrice:收盘价
        percent：涨幅百分比
        '''
        return 100*lastPrice / (percent + 100)
if __name__ == '__main__':
    # apitoken = 'apikey'
    # stock = stockAPITuShare(apitoken)
    
    # data = stock.get_daily_by_code('600203.SH,300223.SZ',start_date='20250612', end_date='20250612')
    
    # data = stock.get_basic_data()
    # data = stock.get_daily_list(start_date='20250612', end_date='20250612')
    # print(data.head())
    
    stockak = stockAPIAkShare()
    # data = stockak.get_daily_by_code('000001',start_date='20250612', end_date='20250712')
    # data = stockak.get_board_list()
    # data=stockak.get_board_contain_stock('融资融券')
    # data=stockak.get_ticket('000001')
    # data = stockak.get_minute('000001',period='5')
    # data = stockak.get_minute_history('000001',period='1' ,start_date='20250710 08:30:00', end_date='20250712 13')
    # data = stockak.get_daily_by_code_list('000001,300222',start_date='20250612', end_date='20250712')
    # data = stockak.get_daily_by_code_list('600203,000001', '20250101', '20250704')
    # data = stockak.get_basic_data('000001')
    # data= stockak.get_institute_hold_list('20251')
    # data = stockak.get_institute_hold_detail_by_stock('000001', '20244')
    # data = stockak.get_daily_list()
    # data = stockak.get_today_list()
    data = stockak.get_basic_gdhs_by_date('20250331')
    print(data.head())
    
    