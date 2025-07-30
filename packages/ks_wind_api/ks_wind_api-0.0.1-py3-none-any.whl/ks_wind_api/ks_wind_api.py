# todo 1. 对于查询的持仓，空的也要推送空的，否则orderplit无法回调.  这对于http请求很容易实现，但是如果是websocket回调，也许空的不会回调？例如ibk
# 所有的期货合约代码，主力合约是XX

import pandas as pd
from typing import Union, Optional, List
from pandas import DataFrame
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from ks_trade_api.base_fundamental_api import BaseFundamentalApi
from ks_trade_api.base_market_api import BaseMarketApi
from ks_trade_api.utility import extract_vt_symbol, generate_vt_symbol, SUB_EXCHANGE2EXCHANGE
from ks_trade_api.constant import Exchange, RET_OK, RET_ERROR, Product, RetCode, SUB_EXCHANGE2EXCHANGE, Interval, Adjustment, \
    EXCHANGE2TIMEZONE, CHINA_TZ, EXCHANGE2SUB_EXCHANGES
from ks_trade_api.object import BarData
from ks_utility.datetimes import get_date_str
from ks_utility import datetimes
from ks_utility.datetimes import DATE_FMT
import sys
import numpy as np
from decimal import Decimal
import uuid
from pathlib import Path
from xlsx2csv import Xlsx2csv
import itertools
import pytz
from dateutil.parser import parse

from logging import DEBUG, WARNING, ERROR
from ks_utility.numbers import to_decimal
from ks_utility.datetimes import get_dt_int
from enum import Enum
import traceback
import pandas as pd
import numpy as np
import typing
import re
try:
    from WindPy import w
except:
    pass

pd.set_option('future.no_silent_downcasting', True) # 关闭df = df.fillna(np.nan)的未来版本提示

class Params(Enum):
    # 下面是我们的参数
    MRYN = 'MRYN' # MRY的N值
    
    # 下面是东财的标准参数
    PriceAdj = 'PriceAdj' # 复权
    currencyType = 'currencyType' # 货币种类
    unit = 'unit' # 单位 1:元
    
# 我们的标准字段
class MarketIndicator(Enum):
    ## 行情字段
    open = 'open'
    high = 'high'
    low = 'low'
    close = 'close'
    volume = 'volume'
    turnover = 'turnover'
    turnover_rate = 'turnover_rate'
    open_interest = 'open_interest'
    total_market_cap = 'total_market_cap'
    float_market_cap = 'float_market_cap'

class Indicator(Enum):    
    ## 财务字段
    ROE = 'ROE' # 净资产收益率
    ROA = 'ROA' # 总资产收益率
    LIBILITYTOASSET = 'LIBILITYTOASSET' # 资产负债率
    DIVANNUPAYRATE = 'DIVANNUPAYRATE' # 年度股利支付率(年度现金分红比例(已宣告))
    MV = 'MV' # 总市值
    CIRCULATEMV = 'CIRCULATEMV' # 流通市值
    PE = 'PE' # 市盈率
    PETTM = 'PETTM' # PETTM
    PB = 'PB' # 市净率
    YOYOR = 'YOYOR' # 营业收入同比增长率(Year-over-Year Operating Revenue)
    YOYNI = 'YOYNI' # 净利润同步增长率(Year-over-Year Net Income)
    CAGRTOR = 'CAGRTOR' # 营业总收入复合增长率(Compound Annual Growth Rate Total Operating revenue)
    GPMARGIN = 'GPMARGIN' # 毛利率
    NPMARGIN= 'NPMARGIN' # 净利率
    DIVIDENDYIELD = 'DIVIDENDYIELD' # 股息率
    DIVIDENDYIELDTTM = 'DIVIDENDYIELDTTM' # 股息率TTM
    
    
    # 财务报表-现金流量表
    CASHFLOWSTATEMENT_NCFO = 'CASHFLOWSTATEMENT_NCFO' # 经营活动产生的现金流量净额
    
# ctr专题函数的字段
class CtrIndicator(Enum):
    FUNDCODE = 'FUNDCODE' # 基金代码
    SECUCODE = 'SECUCODE' # 股票代码
    SECUNAME = 'SECUNAME' # 股票名称
    MVRATIO = 'MVRATIO' # 股票持仓市值占比

class MyCurrency(Enum):
    CNY = 2
    USD = 3
    HKD = 4

class MyExchange(Enum):
    SH = 'SH'
    SZ = 'SZ'
    HK = 'HK'
    BJ = 'BJ'

    N = 'N'
    O = 'O'
    A = 'A'
    F = 'F'
    
    DCE = 'DCE'
    SHF = 'SHF'
    CZC = 'CZC'
    GFE = 'GFE'
    INE = 'INE'
    CFE = 'CFE'
    
    NYB = 'NYB' # ICE美国
    NYM = 'NYM' # 纽约NYMEX
    CMX = 'CMX' # 纽约COMEX
    CME = 'CME' # 芝加哥CME
    CBT = 'CBT' # 芝加哥CBOT
    IPE = 'IPE' # ICE欧洲
    LME = 'LME' # 伦敦LME
    SG = 'SG'   # 新加坡SGX
    TCE = 'TCE' # 东京TOCOM
    MDE = 'MDE' # 马来西亚BMD
    OSE = 'OSE' # Osaka Exchange，大阪交易所. 是日本的期货与衍生品交易所
    THF = 'THF' # Thailand Futures Exchange 泰国的官方金融衍生品交易所
    EUX = 'EUX'             # 欧洲期货交易所
    
MYEXCHANGE2FUTURES_SYMBOLS = {
    MyExchange.NYB: [
        'CT', # ICE2号棉花
        'SB', # ICE11号糖
        'CC', # ICE可可
        'KC', # ICE咖啡
        'OJ', # ICE冷冻浓缩橙汁
    ]
}

EXCHANGE2MY_CURRENCY = {
    Exchange.SSE: MyCurrency.CNY,
    Exchange.SZSE: MyCurrency.CNY,
    Exchange.BSE: MyCurrency.CNY,
    Exchange.SEHK: MyCurrency.HKD,
    Exchange.SMART: MyCurrency.USD
}

# EXCHANGE_KS2MY = {
#     Exchange.SSE: MyExchange.SH,
#     Exchange.SZSE: MyExchange.SZ,
#     Exchange.SEHK: MyExchange.HK,
#     Exchange.BSE: MyExchange.BJ
# }

EXCHANGE_MY2KS = {
    MyExchange.A: Exchange.AMEX,
    MyExchange.O: Exchange.NASDAQ,
    MyExchange.N: Exchange.NYSE,
    MyExchange.F: Exchange.OTC,

    MyExchange.SH: Exchange.SSE,
    MyExchange.SZ: Exchange.SZSE,
    MyExchange.BJ: Exchange.BSE,

    MyExchange.HK: Exchange.SEHK,
    
    MyExchange.DCE: Exchange.DCE,
    MyExchange.SHF: Exchange.SHFE,
    MyExchange.CZC: Exchange.CZCE,
    MyExchange.GFE: Exchange.GFEX,
    MyExchange.INE: Exchange.INE,
    MyExchange.CFE: Exchange.CFFEX,
    
    MyExchange.NYB: Exchange.NYB,
    MyExchange.NYM: Exchange.NYMEX,
    MyExchange.CMX: Exchange.COMEX,
    MyExchange.CME: Exchange.CME,
    MyExchange.CBT: Exchange.CBOT,
    MyExchange.IPE: Exchange.IPE,
    MyExchange.LME: Exchange.LME,
    MyExchange.SG: Exchange.SGX,
    MyExchange.TCE: Exchange.TOCOM,
    MyExchange.MDE: Exchange.BMD
}

EXCHANGE_KS2MY = {v:k for k,v in EXCHANGE_MY2KS.items()}

# 标准字段映射为东财字段(只有需要映射才需要定义，例如ROA就是对应ROA，不需映射)
INDICATORS_KS2MY = {
    # # ROE (chice面板上，沪深股票是ROEWA；港股是ROEAVG)
    # 'ROE.CNSE': 'ROEAVG',
    # 'ROE.SEHK': 'ROEAVG',
    # 'ROE.SMART': 'ROEAVG',
    
    # 'LIBILITYTOASSET.CNSE': 'LIBILITYTOASSETRPT',
    # 'LIBILITYTOASSET.SEHK': 'LIBILITYTOASSET',
    # 'LIBILITYTOASSET.SMART': 'LIBILITYTOASSET',

    # 'DIVANNUPAYRATE.CNSE': 'DIVANNUPAYRATE',
    # 'DIVANNUPAYRATE.SEHK': 'DIVANNUACCUMRATIO',
    # 'DIVANNUPAYRATE.SMART': 'DIVANNUACCUMRATIO',

    # 'MV.CNSE': 'MV',
    # 'MV.SEHK': 'MV',
    # 'MV.SMART': 'MV',
    
    # 'CIRCULATEMV.CNSE': 'CIRCULATEMV',
    # 'CIRCULATEMV.SEHK': 'LIQMV',
    # 'CIRCULATEMV.SMART': 'LIQMV',

    # 'PE.CNSE': 'PELYR',
    # 'PE.SEHK': 'PELYR',
    # 'PE.SMART': 'PELYR',

    # 'PB.CNSE': 'PBMRQ',
    # 'PB.SEHK': 'PBMRQ',
    # 'PB.SMART': 'PBMRQ',
    
    # 'YOYOR.CNSE': 'YOYOR',
    # 'YOYOR.SEHK': 'GR1YGROWTHRATE',
    # 'YOYOR.SMART': 'GR1YGROWTHRATE',
    
    # 'CAGRTOR.CNSE': 'CAGRGR',
    # 'CAGRTOR.SEHK': 'CAGRGR',
    # 'CAGRTOR.SMART': 'CAGRGR',
    
    # 'CASHFLOWSTATEMENT_NCFO.CNSE': 'CASHFLOWSTATEMENT_39',
    # 'CASHFLOWSTATEMENT_NCFO.SEHK': 'CASHFLOWSTATEMENT',
    # 'CASHFLOWSTATEMENT_NCFO.SMART': 'CASHFLOWSTATEMENT',
    
    # 'DIVIDENDYIELDTTM.CNSE': 'DIVIDENDYIELDY',
    # 'DIVIDENDYIELDTTM.SEHK': 'DIVIDENDYIELDY',
    # 'DIVIDENDYIELDTTM.SMART': 'DIVIDENDYIELDY',
    
    ## 下面是行情的
    MarketIndicator.open.name: 'OPEN3',
    MarketIndicator.high.name: 'HIGH3',
    MarketIndicator.low.name: 'LOW3',
    MarketIndicator.close.name: 'CLOSE3', #close3是不向前推导的收盘价，close是如果当天没有数据则向前取
    MarketIndicator.volume.name: 'VOLUME',
    MarketIndicator.turnover.name: 'AMT',
    MarketIndicator.turnover_rate.name: 'TURN',
    MarketIndicator.open_interest.name: 'OI3',
    MarketIndicator.total_market_cap.name: 'MKT_CAP_ARD',
    MarketIndicator.float_market_cap.name: 'MKT_CAP_FLOAT'
}

