from django.test import TestCase
from .services import DataService
import pandas as pd
import io

class AnalysisTests(TestCase):
    def test_stats_calculation(self):
        # Create a fake in-memory CSV
        csv_content = b"Equipment Name,Type,Flowrate,Pressure,Temperature\nPump A,Pump,10,100,50\nPump B,Pump,20,200,150"
        file = io.BytesIO(csv_content)

        # Run analysis
        summary = DataService.process_csv(file)

        # Check math
        self.assertEqual(summary['total_count'], 2)
        self.assertEqual(summary['avg_temperature'], 100.0) # (50+150)/2