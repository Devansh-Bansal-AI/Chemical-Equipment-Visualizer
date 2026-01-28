import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QFileDialog, QLabel, QHBoxLayout, QMessageBox, QFrame)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer (Desktop)")
        self.setGeometry(100, 100, 1100, 800)
        self.setStyleSheet("background-color: #f4f4f9;") # Match Web Theme

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # --- Header Section ---
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("Chemical Visualizer")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #333;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()

        # Upload Button
        self.upload_btn = QPushButton("Upload CSV")
        self.upload_btn.setFont(QFont("Segoe UI", 12))
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.upload_btn.clicked.connect(self.upload_file)
        header_layout.addWidget(self.upload_btn)
        
        self.layout.addLayout(header_layout)

        # --- Stats Cards Section ---
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        
        # Create placeholders for 4 cards
        self.card_total = self.create_card("Total Units", "-")
        self.card_temp = self.create_card("Avg Temp", "-")
        self.card_pressure = self.create_card("Avg Pressure", "-")
        self.card_flow = self.create_card("Avg Flowrate", "-")
        
        self.stats_layout.addWidget(self.card_total)
        self.stats_layout.addWidget(self.card_temp)
        self.stats_layout.addWidget(self.card_pressure)
        self.stats_layout.addWidget(self.card_flow)
        
        self.layout.addLayout(self.stats_layout)

        # --- Charts Section (Matplotlib) ---
        # We create a Matplotlib Figure with 2 subplots
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 5))
        self.figure.patch.set_facecolor('#f4f4f9') # Match background
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def create_card(self, title_text, value_text):
        """Helper to create a nice looking card widget"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
        """)
        layout = QVBoxLayout(card)
        
        title = QLabel(title_text)
        title.setFont(QFont("Segoe UI", 10))
        title.setStyleSheet("color: #888; border: none;")
        title.setAlignment(Qt.AlignCenter)
        
        value = QLabel(value_text)
        value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        value.setStyleSheet("color: #333; border: none;")
        value.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(value)
        return card

    def update_card(self, card_widget, value):
        """Helper to update the value text inside a card"""
        # The value label is the second item in the layout (index 1)
        value_label = card_widget.layout().itemAt(1).widget()
        value_label.setText(str(value))

    def upload_file(self):
        # 1. Open File Dialog
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '.', "CSV files (*.csv)")
        if not fname:
            return

        # 2. Send to Django API
        url = 'http://127.0.0.1:8000/api/upload/'
        files = {'file': open(fname, 'rb')}
        
        try:
            self.upload_btn.setText("Processing...")
            self.upload_btn.setEnabled(False)
            QApplication.processEvents() # Force UI update

            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.update_ui(data)
            else:
                QMessageBox.critical(self, "Error", f"Server Error: {response.text}")
                
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", 
                "Could not connect to Backend.\nMake sure Django is running on Port 8000!")
        finally:
            self.upload_btn.setText("Upload CSV")
            self.upload_btn.setEnabled(True)

    def update_ui(self, data):
        # 1. Update Cards
        self.update_card(self.card_total, data['total_count'])
        self.update_card(self.card_temp, f"{data['avg_temperature']} °C")
        self.update_card(self.card_pressure, f"{data['avg_pressure']} Pa")
        self.update_card(self.card_flow, f"{data['avg_flowrate']} L/min")

        # 2. Update Charts
        self.ax1.clear()
        self.ax2.clear()

        # Chart 1: Bar Chart
        types = list(data['type_distribution'].keys())
        counts = list(data['type_distribution'].values())
        bars = self.ax1.bar(types, counts, color='#36A2EB', alpha=0.7)
        self.ax1.set_title("Equipment Distribution", fontsize=10)
        self.ax1.tick_params(axis='x', rotation=45)

        # Chart 2: Line Chart
        labels = data['chart_data']['labels']
        temps = data['chart_data']['temperature']
        pressures = data['chart_data']['pressure']
        
        self.ax2.plot(labels, temps, label='Temp (°C)', marker='o', color='#FF6384')
        self.ax2.plot(labels, pressures, label='Pressure (Pa)', marker='x', color='#36A2EB')
        self.ax2.set_title("Temperature vs Pressure", fontsize=10)
        self.ax2.legend()
        self.ax2.grid(True, linestyle='--', alpha=0.5)

        # Refresh Canvas
        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == '__main__':
    # Fix for High DPI displays (makes text look sharp)
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())