INDICATORS_MY2KS = {v:'.'.join(k.split('.')[:-1]) if '.' in k else k for k,v in INDICATORS_KS2MY.items()}

EXCHANGE_PRODUCT2PUKEYCODE = {
    'CNSE.EQUITY': '001071',
    'SEHK.EQUITY': '401001',
    'SMART.EQUITY': '202001004',

    'CNSE.ETF': '507001',
    'SEHK.ETF': '404004',
    'SMART.ETF': '202003009',
    
    'CNFE.FUTURES': '715001'
}

STATEMENT_EXCHANGE2ITEMS_CODE = {
    'CASHFLOWSTATEMENT.SEHK': 39,
    'CASHFLOWSTATEMENT.SMART': 28
}

#  EMI01709159 均价:氧化铝, EMM00195469 国内现货价格:批发价:苹果, EMI01763401 实物黄金:中国黄金:基础金价, EMI00240995 价格:15厘胶合板, EMI00546343 出厂价:顺丁橡胶(BR9000):独山子石化(中石油华北销售), EMI01639663 
# 现货价格:石油沥青, EMI00000271 现货价:棉花:新疆
SPOT_SYMBOL_KS2MY = {
    # 纽约NYMEX
    'USCUS_CL': 'S5111903', #  WTI原油
    'USNYC_RB': 'S5111927', # RBOB汽油
    'USNYC_HO': 'S5111930', # 取暖油
    'USHPT_NG': 'S5111047', # 天然气
    'GBSVT_BZ': 'S5111905', # 布伦特原油
    'GBLON_PL': 'S5807341', # 铂
    'GBLON_PA': 'S5807344', # 钯
    
    # COMEX
    'GBLON_GC': 'S0031645', # 黄金
    'GBLON_SI': 'S0031648', # 白银
    
    # CME 外汇加上FX前缀，区分
    'FX_EC': 'G0925982', # 欧元兑美元
    'FX_MP': 'R4127710', # 墨西哥比索兑美元
    'FX_AD': 'M0000204', # 澳元兑美元
    # 'FXCDL6': 'EMI01629229', # 加元兑美元 todo!
    # 'FXJ1L6': 'EM01629230', # 日元兑美元
    'FX_BP': 'M0000201', # 英镑兑美元
    # 'FX_SF': 'M0000202', # 瑞郎兑美元
    'FX_BR': 'Y7450233', # 巴西雷亚尔兑美元
    'FX_NE': 'M0000205', # 新西兰元兑美元
    # 'FXRMBL6': 'EMI01629233', # 人民币兑美元
    # 'FXBTCL6': 'EMI01629233', # 比特币
    # 'FXETHL6': 'EMI01629233', # 以太坊
    
    # CBOT
    # 'SL8': 'EMI01629211', # 大豆
    # 'CL8':'EMI01629212', # 玉米
    'US_W':'S5007750', # 小麦
    # 'OL8':'EMI01629214', # 燕麦
    # 'RRL8':'EMI01629214', # 稻谷
    # 'SML8':'EMI01629215', # 豆粕
    'US_BO':'S5007762', # 豆油
    
    # ICE欧洲
    # 'TL8': 'S5111903', # 轻质低硫原油
    'NLRTM_G': 'C8322686', # 柴油
    'USLAX_N': 'S5111929', # ICE NYH(RBOB)汽油
    # 'ML8': 'EMI01871292', # 天然气
    # 'NLRTM_ATW': 'S5101710', # ICE鹿特丹煤炭
    
    # 伦敦LME
    'GBLON_CA': 'S0029751', # 铜
    'GBLON_AH': 'S0029755', # 铝
    'GBLON_PB': 'S0029763', # 铅
    'GBLON_ZS': 'S0029759', # 锌
    'GBLON_NI': 'S0029771', # 镍
    'GBLON_SN': 'S0029767', # 锡
    'GBLON_ZS': 'S0029759', # 锌

    # TOCOM
    # 'THSGN_RSS3': 'S5120293', # 3号烟片胶
}
SPOT_SYMBOL_MY2KS = {v:k for k,v in SPOT_SYMBOL_KS2MY.items()}

