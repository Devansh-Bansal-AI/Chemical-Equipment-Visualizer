import { useState, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// --- DASHBOARD COMPONENT ---
// This contains the Upload + Charts logic (formerly in App)
function Dashboard({ token, onLogout }) {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handle File Upload
  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Token ${token}` // <--- Critical: Send Token to Backend
        },
      });
      setData(res.data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Upload failed. Session might be expired.");
    } finally {
      setLoading(false);
    }
  };

  // Handle PDF Download
  const downloadPDF = async () => {
    if (!data || !data.file_id) return;

    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/report/${data.file_id}/`, {
        headers: {
          'Authorization': `Token ${token}`
        },
        responseType: 'blob' // Important for handling binary files
      });

      // Create a link to download the blob
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Analysis_Report_${data.file_id}.pdf`);
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      console.error(err);
      alert("Error downloading PDF");
    }
  };

  return (
    <div style={{ padding: '40px', fontFamily: 'Segoe UI, sans-serif', backgroundColor: '#f4f4f9', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ color: '#333', margin: 0 }}>🧪 Chemical Equipment Visualizer</h1>
        <button 
          onClick={onLogout} 
          style={{ padding: '10px 20px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
        >
          Logout
        </button>
      </div>
      
      {/* Upload Section */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', textAlign: 'center', marginBottom: '30px', maxWidth: '800px', margin: '0 auto 30px auto' }}>
        <input 
          type="file" 
          onChange={(e) => setFile(e.target.files[0])} 
          accept=".csv" 
          style={{ padding: '10px', marginRight: '10px' }}
        />
        <button 
          onClick={handleUpload} 
          disabled={loading}
          style={{ 
            padding: '10px 20px', 
            backgroundColor: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '5px', 
            cursor: 'pointer',
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? "Processing..." : "Analyze Data"}
        </button>

        {/* PDF Download Button (Only shows if data exists) */}
        {data && (
          <button 
            onClick={downloadPDF} 
            style={{ 
              marginLeft: '15px', 
              padding: '10px 20px', 
              backgroundColor: '#28a745', 
              color: 'white', 
              border: 'none', 
              borderRadius: '5px', 
              cursor: 'pointer' 
            }}
          >
            📄 Download PDF Report
          </button>
        )}

        {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
      </div>

      {/* Results Dashboard */}
      {data && (
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
          
          {/* Summary Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '30px' }}>
            <Card title="Total Units" value={data.total_count} />
            <Card title="Avg Temp" value={`${data.avg_temperature} °C`} />
            <Card title="Avg Pressure" value={`${data.avg_pressure} Pa`} />
            <Card title="Avg Flowrate" value={`${data.avg_flowrate} L/min`} />
          </div>

          {/* Charts */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
            
            {/* Bar Chart */}
            <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
              <h3 style={{ textAlign: 'center', color: '#555' }}>Equipment Distribution</h3>
              <Bar data={{
                labels: Object.keys(data.type_distribution),
                datasets: [{
                  label: 'Count',
                  data: Object.values(data.type_distribution),
                  backgroundColor: 'rgba(54, 162, 235, 0.6)',
                }]
              }} />
            </div>

            {/* Line Chart */}
            <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
              <h3 style={{ textAlign: 'center', color: '#555' }}>Temperature vs Pressure</h3>
              <Line data={{
                labels: data.chart_data.labels,
                datasets: [
                  {
                    label: 'Temperature (°C)',
                    data: data.chart_data.temperature,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    tension: 0.3
                  },
                  {
                    label: 'Pressure (Pa)',
                    data: data.chart_data.pressure,
                    borderColor: 'rgb(53, 162, 235)',
                    backgroundColor: 'rgba(53, 162, 235, 0.5)',
                    tension: 0.3
                  }
                ]
              }} />
            </div>

          </div>
        </div>
      )}
    </div>
  );
}

// --- HELPER COMPONENT ---
function Card({ title, value }) {
  return (
    <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '10px', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h4 style={{ margin: '0 0 10px 0', color: '#888' }}>{title}</h4>
      <h2 style={{ margin: 0, color: '#333' }}>{value}</h2>
    </div>
  );
}

// --- MAIN APP COMPONENT (ROUTER) ---
function App() {
  // Check if token exists in localStorage to keep user logged in
  const [token, setToken] = useState(localStorage.getItem('auth_token'));

  // Logout function: Clear token and state
  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('auth_token');
  };

  return (
    <Router>
      <Routes>
        {/* If not logged in, show Login. If logged in, go to Dashboard */}
        <Route 
          path="/login" 
          element={!token ? <Login setToken={setToken} /> : <Navigate to="/dashboard" />} 
        />
        
        {/* If logged in, show Dashboard. If not, go to Login */}
        <Route 
          path="/dashboard" 
          element={token ? <Dashboard token={token} onLogout={handleLogout} /> : <Navigate to="/login" />} 
        />
        
        {/* Redirect any other URL to Dashboard (or Login if not auth) */}
        <Route 
          path="*" 
          element={<Navigate to={token ? "/dashboard" : "/login"} />} 
        />
      </Routes>
    </Router>
  );
}

export default App;