import React, { useState } from 'react';
import DocumentUpload from './DocumentUpload';
import DocumentView from './DocumentView';
import './App.css';

const App = () => {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: '',
  });
  const [registerForm, setRegisterForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'corporate',
    org_name: '',
  });

  const handleLoginChange = (e) => {
    const { name, value } = e.target;
    setLoginForm(prev => ({ ...prev, [name]: value }));
  };

  const handleRegisterChange = (e) => {
    const { name, value } = e.target;
    setRegisterForm(prev => ({ ...prev, [name]: value }));
  };

  const handleLogin = async () => {
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: loginForm.email,
          password: loginForm.password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAccessToken(data.access_token);
        setUser(data.user);
        setCurrentPage('dashboard');
      } else {
        alert('Login failed');
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  const handleRegister = async () => {
    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerForm),
      });

      if (response.ok) {
        alert('Registration successful! Please login.');
        setCurrentPage('login');
        setRegisterForm({
          name: '',
          email: '',
          password: '',
          role: 'corporate',
          org_name: '',
        });
      } else {
        const error = await response.json();
        alert(`Registration failed: ${error.detail}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  const handleLogout = () => {
    setUser(null);
    setAccessToken(null);
    setCurrentPage('dashboard');
    setSelectedDocId(null);
  };

  if (!user) {
    return (
      <div className="app">
        <header className="app-header">
          <h1>Trade Finance Blockchain Explorer</h1>
        </header>

        {currentPage === 'login' && (
          <div className="auth-container">
            <div className="auth-form">
              <h2>Login</h2>
              <input
                type="email"
                name="email"
                placeholder="Email"
                value={loginForm.email}
                onChange={handleLoginChange}
              />
              <input
                type="password"
                name="password"
                placeholder="Password"
                value={loginForm.password}
                onChange={handleLoginChange}
              />
              <button onClick={handleLogin}>Login</button>
              <p>
                Don't have an account?{' '}
                <button
                  onClick={() => setCurrentPage('register')}
                  className="link-btn"
                >
                  Register
                </button>
              </p>
            </div>
          </div>
        )}

        {currentPage === 'register' && (
          <div className="auth-container">
            <div className="auth-form">
              <h2>Register</h2>
              <input
                type="text"
                name="name"
                placeholder="Full Name"
                value={registerForm.name}
                onChange={handleRegisterChange}
              />
              <input
                type="email"
                name="email"
                placeholder="Email"
                value={registerForm.email}
                onChange={handleRegisterChange}
              />
              <input
                type="password"
                name="password"
                placeholder="Password"
                value={registerForm.password}
                onChange={handleRegisterChange}
              />
              <select
                name="role"
                value={registerForm.role}
                onChange={handleRegisterChange}
              >
                <option value="corporate">Corporate (Buyer/Seller)</option>
                <option value="bank">Bank</option>
                <option value="auditor">Auditor</option>
                <option value="admin">Admin</option>
              </select>
              <input
                type="text"
                name="org_name"
                placeholder="Organization Name"
                value={registerForm.org_name}
                onChange={handleRegisterChange}
              />
              <button onClick={handleRegister}>Register</button>
              <p>
                Already have an account?{' '}
                <button
                  onClick={() => setCurrentPage('login')}
                  className="link-btn"
                >
                  Login
                </button>
              </p>
            </div>
          </div>
        )}

        {currentPage === 'dashboard' && (
          <div className="welcome">
            <h2>Welcome to Trade Finance Blockchain Explorer</h2>
            <p>
              Please{' '}
              <button
                onClick={() => setCurrentPage('login')}
                className="link-btn"
              >
                login
              </button>{' '}
              or{' '}
              <button
                onClick={() => setCurrentPage('register')}
                className="link-btn"
              >
                register
              </button>{' '}
              to continue.
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Trade Finance Blockchain Explorer</h1>
        <div className="user-info">
          <span>{user.name} ({user.role})</span>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <nav className="app-nav">
        <button
          onClick={() => {
            setCurrentPage('dashboard');
            setSelectedDocId(null);
          }}
          className={currentPage === 'dashboard' ? 'active' : ''}
        >
          Dashboard
        </button>
        {user.role === 'corporate' && (
          <button
            onClick={() => setCurrentPage('upload')}
            className={currentPage === 'upload' ? 'active' : ''}
          >
            Upload Document
          </button>
        )}
      </nav>

      <main className="app-main">
        {currentPage === 'dashboard' && (
          <div className="dashboard">
            <h2>Welcome, {user.name}</h2>
            <p>Role: <strong>{user.role}</strong></p>
            <p>Organization: <strong>{user.org_name}</strong></p>

            {selectedDocId && (
              <div>
                <button onClick={() => setSelectedDocId(null)} className="back-btn">
                  ← Back
                </button>
                <DocumentView
                  docId={selectedDocId}
                  userRole={user.role}
                  userId={user.id}
                  accessToken={accessToken}
                />
              </div>
            )}
          </div>
        )}

        {currentPage === 'upload' && (
          <DocumentUpload
            userRole={user.role}
            userId={user.id}
            accessToken={accessToken}
          />
        )}
      </main>
    </div>
  );
};

export default App;
