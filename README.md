Recruiters often read this before running the code. Create a file named README.md in your root folder (K:\ChemicalVisualizer\README.md) and paste this professional documentation.

Markdown

# Chemical Equipment Parameter Visualizer (Hybrid App)

## 📌 Project Overview
A hybrid analytics application developed for the FOSSEE Internship Screening. This system allows users to upload chemical equipment data (CSV) and visualizes key parameters like Temperature, Pressure, and Flowrate. 

It features a **Single Backend (Django)** that serves two distinct frontends:
1.  **Web Application:** Built with React.js & Chart.js for browser access.
2.  **Desktop Application:** Built with PyQt5 & Matplotlib for native desktop access.

## 🛠️ Tech Stack
* **Backend:** Python Django 5, Django REST Framework, Pandas (Data Analysis)
* **Web Frontend:** React.js, Vite, Chart.js, Axios
* **Desktop Frontend:** Python PyQt5, Matplotlib, Requests
* **Database:** SQLite (Auto-cleans history to keep latest 5 uploads)

## 🚀 How to Run

### Step 1: Start the Backend
The backend must be running for both apps to work.
```bash
cd backend
# Windows:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
# Server will start at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
Step 2: Run the Web App
Bash

cd web-frontend
npm install
npm run dev
# Open the link provided (e.g., http://localhost:5173)
Step 3: Run the Desktop App
Bash

cd desktop-frontend
pip install PyQt5 requests matplotlib
python main.py
📂 Project Structure
Plaintext

ChemicalVisualizer/
├── backend/            # Django API & Logic
├── web-frontend/       # React Source Code
├── desktop-frontend/   # PyQt5 Source Code
└── sample_equipment_data.csv  # Test Data
✨ Key Features
Unified API: Both platforms use the same logic, ensuring data consistency.

Data Analysis: Automatically calculates averages and equipment distributions.

Interactive Charts: Dynamic visualization of Temperature vs. Pressure profiles.