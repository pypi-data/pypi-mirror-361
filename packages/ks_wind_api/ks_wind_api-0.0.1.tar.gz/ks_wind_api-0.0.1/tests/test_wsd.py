from conftest import assert_debug
from ks_wind_api import KsWindApi
import pytest
import asyncio
from datetime import datetime, timedelta
from config import CONFIGS

indicators = 'close'
start = (datetime.now() - timedelta(days=3)).strftime('%Y%m%d')
end = datetime.now().strftime('%Y%m%d')

test_wsd_samples = [
    {
        # 'vt_symbols': ['600519.SSE', '000001.SZSE', '832735.BSE'], # 先不测试北交所，好像有数据缺失
        'vt_symbols': ['IC.CFFEX', '600519.SSE', '000001.SZSE'],
        'indicators': indicators,
        'options': ''
    },
    {
        'vt_symbols': ['00700.SEHK'],
        'indicators': indicators,
        'options': ''
    },
    {
        'vt_symbols': ['NVDA.NASDAQ'],
        'indicators': indicators,
        'options': ''
    }
]

@pytest.mark.asyncio
@pytest.mark.parametrize("wind_api", CONFIGS, indirect=True)
def test_wsd(wind_api):
    for i, sample in enumerate(test_wsd_samples):
        print(f'[{i+1}/{len(test_wsd_samples)}]{sample["vt_symbols"]}...')
        df = wind_api.wsd(sample['vt_symbols'], sample['indicators'], start, end, sample['options'])
        assert_debug(len(df) > 0)
        assert_debug(df.iloc[0]['close'] is not None)
        assert_debug(df.iloc[-1]['close'] is not None)