SPOT_MY_SYMBOL2NAME = {
    # 纽约NYMEX
    'S5111925': '西德克萨斯中级轻质原油(WTI)现货离岸价', #  WTI原油
    'S5111927': '普通传统汽油(纽约港)现货价', # RBOB汽油
    'S5111930': '2号取暖油:纽约港现货价(FOB)', # 取暖油
    'S5111047': '路易斯安那州(亨利港)天然气现货价', # 天然气
    'S5111905': '原油(英国布伦特Dtd)现货价', # 布伦特原油
    'S5807341': '铂(伦敦市场)现货价', # 铂
    'S5807344': '钯(伦敦市场)现货价', # 钯
    
    # COMEX
    'S0031645': 'LME铝现货结算价', # 黄金
    'S0031648': '白银(伦敦市场)现货价', # 白银
    'S0029749': 'LME铜现货结算价', # 铜 todo 这里使用了LME铜的现货价
    'S0029755': 'LME铝现货结算价', # 铝 todo 这里使用了LME铝的现货价
    
    # CME 外汇加上FX前缀，区分
    'G0925982': '欧元兑美元(欧洲央行)汇率', # 欧元兑美元
    'R4127710': 'ICE墨西哥比索兑美元即期汇率', # 墨西哥比索兑美元
    'M0000204': '澳元兑美元(洲际交易所)汇率', # 澳元兑美元
    # 'FXCDL6': 'EMI01629229', # 加元兑美元 todo!
    # 'FXJ1L6': 'EM01629230', # 日元兑美元
    'M0000201': '英镑兑美元(洲际交易所)汇率', # 英镑兑美元
    'M0000202': '瑞郎兑美元(洲际交易所)汇率', # 瑞郎兑美元
    'Y7450233': 'ICE巴西雷亚尔兑美元即期汇率', # 巴西雷亚尔兑美元
    'M0000205': '新西兰元兑美元(洲际交易所)汇率', # 新西兰元兑美元
    # 'FXRMBL6': 'EMI01629233', # 人民币兑美元
    # 'FXBTCL6': 'EMI01629233', # 比特币
    # 'FXETHL6': 'EMI01629233', # 以太坊
    
    # CBOT
    # 'SL8': 'EMI01629211', # 大豆
    # 'CL8':'EMI01629212', # 玉米
    'S5007750': '(商务部)小麦国际现货价', # 小麦
    # 'OL8':'EMI01629214', # 燕麦
    # 'RRL8':'EMI01629214', # 稻谷
    # 'SML8':'EMI01629215', # 豆粕
    'S5007762':'(商务部)美国豆油国际现货价', # 豆油
    
    # ICE欧洲
    # 'TL8': 'S5111903', # 轻质低硫原油
    'C8322686': '欧洲ARA柴油(Gasoil.1)现货价', # 柴油
    'S5111929': '洛杉矶RBOB普通汽油现货价', # ICE NYH(RBOB)汽油
    # 'ML8': 'EMI01871292', # 天然气
    'S5101710': '欧洲ARA港动力煤现货价', # S5101710
}

def wind_data2df(data):
    df = pd.DataFrame()
    if len(data.Times) > 1:
        df_raw = pd.DataFrame(data.Data, index=data.Codes, columns=pd.to_datetime(data.Times, format='%Y%m%d').tz_localize(pytz.UTC))
        df_reset = df_raw.reset_index().rename(columns={'index': 'symbol'})
        df = df_reset.melt(id_vars='symbol', var_name='datetime', value_name='close')
    else:
        df = pd.DataFrame({'symbol': data.Codes, 'close': data.Data[0]})
        df['datetime'] = pytz.UTC.localize(datetime.combine(data.Times[0], time(0,0,0)))
    return df

def extract_my_symbol(my_symbol):
    items = my_symbol.split(".")
    try: 
        exchange = MyExchange(items[-1])
    except:
        exchange = np.nan
    symbol = '.'.join(items[:-1])
    #     else:
    #         breakpoint()
    # else:
    #     if exchange not in [MyExchange.HK]:
    #         breakpoint()
    return symbol, EXCHANGE_MY2KS.get(exchange, Exchange.UNKNOW)

def is_futures(exchange):
    my_exchanges = [
        MyExchange.SHF, MyExchange.DCE, MyExchange.CZC, MyExchange.GFE, MyExchange.INE, MyExchange.CFE,
        MyExchange.NYB, MyExchange.NYM, MyExchange.CME, MyExchange.CMX, MyExchange.CBT, MyExchange.IPE,
        MyExchange.LME, MyExchange.SG, MyExchange.TCE, MyExchange.MDE, MyExchange.OSE, MyExchange.THF,
        MyExchange.EUX
    ]
    ks_exchanges = [EXCHANGE_MY2KS.get(x, x) for x in my_exchanges]
    return exchange in my_exchanges + ks_exchanges

def symbol_ks2my(vt_symbol: str):
    if not vt_symbol:
        return ''
    symbol, ks_exchange = extract_vt_symbol(vt_symbol)
    symbol = symbol.replace('.', '_')
        
    # 港股wind是四位
    if ks_exchange in [Exchange.SEHK]:
        symbol = symbol[1:]
    
    my_symbol = generate_vt_symbol(symbol, EXCHANGE_KS2MY.get(ks_exchange))
    
    if ks_exchange == Exchange.OTC:
        my_symbol = SPOT_SYMBOL_KS2MY.get(symbol)
        
    return my_symbol

def symbol_my2ks(my_symbol: str):
    if not my_symbol:
        return ''
    symbol, my_exchange = extract_my_symbol(my_symbol)
    symbol = symbol.replace('_', '.') # 东财使用下划线，而我们根据futu的用了.
            
    # 港股wind是四位
    if my_exchange in [MyExchange.HK] and len(symbol) < 5:
        symbol = f'0{symbol}'
    
    return generate_vt_symbol(symbol, SUB_EXCHANGE2EXCHANGE.get(EXCHANGE_MY2KS.get(my_exchange, Exchange.UNKNOW)))

def symbol_my2sub_exchange(my_symbol: str):
    if not my_symbol:
        return ''
    symbol, my_exchange = extract_my_symbol(my_symbol)
    
    return EXCHANGE_MY2KS.get(my_exchange).value

