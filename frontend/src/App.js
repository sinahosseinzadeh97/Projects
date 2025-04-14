import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import LoanPrediction from './components/LoanPrediction';
import Dashboard from './components/Dashboard';
import Navbar from './components/Navbar';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<LoanPrediction />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App; 