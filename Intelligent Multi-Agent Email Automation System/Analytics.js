import React, { useState } from 'react';
import { Container, Typography, Grid, Paper, Box, Card, CardContent, Tabs, Tab, Divider } from '@mui/material';
import { styled } from '@mui/material/styles';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Styled components
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
}));

function Analytics() {
  const [timeRange, setTimeRange] = useState(0);

  // Mock data - in a real app, this would come from API calls
  const emailVolumeData = [
    { name: 'Mon', count: 32 },
    { name: 'Tue', count: 45 },
    { name: 'Wed', count: 38 },
    { name: 'Thu', count: 52 },
    { name: 'Fri', count: 48 },
    { name: 'Sat', count: 23 },
    { name: 'Sun', count: 18 },
  ];

  const categoryDistributionData = [
    { name: 'Important', value: 35 },
    { name: 'Promotional', value: 40 },
    { name: 'Support', value: 15 },
    { name: 'Spam', value: 5 },
    { name: 'Other', value: 5 },
  ];

  const responseRateData = [
    { name: 'Mon', rate: 85 },
    { name: 'Tue', rate: 92 },
    { name: 'Wed', rate: 88 },
    { name: 'Thu', rate: 95 },
    { name: 'Fri', rate: 90 },
    { name: 'Sat', rate: 82 },
    { name: 'Sun', rate: 78 },
  ];

  const integrationUsageData = [
    { name: 'Calendar', count: 42 },
    { name: 'CRM', count: 78 },
    { name: 'Task Manager', count: 23 },
  ];

  // Colors for pie chart
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTimeRange(newValue);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Analytics Dashboard
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={timeRange} onChange={handleTabChange} aria-label="time range tabs">
          <Tab label="Last 7 Days" />
          <Tab label="Last 30 Days" />
          <Tab label="Last 90 Days" />
          <Tab label="Custom Range" />
        </Tabs>
      </Box>

      <Grid container spacing={3}>
        {/* Email Volume Chart */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Email Volume
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={emailVolumeData}
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#8884d8" name="Email Count" />
              </BarChart>
            </ResponsiveContainer>
          </StyledPaper>
        </Grid>

        {/* Category Distribution Chart */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Email Category Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryDistributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={true}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value} emails`} />
              </PieChart>
            </ResponsiveContainer>
          </StyledPaper>
        </Grid>

        {/* Response Rate Chart */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Response Rate
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={responseRateData}
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `${value}%`} />
                <Legend />
                <Bar dataKey="rate" fill="#00C49F" name="Response Rate (%)" />
              </BarChart>
            </ResponsiveContainer>
          </StyledPaper>
        </Grid>

        {/* Integration Usage Chart */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Integration Usage
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={integrationUsageData}
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#FFBB28" name="Usage Count" />
              </BarChart>
            </ResponsiveContainer>
          </StyledPaper>
        </Grid>

        {/* Summary Stats */}
        <Grid item xs={12}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Performance Summary
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h5" component="div">
                      256
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Emails Processed
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h5" component="div">
                      89%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Average Response Rate
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h5" component="div">
                      3.2 min
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Average Processing Time
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h5" component="div">
                      143
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Integration Actions
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </StyledPaper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Analytics;
