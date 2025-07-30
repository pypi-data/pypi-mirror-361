# conftest.py
import pytest
import os

def assert_debug(something):
    try:
        assert something
    except AssertionError as e:
        breakpoint()
        raise e
    
@pytest.fixture
def wind_api(request, monkeypatch):
    # 设置环境变量 CONFIG 的值
    CONFIG_NAME = request.param['config_name']
    GATEWAY_NAME = request.param['gateway_name']

    assert(GATEWAY_NAME == 'KS_WIND')
    monkeypatch.setenv('CONFIG', CONFIG_NAME)
    assert_debug(os.getenv('CONFIG') == CONFIG_NAME)
    

    from module.setting import load_json
    from ks_wind_api import KsWindApi
    
    config = load_json('setting.json')
    wind_api = KsWindApi(config['stock_lb_rank']['gateway']['market_api']['setting'])
    return wind_api

