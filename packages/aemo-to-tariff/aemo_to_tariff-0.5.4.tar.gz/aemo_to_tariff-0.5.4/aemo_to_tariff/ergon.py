from datetime import time, datetime
from zoneinfo import ZoneInfo

def time_zone():
    return 'Australia/Brisbane'

daily_fees = {
    'WRTDEMT1': 1.746,
    'ERTOUET1': 1.798,
}

demand_charges = {
    'WRTDEMT1': 22.388,
}

tariffs = {
    'WRTDEMT1': {
        'name': 'Residential Transitional Demand WRTDEMT1',
        'periods': [('Anytime', time(0, 0), time(23, 59), 26.793)],
        'rate': 26.793
    },
    'ERTOUET1': {
        'name': 'Residential ToU Energy',
        'periods': [
            ('Peak', time(17, 0), time(21, 0), 59.684),
            ('Shoulder', time(7, 0), time(17, 0), 24.912),
            ('Off-Peak', time(21, 0), time(7, 0), 7.161)
        ],
        'rate': {'Peak': 59.684, 'Shoulder': 24.912, 'Off-Peak': 7.161}
    }
}

def get_daily_fee(tariff_code: str, annual_usage: float = None):
    return daily_fees.get(tariff_code, 0.0)

def calculate_demand_fee(tariff_code: str, demand_kw: float, days: int = 30):
    if tariff_code not in demand_charges:
        return 0.0
    daily_rate = demand_charges[tariff_code]
    return daily_rate * demand_kw * days

def get_periods(tariff_code: str):
    tariff = tariffs.get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")
    return tariff['periods']

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    return rrp / 10

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()
    rrp_c_kwh = rrp / 10
    tariff = tariffs.get(tariff_code)
    if not tariff:
        slope = 1.037869032618134
        intercept = 5.586606750833143
        return rrp_c_kwh * slope + intercept
    for period, start, end, rate in tariff['periods']:
        if start <= interval_time < end or (start > end and (interval_time >= start or interval_time < end)):
            return rrp_c_kwh + rate
    return rrp_c_kwh + (tariff['rate'] if isinstance(tariff['rate'], float) else list(tariff['rate'].values())[0])
