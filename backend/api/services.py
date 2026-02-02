import pandas as pd
import io
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

class DataService:
    @staticmethod
    def process_csv(file_path):
        """Parses CSV and returns summary stats and chart data."""
        try:
            df = pd.read_csv(file_path)
            
            # 1. Validation
            required_cols = {'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'}
            if not required_cols.issubset(df.columns):
                raise ValueError(f"Missing columns. Required: {required_cols}")

            # 2. Calculations
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
    def _create_chart_image(plot_callback):
        """Helper to render a matplotlib plot to an in-memory image buffer."""
        buffer = io.BytesIO()
        plt.figure(figsize=(6, 3.5)) # Corporate standard size for PDF
        plot_callback()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100)
        plt.close()
        buffer.seek(0)
        return ImageReader(buffer)

    @staticmethod
    def generate_pdf(summary):
        """Generates a PDF report with embedded charts."""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # --- HEADER ---
        p.setFont("Helvetica-Bold", 18)
        p.drawString(50, height - 50, "Chemical Equipment Analysis Report")
        p.setFont("Helvetica", 10)
        p.drawString(50, height - 70, "Generated via FOSSEE Internship Visualizer")
        
        p.line(50, height - 80, width - 50, height - 80)

        # --- KEY STATISTICS ---
        y_pos = height - 120
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_pos, "1. Executive Summary")
        
        p.setFont("Helvetica", 12)
        stats = [
            f"Total Units Analyzed: {summary['total_count']}",
            f"Average Temperature: {summary['avg_temperature']} °C",
            f"Average Pressure: {summary['avg_pressure']} Pa",
            f"Average Flowrate: {summary['avg_flowrate']} L/min"
        ]
        
        y_pos -= 25
        for stat in stats:
            p.drawString(70, y_pos, f"• {stat}")
            y_pos -= 20

        # --- CHART 1: EQUIPMENT DISTRIBUTION (Bar) ---
        y_pos -= 40
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_pos, "2. Equipment Distribution")
        
        def plot_bar():
            types = list(summary['type_distribution'].keys())
            counts = list(summary['type_distribution'].values())
            colors = ['#36a2eb', '#ff6384', '#4bc0c0', '#ff9f40', '#9966ff']
            plt.bar(types, counts, color=colors[:len(types)])
            plt.title("Count by Equipment Type")
            plt.ylabel("Quantity")
        
        img_bar = DataService._create_chart_image(plot_bar)
        # Draw image (x, y, width, height)
        p.drawImage(img_bar, 50, y_pos - 220, width=500, height=200)

        # --- CHART 2: TEMP VS PRESSURE (Line) ---
        y_pos -= 260
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_pos, "3. Operational Parameters (Temp vs Pressure)")

        def plot_line():
            labels = summary['chart_data']['labels']
            temp = summary['chart_data']['temperature']
            press = summary['chart_data']['pressure']
            plt.plot(labels, temp, label='Temperature (°C)', color='#ff6384', marker='o')
            plt.plot(labels, press, label='Pressure (Pa)', color='#36a2eb', marker='x')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.xticks(rotation=45)
            
        img_line = DataService._create_chart_image(plot_line)
        p.drawImage(img_line, 50, y_pos - 220, width=500, height=200)

        # --- FOOTER ---
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(50, 30, "Confidential - Internal Use Only")
        p.drawRightString(width - 50, 30, "Page 1")

        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer