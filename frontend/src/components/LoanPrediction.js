import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Grid,
  CircularProgress,
} from '@material-ui/core';
import axios from 'axios';

const LoanPrediction = () => {
  const [formData, setFormData] = useState({
    creditScore: '',
    income: '',
    loanAmount: '',
    loanTerm: '',
    employmentLength: '',
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('https://your-heroku-app.herokuapp.com/api/predict', formData);
      setPrediction(response.data.prediction);
    } catch (err) {
      setError('Error making prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" style={{ marginTop: '2rem' }}>
      <Paper elevation={3} style={{ padding: '2rem' }}>
        <Typography variant="h4" gutterBottom>
          Loan Prediction
        </Typography>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Credit Score"
                name="creditScore"
                type="number"
                value={formData.creditScore}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Income"
                name="income"
                type="number"
                value={formData.income}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Loan Amount"
                name="loanAmount"
                type="number"
                value={formData.loanAmount}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Loan Term (months)"
                name="loanTerm"
                type="number"
                value={formData.loanTerm}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Employment Length (years)"
                name="employmentLength"
                type="number"
                value={formData.employmentLength}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Predict'}
              </Button>
            </Grid>
          </Grid>
        </form>

        {error && (
          <Typography color="error" style={{ marginTop: '1rem' }}>
            {error}
          </Typography>
        )}

        {prediction && (
          <Paper elevation={2} style={{ marginTop: '2rem', padding: '1rem' }}>
            <Typography variant="h6">Prediction Result:</Typography>
            <Typography variant="body1">
              {prediction === 1 ? 'Loan Approved' : 'Loan Rejected'}
            </Typography>
          </Paper>
        )}
      </Paper>
    </Container>
  );
};

export default LoanPrediction; 