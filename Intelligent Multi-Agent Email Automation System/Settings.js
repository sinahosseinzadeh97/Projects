import React, { useState } from 'react';
import { Container, Typography, Grid, Paper, Box, Button, TextField, FormControl, InputLabel, Select, MenuItem, Switch, FormControlLabel } from '@mui/material';
import { styled } from '@mui/material/styles';
import SaveIcon from '@mui/icons-material/Save';

// Styled components
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
}));

function Settings() {
  // Mock settings - in a real app, these would be loaded from API
  const [settings, setSettings] = useState({
    emailIngestion: {
      batchSize: 10,
      pollingInterval: 300, // seconds
    },
    classification: {
      modelType: 'bert',
      categories: ['important', 'promotional', 'support', 'spam', 'other'],
      threshold: 0.7,
    },
    summarization: {
      modelType: 'gpt',
      summaryMaxLength: 150,
    },
    responseGeneration: {
      modelType: 'gpt',
      autoSendThreshold: 0.9,
    },
    integration: {
      autoSendEnabled: true,
      batchSize: 10,
      calendar: {
        enabled: true,
        service: 'google_calendar',
      },
      crm: {
        enabled: true,
        service: 'salesforce',
      },
      taskManager: {
        enabled: true,
        service: 'asana',
      },
    },
  });

  // Handle settings change
  const handleSettingChange = (section, field, value) => {
    setSettings({
      ...settings,
      [section]: {
        ...settings[section],
        [field]: value,
      },
    });
  };

  // Handle integration setting change
  const handleIntegrationSettingChange = (integration, field, value) => {
    setSettings({
      ...settings,
      integration: {
        ...settings.integration,
        [integration]: {
          ...settings.integration[integration],
          [field]: value,
        },
      },
    });
  };

  // Handle save settings
  const handleSaveSettings = () => {
    // In a real app, this would make an API call to save settings
    console.log('Saving settings:', settings);
    alert('Settings saved successfully!');
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          System Settings
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<SaveIcon />}
          onClick={handleSaveSettings}
        >
          Save Settings
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Email Ingestion Settings */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Email Ingestion Settings
            </Typography>
            
            <TextField
              label="Batch Size"
              type="number"
              value={settings.emailIngestion.batchSize}
              onChange={(e) => handleSettingChange('emailIngestion', 'batchSize', parseInt(e.target.value))}
              fullWidth
              margin="normal"
              helperText="Maximum number of emails to fetch in one batch"
            />
            
            <TextField
              label="Polling Interval (seconds)"
              type="number"
              value={settings.emailIngestion.pollingInterval}
              onChange={(e) => handleSettingChange('emailIngestion', 'pollingInterval', parseInt(e.target.value))}
              fullWidth
              margin="normal"
              helperText="Time between email fetching operations"
            />
          </StyledPaper>
        </Grid>

        {/* Classification Settings */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Classification Settings
            </Typography>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Model Type</InputLabel>
              <Select
                value={settings.classification.modelType}
                label="Model Type"
                onChange={(e) => handleSettingChange('classification', 'modelType', e.target.value)}
              >
                <MenuItem value="bert">BERT</MenuItem>
                <MenuItem value="distilbert">DistilBERT</MenuItem>
                <MenuItem value="roberta">RoBERTa</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              label="Confidence Threshold"
              type="number"
              value={settings.classification.threshold}
              onChange={(e) => handleSettingChange('classification', 'threshold', parseFloat(e.target.value))}
              fullWidth
              margin="normal"
              inputProps={{ min: 0, max: 1, step: 0.1 }}
              helperText="Minimum confidence level for classification (0-1)"
            />
          </StyledPaper>
        </Grid>

        {/* Summarization Settings */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Summarization Settings
            </Typography>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Model Type</InputLabel>
              <Select
                value={settings.summarization.modelType}
                label="Model Type"
                onChange={(e) => handleSettingChange('summarization', 'modelType', e.target.value)}
              >
                <MenuItem value="gpt">GPT</MenuItem>
                <MenuItem value="t5">T5</MenuItem>
                <MenuItem value="bart">BART</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              label="Summary Max Length"
              type="number"
              value={settings.summarization.summaryMaxLength}
              onChange={(e) => handleSettingChange('summarization', 'summaryMaxLength', parseInt(e.target.value))}
              fullWidth
              margin="normal"
              helperText="Maximum length of generated summaries"
            />
          </StyledPaper>
        </Grid>

        {/* Response Generation Settings */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Response Generation Settings
            </Typography>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Model Type</InputLabel>
              <Select
                value={settings.responseGeneration.modelType}
                label="Model Type"
                onChange={(e) => handleSettingChange('responseGeneration', 'modelType', e.target.value)}
              >
                <MenuItem value="gpt">GPT</MenuItem>
                <MenuItem value="t5">T5</MenuItem>
                <MenuItem value="bart">BART</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              label="Auto-Send Threshold"
              type="number"
              value={settings.responseGeneration.autoSendThreshold}
              onChange={(e) => handleSettingChange('responseGeneration', 'autoSendThreshold', parseFloat(e.target.value))}
              fullWidth
              margin="normal"
              inputProps={{ min: 0, max: 1, step: 0.1 }}
              helperText="Minimum confidence level for auto-sending responses (0-1)"
            />
          </StyledPaper>
        </Grid>

        {/* Integration Settings */}
        <Grid item xs={12}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Integration Settings
            </Typography>
            
            <FormControlLabel
              control={
                <Switch
                  checked={settings.integration.autoSendEnabled}
                  onChange={(e) => handleSettingChange('integration', 'autoSendEnabled', e.target.checked)}
                />
              }
              label="Enable Auto-Send for Responses"
              sx={{ mb: 2 }}
            />
            
            <TextField
              label="Batch Size"
              type="number"
              value={settings.integration.batchSize}
              onChange={(e) => handleSettingChange('integration', 'batchSize', parseInt(e.target.value))}
              fullWidth
              margin="normal"
              helperText="Maximum number of emails to process in one workflow run"
              sx={{ mb: 3 }}
            />
            
            <Grid container spacing={3}>
              {/* Calendar Integration */}
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Calendar Integration
                  </Typography>
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.integration.calendar.enabled}
                        onChange={(e) => handleIntegrationSettingChange('calendar', 'enabled', e.target.checked)}
                      />
                    }
                    label="Enable"
                    sx={{ mb: 2, display: 'block' }}
                  />
                  
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Service</InputLabel>
                    <Select
                      value={settings.integration.calendar.service}
                      label="Service"
                      onChange={(e) => handleIntegrationSettingChange('calendar', 'service', e.target.value)}
                      disabled={!settings.integration.calendar.enabled}
                    >
                      <MenuItem value="google_calendar">Google Calendar</MenuItem>
                      <MenuItem value="outlook_calendar">Outlook Calendar</MenuItem>
                      <MenuItem value="ical">iCal</MenuItem>
                    </Select>
                  </FormControl>
                </Paper>
              </Grid>
              
              {/* CRM Integration */}
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    CRM Integration
                  </Typography>
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.integration.crm.enabled}
                        onChange={(e) => handleIntegrationSettingChange('crm', 'enabled', e.target.checked)}
                      />
                    }
                    label="Enable"
                    sx={{ mb: 2, display: 'block' }}
                  />
                  
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Service</InputLabel>
                    <Select
                      value={settings.integration.crm.service}
                      label="Service"
                      onChange={(e) => handleIntegrationSettingChange('crm', 'service', e.target.value)}
                      disabled={!settings.integration.crm.enabled}
                    >
                      <MenuItem value="salesforce">Salesforce</MenuItem>
                      <MenuItem value="hubspot">HubSpot</MenuItem>
                      <MenuItem value="zoho">Zoho CRM</MenuItem>
                    </Select>
                  </FormControl>
                </Paper>
              </Grid>
              
              {/* Task Manager Integration */}
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Task Manager Integration
                  </Typography>
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.integration.taskManager.enabled}
                        onChange={(e) => handleIntegrationSettingChange('taskManager', 'enabled', e.target.checked)}
                      />
                    }
                    label="Enable"
                    sx={{ mb: 2, display: 'block' }}
                  />
                  
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Service</InputLabel>
                    <Select
                      value={settings.integration.taskManager.service}
                      label="Service"
                      onChange={(e) => handleIntegrationSettingChange('taskManager', 'service', e.target.value)}
                      disabled={!settings.integration.taskManager.enabled}
                    >
                      <MenuItem value="asana">Asana</MenuItem>
                      <MenuItem value="trello">Trello</MenuItem>
                      <MenuItem value="jira">Jira</MenuItem>
                    </Select>
                  </FormControl>
                </Paper>
              </Grid>
            </Grid>
          </StyledPaper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Settings;
