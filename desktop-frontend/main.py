import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                             QFileDialog, QVBoxLayout, QWidget, QMessageBox, 
                             QHBoxLayout, QFrame, QDialog, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000/api"

# --- LOGIN DIALOG (New Corporate Feature) ---
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Login - Chemical Visualizer")
        self.setFixedSize(300, 200)
        self.token = None

        layout = QVBoxLayout()

        # Title
        title = QLabel("Please Log In")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Inputs
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        # Login Button
        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_login.setStyleSheet("background-color: #007bff; color: white; padding: 5px;")
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username.text()
        password = self.password.text()

        try:
            response = requests.post(f"{API_URL}/login/", json={
                "username": username,
                "password": password
            })
            
            if response.status_code == 200:
                self.token = response.json()['token']
                self.accept()  # Close dialog and proceed
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid Username or Password")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Could not connect to server.\n{str(e)}")

# --- WORKER THREAD (Prevents GUI Freezing) ---
class UploadThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, file_path, token):
        super().__init__()
        self.file_path = file_path
        self.token = token

    def run(self):
        try:
            with open(self.file_path, 'rb') as f:
                # SECURE UPLOAD: Sending Token in Header
                headers = {'Authorization': f'Token {self.token}'}
                response = requests.post(
                    f"{API_URL}/upload/", 
                    files={'file': f},
                    headers=headers 
                )
            
            if response.status_code == 200:
                self.finished.emit(response.json())
            else:
                self.error.emit(f"Server Error: {response.text}")
        except Exception as e:
            self.error.emit(str(e))

# --- MAIN DASHBOARD ---
class ChemicalApp(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token # Store the token for future requests
        self.setWindowTitle("Chemical Equipment Visualizer (Desktop)")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #f4f4f9;")

        # Main Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)

        # Header
        self.header = QLabel("Chemical Visualizer")
        self.header.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.header.setStyleSheet("color: #333; margin-bottom: 20px;")
        self.layout.addWidget(self.header)

        # Stats Cards Area
        self.stats_layout = QHBoxLayout()
        self.cards = {}
        for title in ["Total Units", "Avg Temp", "Avg Pressure", "Avg Flowrate"]:
            card = QFrame()
            card.setStyleSheet("background-color: white; border-radius: 10px; padding: 10px;")
            card_layout = QVBoxLayout(card)
            
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("color: #888; font-size: 14px;")
            lbl_title.setAlignment(Qt.AlignCenter)
            
            lbl_value = QLabel("-")
            lbl_value.setStyleSheet("color: #333; font-size: 24px; font-weight: bold;")
            lbl_value.setAlignment(Qt.AlignCenter)
            
            card_layout.addWidget(lbl_title)
            card_layout.addWidget(lbl_value)
            self.stats_layout.addWidget(card)
            self.cards[title] = lbl_value

        self.layout.addLayout(self.stats_layout)

        # Upload Button
        self.upload_btn = QPushButton("Upload CSV & Analyze")
        self.upload_btn.setFont(QFont("Segoe UI", 12))
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff; color: white; padding: 10px; border-radius: 5px;
            }
            QPushButton:hover { background-color: #0056b3; }
        """)
        self.upload_btn.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)

        # Charts Area
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', 'CSV Files (*.csv)')
        if fname:
            self.upload_btn.setText("Processing...")
            self.upload_btn.setEnabled(False)
            
            # Start Worker Thread with Token
            self.worker = UploadThread(fname, self.token)
            self.worker.finished.connect(self.update_dashboard)
            self.worker.error.connect(self.show_error)
            self.worker.start()

    def update_dashboard(self, data):
        self.upload_btn.setText("Upload CSV & Analyze")
        self.upload_btn.setEnabled(True)

        # Update Cards
        self.cards["Total Units"].setText(str(data['total_count']))
        self.cards["Avg Temp"].setText(f"{data['avg_temperature']} °C")
        self.cards["Avg Pressure"].setText(f"{data['avg_pressure']} Pa")
        self.cards["Avg Flowrate"].setText(f"{data['avg_flowrate']} L/min")

        # Update Charts
        self.ax1.clear()
        self.ax2.clear()

        # Bar Chart
        types = list(data['type_distribution'].keys())
        counts = list(data['type_distribution'].values())
        self.ax1.bar(types, counts, color='#36a2eb')
        self.ax1.set_title("Equipment Distribution")
        self.ax1.tick_params(axis='x', rotation=45)

        # Line Chart
        labels = data['chart_data']['labels']
        temps = data['chart_data']['temperature']
        pressures = data['chart_data']['pressure']
        
        self.ax2.plot(labels, temps, label='Temp', color='#ff6384')
        self.ax2.plot(labels, pressures, label='Pressure', color='#35a2eb')
        self.ax2.set_title("Temp vs Pressure")
        self.ax2.legend()
        self.ax2.tick_params(axis='x', rotation=45)

        self.figure.tight_layout()
        self.canvas.draw()
        
        QMessageBox.information(self, "Success", "Analysis Complete!")

    def show_error(self, message):
        self.upload_btn.setText("Upload CSV & Analyze")
        self.upload_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", message)

# --- APPLICATION ENTRY POINT ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # 1. Show Login Dialog First
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        # 2. If Login Success, Show Main App with Token
        window = ChemicalApp(login.token)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)