# 用于mry，把为None的数据剔除，并且补齐性质
def clean_group(indicators: list[str] = [], n: int = 3):
    def fn(group):
        cleaned = pd.DataFrame()
        for col in group.columns:
            group_len = len(group)
            if col in indicators:
                # 把开头和结尾的空值都给去掉
                s = group[col].fillna(np.nan)
                start = s.first_valid_index()
                end = s.last_valid_index()
                non_na = s.loc[start:end]
                # 这里是因为某些指标没有制定日期的数据会往前滚动取数，所以导致重复，所以删除头两行一致的其中一行
                non_na = non_na.drop([x for x in non_na.duplicated()[lambda x: x].index if x < 2]) 
                series = non_na.reset_index(drop=True)
                series = series.reindex(range(len(group)))
                cleaned[col] = series
            else:
                cleaned[col] = group[col].reset_index(drop=True)
        return cleaned.head(n)
    return fn


class KsWindApi(BaseFundamentalApi):
    gateway_name: str = "KS_WIND"

    def __init__(self, setting: dict):
        dd_secret = setting.get('dd_secret')
        dd_token = setting.get('dd_token')
        gateway_name = setting.get('gateway_name', self.gateway_name)
        super().__init__(gateway_name=gateway_name, dd_secret=dd_secret, dd_token=dd_token)

        self.setting = setting
        self.login()
        
    def login(self):
        result = w.start()
        self.log(result.Data, '登录结果')

    def _normalization_indicators_input(self, indicators: str):
        indicators_list = indicators.split(',')
        indicators_new = [INDICATORS_KS2MY.get(x) for x in indicators_list]
        return ','.join(indicators_new)
    
    def _normalization_indicators_output(self, df: DataFrame):
        rename_columns = {x:INDICATORS_MY2KS[x] for x in df.columns if x in INDICATORS_MY2KS}
        return df.rename(columns=rename_columns)

    # 暂时不支持跨市场多标的，使用第一个表的市场来决定所有标的的市场
    # sub_exchange是用来做美股区分，东财
    def css(self, vt_symbols: list[str], indicators: str = '', options: str = '', sub_exchanges: list[str] = []) -> tuple[RetCode, pd.DataFrame]:
        if not vt_symbols:
            return None
        
        symbol, exchange = extract_vt_symbol(vt_symbols[0])
        indicators = self._normalization_indicators_input(indicators, exchange)

        # 默认pandas返回
        if not 'IsPandas' in options:
            options += ',IsPandas=1'

        if not 'TradeDate' in options:
            options += f',TradeDate={get_date_str()}'
        
        if not 'N=' in options: # CAGRTOR需要N参数
            options += ',N=3'    

        year = datetimes.now().year
        if not 'Year' in options:      
            options += f',Year={year}'

        if not 'PayYear' in options:
            options += f',PayYear={year}'

        if not 'ReportDate' in options:
            options += ',ReportDate=MRQ'

        if not 'CurType' in options:
            # options += f',CurType={EXCHANGE2MY_CURRENCY.get(exchange).value}'
            options += f',CurType=1' # 使用原始币种，港股-人民币

        if 'ROETTM' in indicators:
            options += ',TtmType=1'

        if 'LIBILITYTOASSETRPT' in indicators:
            options += ',Type=3' # 合并报表（调整后）
            
        if 'STATEMENT' in indicators:
            statement_matched = re.search(r'([^,]+STATEMENT\b)', indicators)
            if statement_matched:
                statement_indicator = statement_matched.groups()[0]
                ItemsCode = STATEMENT_EXCHANGE2ITEMS_CODE.get(f'{statement_indicator}.{exchange.value}')
                options += f',ItemsCode={ItemsCode}' # 合并报表（调整后）

        # if 'BPS' in indicators:
        #     options += f',CurType={EXCHANGE2MY_CURRENCY.get(exchange).value}'

        my_symbols = [symbol_ks2my(x, Exchange(sub_exchanges[i]) if len(sub_exchanges) and sub_exchanges[i] else None) for i,x in enumerate(vt_symbols)]
        df = c.css(my_symbols, indicators=indicators, options=options)
        if isinstance(df, c.EmQuantData):
            return RET_ERROR, str(df)
        
        df.reset_index(drop=False, inplace=True)

        # 转换symbol
        df['CODES'] = df['CODES'].transform(symbol_my2ks)
        df.rename(columns={'CODES': 'vt_symbol'}, inplace=True)

        # LIBILITYTOASSET: 港美的是百分号，A股是小数
        if 'LIBILITYTOASSET' in df.columns:
            is_cn = df.vt_symbol.str.endswith('.SSE') | df.vt_symbol.str.endswith('.SZSE') | df.vt_symbol.str.endswith('.CNSE')
            df.loc[is_cn, 'LIBILITYTOASSET'] = df[is_cn]['LIBILITYTOASSET'] * 100

        df = self._normalization_indicators_output(df)
        
        # 把None转为np.nan
        df = df.infer_objects(copy=False).fillna(np.nan)

        return RET_OK, df
    
    # alisa放阿飞
    css_mrq = css
    
    def _parse_options(self, options: str = '') -> dict:
        ret_options = {}
        for k,v in dict(x.strip().split('=') for x in options.split(',')).items():
            try:
                enumn_key = Params(k)
            except Exception as e:
                raise e
            ret_options[enumn_key] = v if not v.isdigit() else int(v)
        return ret_options
    
    def _generate_options(self, options: dict = {}) -> str:
        return ','.join([f'{k.name if isinstance(k, Enum) else k}={v}' for k,v in options.items()])
    
    def _parse_indicators(self, indicators: str = '', typing: typing = Enum) -> dict:
        ret_indicators = []
        for k in [x.strip() for x in indicators.split(',')]:
            if typing == str:
                key = k
            else:
                try:
                    key = Indicator(k)
                except Exception as e:
                    raise e
            ret_indicators.append(key)
        return ret_indicators
    
    def _generate_indicators(self, indicators: dict = {}) -> str:
        return ','.join([x.name if isinstance(x, Enum) else x for x in indicators])
    
    # 获取最近N年的数据例如2024-12-31, 2023-12-31, 2022-12-31
    def css_mry(self, vt_symbols: list[str], indicators: str = '', options: str = '', sub_exchanges: list[str] = []) -> pd.DataFrame:
        try:
            options = self._parse_options(options)
            n = options[Params.MRYN]
            
            # 因为年报公布延迟，年初的时候没有当年和前一年的数据，所以要取N个数据必须是N+2年
            y0 = datetimes.now().replace(month=12, day=31)
            dates = [(y0-relativedelta(years=i)).strftime(DATE_FMT) for i in range(n+2)]
            del options[Params.MRYN]
            all_df = pd.DataFrame()
            for date in dates:
                options[Params.ReportDate] = date
                options[Params.TradeDate] = date
                year = date[:4]
                options[Params.Year] = year
                options[Params.PayYear] = year
                other_options = self._generate_options(options)
                ret, df = self.css(
                    vt_symbols=vt_symbols,
                    indicators=indicators,
                    options=other_options,
                    sub_exchanges=sub_exchanges
                )
                if ret == RET_ERROR:
                    return RET_ERROR, df
                df['DATES'] = date
                all_df = pd.concat([all_df, df], ignore_index=True)

            indicators_str = self._parse_indicators(indicators, typing=str)
            all_df = all_df.fillna(np.nan)
            cleaned = all_df.groupby('vt_symbol', group_keys=False).apply(clean_group(indicators=indicators_str, n=n))
            table = cleaned.reset_index(drop=False).pivot(index='vt_symbol', columns='index', values=indicators_str)
            table.columns = [f"{col[0]}_MRY{col[1]}" for col in table.columns]
            table = table.loc[vt_symbols] # 按照传入的顺序组织顺组，因为pivot把顺序弄乱了
            table.reset_index(drop=False, inplace=True)
            return RET_OK, table
                
            
        except Exception as e:
            return RET_ERROR, traceback.format_exc()
    
    def sector(self, exchange: Exchange, products: list[Product], tradedate: str = None):
        if not tradedate:
            tradedate = get_date_str()
        # 默认pandas返回
        options = 'IsPandas=1'

        all_df = pd.DataFrame()
        for product in products:
            pukeycode = EXCHANGE_PRODUCT2PUKEYCODE.get(f'{exchange.name}.{product.name}')
            df = c.sector(pukeycode, tradedate, options)
            df['vt_symbol'] = df['SECUCODE'].transform(symbol_my2ks)
            df['sub_exchange'] = df['SECUCODE'].transform(symbol_my2sub_exchange)
            df['name'] = df['SECURITYSHORTNAME']
            df['product'] = product.name

            all_df = pd.concat([all_df, df[['vt_symbol', 'name', 'sub_exchange', 'product']]], ignore_index=True)
            
        # 如果是期货，需要增加中金所支持，东财的主力连续期货只有商品期货
        # if Product.FUTURES in products:
        #     cf_df = c.sector('701001', tradedate, options)
        #     cf_df['vt_symbol'] = cf_df['SECUCODE'].transform(symbol_my2ks)
        #     cf_df['sub_exchange'] = cf_df['SECUCODE'].transform(symbol_my2sub_exchange)
        #     cf_df['name'] = cf_df['SECURITYSHORTNAME']
        #     cf_df['product'] = product.name
        #     cf_df = cf_df[cf_df['name'].str.contains('主力连续')]
        #     all_df = pd.concat([all_df, cf_df[['vt_symbol', 'name', 'sub_exchange', 'product']]], ignore_index=True)
            
        return RET_OK, all_df
    
    def ctr(self, method: str, indicators: list[str], options: str = ''):
        try:
            CtrMethod(method)
        except:
            raise Exception(f'{method} not in CtrMethod')
            
        options_dict = self._parse_options(options)
        if not Params.ReportDate in options_dict:
            if Params.FundCode in options_dict:
                # 获取基金最新报告期
                res = c.css(options_dict[Params.FundCode], "LASTREPORTDATE", f"EndDate={get_date_str()},dataType=1")
                if not res.ErrorCode == 0:
                    raise Exception(str(res))
                options_dict[Params.ReportDate] = res.Data[options_dict[Params.FundCode]][0]
        
        if not Params.IsPandas in options_dict:
            options_dict[Params.IsPandas] = 1
        
        if not CtrIndicator.FUNDCODE.value in indicators:
            indicators += f',{CtrIndicator.FUNDCODE.value}'
            
        if not CtrIndicator.SECUCODE.value in indicators:
            indicators += f',{CtrIndicator.SECUCODE.value}'
            
        options_str = self._generate_options(options_dict)
           
        df = c.ctr(method, indicators, options_str)
        if isinstance(df, c.EmQuantData) and df.ErrorCode in [0, 10000009]:
            raise Exception(str(df))
        
        df['vt_symbol'] = df['SECUCODE'].transform(symbol_my2ks)
        
        return df
    
    def query_trading_days(self, sub_exchange: Exchange, start: str, end=str) -> DataFrame:
        if not hasattr(self, '_query_trading_days'):
            self._query_trading_days = {}
        param_key = f'{sub_exchange},{start},{end}'
        if self._query_trading_days.get(param_key):
            return self._query_trading_days.get(param_key)
        ret, df = w.tdays(start, end, f"TradingCalendar={sub_exchange.value}", usedf=True)
        if ret:
            raise Exception(df)
        tz = EXCHANGE2TIMEZONE.get(sub_exchange)
        if len(df):
            df['datetime'] = df.iloc[:, 0].dt.tz_localize('PRC').dt.tz_convert(tz)
            df['type'] = 'WHOLE'
            df['exchange'] = sub_exchange.value
        else:
            df = pd.DataFrame(columns=['datetime', 'type', 'exchange'])
        df = df.reset_index(drop=True)
        df = df.drop(df.columns[0], axis=1)
        self._query_trading_days[param_key] = df
        return self._query_trading_days[param_key]
    
    # 原始的wsd，只能传入单个标的
    def _wsd(self, vt_symbol: str, indicators: str = '', start: str = '', end: str = '', options: str = '') -> tuple[RetCode, pd.DataFrame]:
        my_symbol = symbol_ks2my(vt_symbol)
        symbol, exchange = extract_vt_symbol(vt_symbol)
        tz = pytz.UTC # 统一使用UTC时区，方便多个数据datetime的merge
        
        indicators = self._normalization_indicators_input(indicators)
        
        ret, df = w.wsd(my_symbol, indicators, start, end, options, usedf=True)
        if ret:
            raise Exception(df)
        
        df = df.reset_index(drop=False)
        df['vt_symbol'] = vt_symbol
        if not start == end:
            df['datetime'] = pd.to_datetime(df['index']).dt.tz_localize(tz)
        else:
            df['datetime'] = pd.to_datetime(start).tz_localize(tz)
        df = self._normalization_indicators_output(df)
        # rename_columns = {x: INDICATORS_MY2KS[x] for x in df.columns if x in INDICATORS_MY2KS}
        # df.rename(columns=rename_columns, inplace=True)
        df.drop(columns=['index'], inplace=True)
        first_clumn = df.columns[0]
        s = df[first_clumn].first_valid_index()
        e = df[first_clumn].last_valid_index()
        nona_df = df.loc[s:e]
        
        if s is None or e is None:
            return pd.DataFrame()
        
        return nona_df
    
    def wsd(self, vt_symbols: list[str], indicators: str = '', start: str = '', end: str = '', options: str = '') -> pd.DataFrame:
        all_df = pd.DataFrame()
        for i, vt_symbol in enumerate(vt_symbols):
            self.log(f'[{i+1}/{len(vt_symbols)}]fetching {vt_symbol}...')
            df = self._wsd(vt_symbol=vt_symbol, indicators=indicators, start=start, end=end, options=options)
            if len(df):
                all_df = pd.concat([all_df, df], ignore_index=True)
        return all_df
    
    def edb(self, vt_symbols: list[str], start: str = '', end: str = '', options: str = '') -> pd.DataFrame:
        my_symbols = [symbol_ks2my(x) for x in vt_symbols]
        
        
        data:w.WindData = w.edb(','.join(my_symbols), beginTime=start, endTime=end, options=options)
        if data.ErrorCode:
            raise Exception(data.Data)
        
        df = wind_data2df(data)
        
        symbol, sub_exchange = extract_vt_symbol(vt_symbols[0])

        
        df['symbol'] = df['symbol'].transform(lambda x: SPOT_SYMBOL_MY2KS.get(x))
        df['exchange'] = sub_exchange.name
        df['vt_symbol'] = df['symbol'] + '.' + df['exchange']
        df.drop(columns=['symbol', 'exchange'], inplace=True)
        
        start_time = pytz.UTC.localize(pd.to_datetime(start))
        end_time = pytz.UTC.localize(pd.to_datetime(end))
        
        df = df.groupby('vt_symbol').apply(lambda x: x.loc[x['close'].first_valid_index():x['close'].last_valid_index()]).reset_index(drop=True)
        
        df_filtered = df[df.datetime>=start_time][df.datetime<=end_time]
        
        return df_filtered
    
    def query_contracts(
            self,
            vt_symbols: Optional[List[str]] = None,
            exchanges: Optional[list[Exchange]] = None,
            products: Optional[List[Product]] = None,
            df: bool = True
        ) -> DataFrame:
        all_df = pd.DataFrame()
        if Product.FUTURES in products:
            ret, df = w.wset("sectorconstituent","sectorid=1000002554000000", usedf=True) # 全球主力连续和次主力连续合约
            if ret:
                raise Exception(str(df))
            if df.empty:
                return df
            df_main = df[~df.sec_name.str.contains('次活跃')]
            df_main['datetime'] = pd.to_datetime(df_main['date']).dt.tz_localize('UTC')
            df_main[['symbol', 'sub_exchange']] = df_main['wind_code'].apply(lambda x: pd.Series(extract_my_symbol(x)))
            df_main['sub_exchange'] = df_main['sub_exchange'].transform(lambda x: x.name)
            
            df_main['vt_symbol'] = df_main['symbol'] + '.' + df_main['sub_exchange']
            df_main['name'] = df_main['sec_name']
            df_main['product'] = Product.FUTURES.name
            df_main['min_volume'] = np.nan
            df_main['size'] = np.nan
            all_df = pd.concat([all_df, df_main], ignore_index=True)

        # 现货
        if Product.SPOT in products:
            spots = []
            for ks_symbol, my_symbol in SPOT_SYMBOL_KS2MY.items():
                spot_name = SPOT_MY_SYMBOL2NAME.get(my_symbol)
                spots.append({
                    'symbol': ks_symbol,
                    'exchange': Exchange.OTC.name,
                    'sub_exchange': Exchange.OTC.name,
                    'product': Product.SPOT.name,
                    'name': spot_name,
                    'min_volume': np.nan,
                    'size': np.nan
                })
            spots_df = pd.DataFrame(spots)
            spots_df['datetime'] = pytz.UTC.localize(parse('00:00:00'))
            spots_df['vt_symbol'] = spots_df['symbol'] + '.' + spots_df['sub_exchange']
            all_df = pd.concat([all_df, spots_df], ignore_index=True)
            
        # 过滤Exchanges和products
        if exchanges:
            sub_exchanges = [EXCHANGE2SUB_EXCHANGES.get(x, x) for x in exchanges]
            sub_exchanges_str = [x.name for x in itertools.chain.from_iterable(sub_exchanges)]
            all_df = all_df[all_df['sub_exchange'].isin(sub_exchanges_str)]
        
        if products:
            products_str = [x.name for x in products]
            all_df = all_df[all_df['product'].isin(products_str)]
        
        all_df.reset_index(drop=True, inplace=True)
        return all_df
        
    # 关闭上下文连接
    def close(self):
        pass
        # self.app.quit()
        # self.quote_ctx.close()
        # self.trd_ctx.close()
        
