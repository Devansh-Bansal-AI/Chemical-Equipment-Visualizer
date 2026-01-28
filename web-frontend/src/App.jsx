import { useState } from 'react';
import axios from 'axios';
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

// Register ChartJS components so they work
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

function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handle file selection
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null); 
  };

  // Handle Upload to Django
  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    setLoading(true);

    try {
      // POST request to your Django Backend
      const res = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setData(res.data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setError("Upload failed. Make sure Backend is running!");
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', fontFamily: 'Segoe UI, sans-serif', backgroundColor: '#f4f4f9', minHeight: '100vh' }}>
      <h1 style={{ color: '#333', textAlign: 'center' }}>🧪 Chemical Equipment Visualizer</h1>
      
      {/* Upload Section */}
      <div style={{ 
        backgroundColor: 'white', 
        padding: '20px', 
        borderRadius: '10px', 
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)', 
        maxWidth: '600px', 
        margin: '0 auto 30px auto',
        textAlign: 'center' 
      }}>
        <input 
          type="file" 
          onChange={handleFileChange} 
          accept=".csv" 
          style={{ padding: '10px' }}
        />
        <button 
          onClick={handleUpload} 
          style={{ 
            padding: '10px 20px', 
            backgroundColor: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '5px', 
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          {loading ? "Processing..." : "Analyze Data"}
        </button>
        {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
      </div>

      {/* Dashboard Results */}
      {data && (
        <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
          
          {/* 1. Summary Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '30px' }}>
            <Card title="Total Units" value={data.total_count} />
            <Card title="Avg Temp" value={`${data.avg_temperature} °C`} />
            <Card title="Avg Pressure" value={`${data.avg_pressure} Pa`} />
            <Card title="Avg Flowrate" value={`${data.avg_flowrate} L/min`} />
          </div>

          {/* 2. Charts Area */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
            
            {/* Bar Chart: Equipment Types */}
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

            {/* Line Chart: Temp vs Pressure */}
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

// Simple Card Component for Stats
function Card({ title, value }) {
  return (
    <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '10px', textAlign: 'center', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h4 style={{ margin: '0 0 10px 0', color: '#888' }}>{title}</h4>
      <h2 style={{ margin: 0, color: '#333' }}>{value}</h2>
    </div>
  );
}

export default App;