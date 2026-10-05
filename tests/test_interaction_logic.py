import unittest
from datetime import datetime, date
from vitalregistro.picker_logic import valid_date, wheel_index, wheel_position, format_day
from vitalregistro.chart_logic import ChartPoint, project_x, hit_points, point_text
from vitalregistro.models import Measurement

class WheelLogicTests(unittest.TestCase):
    def test_leap_and_month_clamping(self):
        self.assertEqual(valid_date(2024,2,31),date(2024,2,29))
        self.assertEqual(valid_date(2025,2,29),date(2025,2,28))
        self.assertEqual(valid_date(2026,4,31),date(2026,4,30))
        self.assertEqual(valid_date(2000,2,29),date(2000,2,29))
        self.assertEqual(valid_date(1900,2,29),date(1900,2,28))
    def test_historical_years_roundtrip_to_form(self):
        for year in (1, 999, 1900, 9999):
            value=date(year,1,1)
            record=Measurement.from_fields(format_day(value),"23:59","peso",weight="70")
            self.assertEqual(record.measured_at.date(), value)
    def test_wheel_indices_roundtrip_and_bounds(self):
        for count in (1,24,60,9999):
            for i in range(count):
                self.assertEqual(wheel_index(wheel_position(i,count),count),i)
            self.assertEqual(wheel_index(-1,count),count-1)
            self.assertEqual(wheel_index(2,count),0)
        self.assertEqual(wheel_index(.51,60),29)

class ChartLogicTests(unittest.TestCase):
    def setUp(self):
        self.record=Measurement(datetime(2026,10,5,8),"pressao",systolic=120,diastolic=80,pulse=70)
        self.a=ChartPoint(100,100,self.record,"systolic")
        self.b=ChartPoint(100,90,self.record,"diastolic")
    def test_distinct_times_same_day_and_single_point(self):
        first=self.record.measured_at; last=first.replace(hour=19)
        self.assertEqual(project_x(first,first,last,10,200),10)
        self.assertEqual(project_x(last,first,last,10,200),210)
        self.assertEqual(project_x(first,first,first,10,200),110)
    def test_nearest_with_tolerance_and_series(self):
        self.assertEqual(hit_points([self.a,self.b],100,91,24),[self.b])
        self.assertEqual(hit_points([self.a,self.b],100,101,24),[self.a])
        self.assertEqual(hit_points([self.a,self.b],200,200,24),[])
        self.assertEqual(hit_points([self.a],124,100,24),[self.a])
        self.assertEqual(hit_points([self.a],124.01,100,24),[])
        self.assertIn("Diastólica: 80 mmHg",point_text(self.b))
        self.assertIn("05/10/2026 08:00",point_text(self.a))
    def test_exact_overlap_does_not_hide_second_series(self):
        b=ChartPoint(100,100,self.record,"diastolic")
        self.assertEqual(hit_points([self.a,b],100,100,24),[self.a,b])
