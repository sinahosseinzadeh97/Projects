import React, { useState } from 'react';
import { Container, Typography, Grid, Paper, Box, Button, Card, CardContent, CardActions, Divider, Chip, Switch, FormControlLabel } from '@mui/material';
import { styled } from '@mui/material/styles';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import BusinessIcon from '@mui/icons-material/Business';
import TaskIcon from '@mui/icons-material/Task';
import AddIcon from '@mui/icons-material/Add';
import SyncIcon from '@mui/icons-material/Sync';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

// Styled components
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
}));

const IntegrationCard = styled(Card)(({ theme, connected }) => ({
  marginBottom: theme.spacing(2),
  borderLeft: `4px solid ${connected ? theme.palette.success.main : theme.palette.error.main}`,
}));

function Integrations() {
  // Mock integrations data - in a real app, this would come from API calls
  const [integrations, setIntegrations] = useState({
    calendar: {
      name: 'Google Calendar',
      connected: true,
      lastSync: '2025-04-14T05:30:00Z',
      eventsCreated: 42,
      status: 'active'
    },
    crm: {
      name: 'Salesforce',
      connected: true,
      lastSync: '2025-04-14T06:15:00Z',
      contactsUpdated: 78,
      status: 'active'
    },
    taskManager: {
      name: 'Asana',
      connected: false,
      lastSync: '2025-04-13T12:45:00Z',
      tasksCreated: 23,
      status: 'disconnected'
    }
  });

  // Function to format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Handle toggle integration
  const handleToggleIntegration = (integration) => {
    setIntegrations({
      ...integrations,
      [integration]: {
        ...integrations[integration],
        connected: !integrations[integration].connected,
        status: integrations[integration].connected ? 'disconnected' : 'active'
      }
    });
  };

  // Handle sync integration
  const handleSyncIntegration = (integration) => {
    // In a real app, this would make an API call to sync the integration
    console.log(`Syncing ${integration}...`);
    alert(`Syncing ${integration} integration...`);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        External Integrations
      </Typography>

      <Grid container spacing={3}>
        {/* Calendar Integration */}
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <CalendarMonthIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">
                Calendar Integration
              </Typography>
            </Box>
            
            <IntegrationCard connected={integrations.calendar.connected}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" component="div">
                    {integrations.calendar.name}
                  </Typography>
                  <Chip 
                    label={integrations.calendar.status} 
                    color={integrations.calendar.connected ? "success" : "error"} 
                    size="small"
                    icon={integrations.calendar.connected ? <CheckCircleIcon /> : <ErrorIcon />}
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Last Synchronized: {formatDate(integrations.calendar.lastSync)}
                </Typography>
                
                <Typography variant="body2" color="text.secondary">
                  Events Created: {integrations.calendar.eventsCreated}
                </Typography>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={integrations.calendar.connected}
                      onChange={() => handleToggleIntegration('calendar')}
                      color="primary"
                    />
                  }
                  label={integrations.calendar.connected ? "Connected" : "Disconnected"}
                  sx={{ mt: 2 }}
                />
              </CardContent>
              <Divider />
              <CardActions>
                <Button 
                  size="small" 
                  startIcon={<SyncIcon />}
                  onClick={() => handleSyncIntegration('calendar')}
                  disabled={!integrations.calendar.connected}
                >
                  Sync Now
                </Button>
                <Button 
                  size="small" 
                  startIcon={<AddIcon />}
                  disabled={!integrations.calendar.connected}
                >
                  Create Event
                </Button>
              </CardActions>
            </IntegrationCard>
            
            <Button variant="outlined" fullWidth>
              Configure Calendar Settings
            </Button>
          </StyledPaper>
        </Grid>

        {/* CRM Integration */}
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <BusinessIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">
                CRM Integration
              </Typography>
            </Box>
            
            <IntegrationCard connected={integrations.crm.connected}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" component="div">
                    {integrations.crm.name}
                  </Typography>
                  <Chip 
                    label={integrations.crm.status} 
                    color={integrations.crm.connected ? "success" : "error"} 
                    size="small"
                    icon={integrations.crm.connected ? <CheckCircleIcon /> : <ErrorIcon />}
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Last Synchronized: {formatDate(integrations.crm.lastSync)}
                </Typography>
                
                <Typography variant="body2" color="text.secondary">
                  Contacts Updated: {integrations.crm.contactsUpdated}
                </Typography>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={integrations.crm.connected}
                      onChange={() => handleToggleIntegration('crm')}
                      color="primary"
                    />
                  }
                  label={integrations.crm.connected ? "Connected" : "Disconnected"}
                  sx={{ mt: 2 }}
                />
              </CardContent>
              <Divider />
              <CardActions>
                <Button 
                  size="small" 
                  startIcon={<SyncIcon />}
                  onClick={() => handleSyncIntegration('crm')}
                  disabled={!integrations.crm.connected}
                >
                  Sync Now
                </Button>
                <Button 
                  size="small" 
                  startIcon={<AddIcon />}
                  disabled={!integrations.crm.connected}
                >
                  Add Contact
                </Button>
              </CardActions>
            </IntegrationCard>
            
            <Button variant="outlined" fullWidth>
              Configure CRM Settings
            </Button>
          </StyledPaper>
        </Grid>

        {/* Task Manager Integration */}
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <TaskIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">
                Task Manager Integration
              </Typography>
            </Box>
            
            <IntegrationCard connected={integrations.taskManager.connected}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" component="div">
                    {integrations.taskManager.name}
                  </Typography>
                  <Chip 
                    label={integrations.taskManager.status} 
                    color={integrations.taskManager.connected ? "success" : "error"} 
                    size="small"
                    icon={integrations.taskManager.connected ? <CheckCircleIcon /> : <ErrorIcon />}
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Last Synchronized: {formatDate(integrations.taskManager.lastSync)}
                </Typography>
                
                <Typography variant="body2" color="text.secondary">
                  Tasks Created: {integrations.taskManager.tasksCreated}
                </Typography>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={integrations.taskManager.connected}
                      onChange={() => handleToggleIntegration('taskManager')}
                      color="primary"
                    />
                  }
                  label={integrations.taskManager.connected ? "Connected" : "Disconnected"}
                  sx={{ mt: 2 }}
                />
              </CardContent>
              <Divider />
              <CardActions>
                <Button 
                  size="small" 
                  startIcon={<SyncIcon />}
                  onClick={() => handleSyncIntegration('taskManager')}
                  disabled={!integrations.taskManager.connected}
                >
                  Sync Now
                </Button>
                <Button 
                  size="small" 
                  startIcon={<AddIcon />}
                  disabled={!integrations.taskManager.connected}
                >
                  Create Task
                </Button>
              </CardActions>
            </IntegrationCard>
            
            <Button variant="outlined" fullWidth>
              Configure Task Manager Settings
            </Button>
          </StyledPaper>
        </Grid>

        {/* Add New Integration */}
        <Grid item xs={12}>
          <StyledPaper>
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 3 }}>
              <Button 
                variant="contained" 
                startIcon={<AddIcon />}
                size="large"
              >
                Add New Integration
              </Button>
            </Box>
          </StyledPaper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Integrations;
