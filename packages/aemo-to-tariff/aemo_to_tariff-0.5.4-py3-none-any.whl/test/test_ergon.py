import unittest
from datetime import datetime, time
from zoneinfo import ZoneInfo

from aemo_to_tariff.ergon import (
    time_zone,
    get_daily_fee,
    calculate_demand_fee,
    get_periods,
    convert_feed_in_tariff,
    convert,
)

class TestErgonFunctions(unittest.TestCase):
    def test_time_zone(self):
        self.assertEqual(time_zone(), 'Australia/Brisbane')

    def test_get_daily_fee(self):
        self.assertEqual(get_daily_fee('WRTDEMT1'), 1.746)
        self.assertEqual(get_daily_fee('ERTOUET1'), 1.798)

    
    def test_get_periods(self):
        periods = get_periods('WRTDEMT1')
        self.assertEqual(len(periods), 1)
        self.assertEqual(periods[0], ('Anytime', time(0, 0), time(23, 59), 26.793))
        with self.assertRaises(ValueError):
            get_periods('UNKNOWN')

    def test_convert_feed_in_tariff(self):
        interval_datetime = datetime(2023, 1, 1, 12, 0, tzinfo=ZoneInfo('Australia/Brisbane'))
        self.assertEqual(convert_feed_in_tariff(interval_datetime, 'WRTDEMT1', 100), 10.0)

    def test_WRTDEMT1_tariff(self):
        # 13:00 27.25c/kWh v -3.66c/kWh for RRP $-31.99/MWh
        interval_datetime = datetime(2025, 4, 5, 12, 0, tzinfo=ZoneInfo('Australia/Brisbane'))
        self.assertAlmostEqual(convert(interval_datetime, 'WRTDEMT1', -31.99), 23.594, places=2)
    
    def test_ERTOUET1_tariff(self):
        # 13:00 27.25c/kWh v -3.66c/kWh for RRP $-31.99/MWh
        interval_datetime = datetime(2025, 4, 5, 12, 0, tzinfo=ZoneInfo('Australia/Brisbane'))
        self.assertAlmostEqual(convert(interval_datetime, 'ERTOUET1', -31.99), 21.713, places=2)
    