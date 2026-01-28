import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Login({ setToken }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/login/', {
        username,
        password
      });
      // Save token to parent state and localStorage
      const token = res.data.token;
      setToken(token);
      localStorage.setItem('auth_token', token);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid Credentials');
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#f0f2f5' }}>
      <div style={{ padding: '40px', background: 'white', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '300px' }}>
        <h2 style={{ textAlign: 'center', color: '#333' }}>Login</h2>
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '15px' }}>
            <input 
              type="text" 
              placeholder="Username" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
            />
          </div>
          <div style={{ marginBottom: '15px' }}>
            <input 
              type="password" 
              placeholder="Password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: '100%', padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
            />
          </div>
          {error && <p style={{ color: 'red', fontSize: '14px' }}>{error}</p>}
          <button type="submit" style={{ width: '100%', padding: '10px', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;