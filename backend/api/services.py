import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class DataService:
    @staticmethod
    def process_csv(file_path):
        """Parses CSV and returns summary stats and chart data."""
        try:
            df = pd.read_csv(file_path)
            
            # 1. Corporate Validation: Ensure required columns exist
            required_cols = {'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'}
            if not required_cols.issubset(df.columns):
                raise ValueError(f"Missing columns. Required: {required_cols}")

            # 2. Perform Calculations
            summary = {
                "total_count": int(len(df)),
                "avg_temperature": round(float(df['Temperature'].mean()), 2),
                "avg_pressure": round(float(df['Pressure'].mean()), 2),
                "avg_flowrate": round(float(df['Flowrate'].mean()), 2),
                "type_distribution": df['Type'].value_counts().to_dict(),
                "chart_data": {
                    "labels": df['Equipment Name'].fillna("Unknown").tolist(),
                    "temperature": df['Temperature'].fillna(0).tolist(),
                    "pressure": df['Pressure'].fillna(0).tolist()
                }
            }
            return summary
        except Exception as e:
            raise ValueError(f"Error processing CSV: {str(e)}")

    @staticmethod
    def generate_pdf(summary):
        """Generates a PDF report buffer."""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Chemical Equipment Analysis Report")
        
        # Stats
        p.setFont("Helvetica", 12)
        p.drawString(100, 730, "------------------------------------------------")
        p.drawString(100, 700, f"Total Units: {summary['total_count']}")
        p.drawString(100, 680, f"Avg Temperature: {summary['avg_temperature']} C")
        p.drawString(100, 660, f"Avg Pressure: {summary['avg_pressure']} Pa")
        p.drawString(100, 640, f"Avg Flowrate: {summary['avg_flowrate']} L/min")
        
        # Distribution List
        y = 600
        p.drawString(100, y, "Equipment Distribution:")
        p.setFont("Helvetica-Oblique", 10)
        for type_name, count in summary['type_distribution'].items():
            y -= 20
            p.drawString(120, y, f"- {type_name}: {count}")
            
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer