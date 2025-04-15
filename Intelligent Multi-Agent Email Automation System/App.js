import React, { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Import pages
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import EmailList from './pages/EmailList';
import Settings from './pages/Settings';
import Integrations from './pages/Integrations';
import Analytics from './pages/Analytics';

// Import components
import Sidebar from './components/Sidebar';
import Header from './components/Header';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  
  // Handle login
  const handleLogin = (credentials) => {
    // In a real app, this would make an API call to authenticate
    console.log('Login with:', credentials);
    setIsAuthenticated(true);
  };
  
  // Handle logout
  const handleLogout = () => {
    setIsAuthenticated(false);
  };
  
  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };
  
  // If not authenticated, show login page
  if (!isAuthenticated) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Login onLogin={handleLogin} />
      </ThemeProvider>
    );
  }
  
  // Main app layout
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        <Header onLogout={handleLogout} darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
        <Sidebar />
        <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/emails" element={<EmailList />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/integrations" element={<Integrations />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