class KsWindFileApi(BaseMarketApi):
    gateway_name: str = "KS_WIND_FILE"

    def __init__(self, setting: dict):
        dd_secret = setting.get('dd_secret')
        dd_token = setting.get('dd_token')
        gateway_name = setting.get('gateway_name', self.gateway_name)
        super().__init__(gateway_name=gateway_name, dd_secret=dd_secret, dd_token=dd_token)
        
        # self.log('opening wps')
        # app = xw.App(visible=False)         # ✅ 后台模式，不弹出 Excel 窗口
        # app.interactive = False             # ✅ 非交互模式，不响应用户操作
        # app.screen_updating = False         # ✅ 不刷新界面，加快处理速度
        # app.display_alerts = False          # ✅ 不弹出警告窗口
        # self.app = app
        # self.log('wps oeped')

        self.setting = setting
        self.client_tmp: Path = Path(self.setting.get('client_tmp', r'F:\Wind\Wind.NET.Client\WindNET\tmp'))
        
    def _wsd(self, vt_symbol: str, indicators: str = '', start: str = '', end: str = '', options: str = '') -> tuple[RetCode, pd.DataFrame]:

        my_symbol = symbol_ks2my(vt_symbol=vt_symbol)
        
        xlsx_file_path = self.client_tmp.joinpath(f'{my_symbol}.xlsx')
        csv_file_path = self.client_tmp.joinpath(f'{my_symbol}.csv')
        if not xlsx_file_path.is_file():
            raise Exception(f'{xlsx_file_path} not found.')
        
        Xlsx2csv(xlsx_file_path, outputencoding="utf-8").convert(csv_file_path)
        df = pd.read_csv(csv_file_path)
        df = df[:-1] # 最后一行是wind的签名
        
        df[['symbol', 'sub_exchange']] = df['代码'].apply(lambda x: pd.Series(extract_my_symbol(x)))
        df['exchange'] = df['sub_exchange'].transform(SUB_EXCHANGE2EXCHANGE.get)
        
        df['exchange'] = df['exchange'].transform(lambda x: x.value)
        df['sub_exchange'] = df['sub_exchange'].transform(lambda x: x.value)
        df['vt_symbol'] = df['symbol'] + '.' + df['sub_exchange']
        
        symbol, exchange = extract_vt_symbol(vt_symbol)
        tz = pytz.UTC
        df['datetime'] = pd.to_datetime(df['日期']).dt.tz_localize(tz)
        # df['product'] = product.value
        # df['interval'] = interval.value
        df.rename(columns={
            '开盘价(元)': 'open', 
            '最高价(元)': 'high', 
            '最低价(元)': 'low', 
            '收盘价(元)': 'close',
            '成交量': 'volume',
            '成交量(股)': 'volume',
            '成交额(百万)': 'turnover',
            '持仓量': 'open_interest'
        }, inplace=True)
        if not 'open_interest' in df.columns:
            df['open_interest'] = np.nan
    
        df_clip = df[[
            'vt_symbol', 'datetime', 'open', 'high',
            'low', 'close', 'volume', 'turnover', 'open_interest'
        ]]
        return df_clip
    
    def wsd(self, vt_symbols: list[str], indicators: str = '', start: str = '', end: str = '', options: str = '') -> tuple[RetCode, pd.DataFrame]:
        all_df = pd.DataFrame()
        for i, vt_symbol in enumerate(vt_symbols):
            self.log(f'[{i+1}/{len(vt_symbols)}]fetching {vt_symbol}...')
            df = self._wsd(vt_symbol=vt_symbol, indicators=indicators, start=start, end=end, options=options)
            if len(df):
                all_df = pd.concat([all_df, df], ignore_index=True)
        return all_df
    
    def edb(self, vt_symbols: list[str], start: str = '', end: str = '', options: str = '') -> pd.DataFrame:
        return pd.DataFrame()
    
    def query_contracts(self, vt_symbols = None, exchanges = None, products = None, df = True):
        return super().query_contracts(vt_symbols, exchanges, products, df)
    
    def close(self):
        # self.app.quit()
        self.log('wind api closed.')


        