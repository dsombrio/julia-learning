import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000/api';

// Login component
function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_URL}/auth/login`, { email, password });
      localStorage.setItem('token', res.data.token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
      onLogin(res.data.user);
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>CRM Login</h1>
        {error && <div className="error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Login</button>
        </form>
      </div>
    </div>
  );
}

// Company List component
function Companies({ token }) {
  const [companies, setCompanies] = useState([]);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '', type: '', city: '', state: '', metro_area: '', phone: '', website: ''
  });

  useEffect(() => {
    fetchCompanies();
  }, [search]);

  const fetchCompanies = async () => {
    try {
      const url = search 
        ? `${API_URL}/companies?search=${search}`
        : `${API_URL}/companies`;
      const res = await axios.get(url, { headers: { Authorization: `Bearer ${token}` } });
      setCompanies(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/companies`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowForm(false);
      setFormData({ name: '', type: '', city: '', state: '', metro_area: '', phone: '', website: '' });
      fetchCompanies();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="section">
      <div className="section-header">
        <h2>Companies ({companies.length})</h2>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add'}
        </button>
      </div>
      
      <input
        type="text"
        placeholder="Search companies..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="search-input"
      />

      {showForm && (
        <form onSubmit={handleSubmit} className="form-inline">
          <input placeholder="Company Name" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
          <input placeholder="Type" value={formData.type} onChange={e => setFormData({...formData, type: e.target.value})} />
          <input placeholder="City" value={formData.city} onChange={e => setFormData({...formData, city: e.target.value})} />
          <input placeholder="State" value={formData.state} onChange={e => setFormData({...formData, state: e.target.value})} />
          <select value={formData.metro_area} onChange={e => setFormData({...formData, metro_area: e.target.value})}>
            <option value="">Select Metro</option>
            <option value="Austin">Austin</option>
            <option value="Houston">Houston</option>
            <option value="Dallas-Fort Worth">Dallas-Fort Worth</option>
            <option value="San Antonio">San Antonio</option>
            <option value="College Station">College Station</option>
          </select>
          <input placeholder="Phone" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />
          <input placeholder="Website" value={formData.website} onChange={e => setFormData({...formData, website: e.target.value})} />
          <button type="submit">Save</button>
        </form>
      )}

      <div className="list">
        {companies.map(company => (
          <div key={company.id} className="card">
            <div className="card-header">
              <strong>{company.name}</strong>
              <span className="badge">{company.type}</span>
            </div>
            <div className="card-body">
              <p>{company.city}, {company.state}</p>
              <p>{company.phone}</p>
              <p>{company.metro_area}</p>
            </div>
          </div>
        ))}
        {companies.length === 0 && <p className="empty">No companies found</p>}
      </div>
    </div>
  );
}

// Tasks component
function Tasks({ token }) {
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('pending');

  useEffect(() => {
    fetchTasks();
  }, [filter]);

  const fetchTasks = async () => {
    try {
      let url = `${API_URL}/tasks?`;
      if (filter === 'pending') url += 'completed=false';
      else if (filter === 'today') url += 'due_today=true';
      else if (filter === 'overdue') url += 'overdue=true';
      
      const res = await axios.get(url, { headers: { Authorization: `Bearer ${token}` } });
      setTasks(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const completeTask = async (id) => {
    try {
      await axios.patch(`${API_URL}/tasks/${id}/complete`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchTasks();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="section">
      <div className="section-header">
        <h2>Tasks</h2>
      </div>
      
      <div className="tabs">
        <button className={filter === 'pending' ? 'active' : ''} onClick={() => setFilter('pending')}>Pending</button>
        <button className={filter === 'today' ? 'active' : ''} onClick={() => setFilter('today')}>Due Today</button>
        <button className={filter === 'overdue' ? 'active' : ''} onClick={() => setFilter('overdue')}>Overdue</button>
      </div>

      <div className="list">
        {tasks.map(task => (
          <div key={task.id} className={`card ${task.completed ? 'completed' : ''}`}>
            <div className="card-header">
              <strong>{task.title}</strong>
              {!task.completed && (
                <button className="btn-small" onClick={() => completeTask(task.id)}>✓</button>
              )}
            </div>
            <div className="card-body">
              <p>{task.description}</p>
              {task.due_date && <p className="date">Due: {new Date(task.due_date).toLocaleDateString()}</p>}
              {task.company_name && <p className="company">Company: {task.company_name}</p>}
            </div>
          </div>
        ))}
        {tasks.length === 0 && <p className="empty">No tasks</p>}
      </div>
    </div>
  );
}

// Deals component
function Deals({ token }) {
  const [deals, setDeals] = useState([]);

  useEffect(() => {
    fetchDeals();
  }, []);

  const fetchDeals = async () => {
    try {
      const res = await axios.get(`${API_URL}/deals`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDeals(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="section">
      <div className="section-header">
        <h2>Deals ({deals.length})</h2>
      </div>
      
      <div className="list">
        {deals.map(deal => (
          <div key={deal.id} className="card">
            <div className="card-header">
              <strong>{deal.name}</strong>
              <span className="badge">{deal.stage}</span>
            </div>
            <div className="card-body">
              <p className="value">${parseFloat(deal.value).toLocaleString()}</p>
              {deal.company_name && <p>Company: {deal.company_name}</p>}
              <p>Status: {deal.status}</p>
            </div>
          </div>
        ))}
        {deals.length === 0 && <p className="empty">No deals</p>}
      </div>
    </div>
  );
}

// Main App
function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('companies');

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>CRM</h1>
        <div className="user-info">
          <span>{user.name}</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </header>
      
      <nav className="nav">
        <button className={activeTab === 'companies' ? 'active' : ''} onClick={() => setActiveTab('companies')}>Companies</button>
        <button className={activeTab === 'deals' ? 'active' : ''} onClick={() => setActiveTab('deals')}>Deals</button>
        <button className={activeTab === 'tasks' ? 'active' : ''} onClick={() => setActiveTab('tasks')}>Tasks</button>
      </nav>
      
      <main className="main">
        {activeTab === 'companies' && <Companies token={localStorage.getItem('token')} />}
        {activeTab === 'deals' && <Deals token={localStorage.getItem('token')} />}
        {activeTab === 'tasks' && <Tasks token={localStorage.getItem('token')} />}
      </main>
    </div>
  );
}

export default App;
