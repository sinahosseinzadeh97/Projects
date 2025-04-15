import React, { useState } from 'react';
import { Container, Typography, Grid, Paper, Box, Button, TextField } from '@mui/material';
import { styled } from '@mui/material/styles';
import EmailIcon from '@mui/icons-material/Email';
import CategoryIcon from '@mui/icons-material/Category';
import SummarizeIcon from '@mui/icons-material/Summarize';
import ReplyIcon from '@mui/icons-material/Reply';
import IntegrationInstructionsIcon from '@mui/icons-material/IntegrationInstructions';

// Styled components
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
}));

const StatBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  backgroundColor: theme.palette.background.default,
  borderRadius: theme.shape.borderRadius,
}));

const IconWrapper = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: 48,
  height: 48,
  borderRadius: '50%',
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
}));

function Dashboard() {
  // Mock data - in a real app, this would come from API calls
  const [stats, setStats] = useState({
    emailsProcessed: 152,
    emailsClassified: 152,
    emailsSummarized: 148,
    responsesGenerated: 145,
    integrationsCompleted: 87,
  });

  const [recentEmails, setRecentEmails] = useState([
    { id: 1, subject: 'Project Update Meeting', from: 'john.doe@example.com', category: 'important', timestamp: '2025-04-14T06:30:00Z' },
    { id: 2, subject: 'Weekly Newsletter', from: 'newsletter@company.com', category: 'promotional', timestamp: '2025-04-14T05:45:00Z' },
    { id: 3, subject: 'Support Request #12345', from: 'customer@client.org', category: 'support', timestamp: '2025-04-14T04:20:00Z' },
    { id: 4, subject: 'Invoice for April 2025', from: 'billing@vendor.net', category: 'important', timestamp: '2025-04-14T03:15:00Z' },
  ]);

  // Function to format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Stats Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            <StatBox>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Emails Processed
                </Typography>
                <Typography variant="h5">{stats.emailsProcessed}</Typography>
              </Box>
              <IconWrapper>
                <EmailIcon />
              </IconWrapper>
            </StatBox>
            <StatBox>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Emails Classified
                </Typography>
                <Typography variant="h5">{stats.emailsClassified}</Typography>
              </Box>
              <IconWrapper>
                <CategoryIcon />
              </IconWrapper>
            </StatBox>
            <StatBox>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Emails Summarized
                </Typography>
                <Typography variant="h5">{stats.emailsSummarized}</Typography>
              </Box>
              <IconWrapper>
                <SummarizeIcon />
              </IconWrapper>
            </StatBox>
            <StatBox>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Responses Generated
                </Typography>
                <Typography variant="h5">{stats.responsesGenerated}</Typography>
              </Box>
              <IconWrapper>
                <ReplyIcon />
              </IconWrapper>
            </StatBox>
            <StatBox>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Integrations Completed
                </Typography>
                <Typography variant="h5">{stats.integrationsCompleted}</Typography>
              </Box>
              <IconWrapper>
                <IntegrationInstructionsIcon />
              </IconWrapper>
            </StatBox>
          </StyledPaper>
        </Grid>

        <Grid item xs={12} md={8}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Recent Emails
            </Typography>
            <Box sx={{ mb: 2 }}>
              <TextField
                fullWidth
                label="Search Emails"
                variant="outlined"
                size="small"
                sx={{ mb: 2 }}
              />
              {recentEmails.map((email) => (
                <Paper
                  key={email.id}
                  elevation={1}
                  sx={{ p: 2, mb: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                >
                  <Box>
                    <Typography variant="subtitle1">{email.subject}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      From: {email.from}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box
                      sx={{
                        backgroundColor: 
                          email.category === 'important' ? 'error.light' :
                          email.category === 'promotional' ? 'info.light' :
                          email.category === 'support' ? 'warning.light' : 'grey.300',
                        px: 1,
                        py: 0.5,
                        borderRadius: 1,
                        mr: 2
                      }}
                    >
                      <Typography variant="caption">{email.category}</Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      {formatDate(email.timestamp)}
                    </Typography>
                  </Box>
                </Paper>
              ))}
              <Button variant="text" sx={{ mt: 1 }}>
                View All Emails
              </Button>
            </Box>
          </StyledPaper>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button variant="contained" startIcon={<EmailIcon />}>
                Fetch New Emails
              </Button>
              <Button variant="outlined" startIcon={<ReplyIcon />}>
                Review Responses
              </Button>
              <Button variant="outlined" startIcon={<IntegrationInstructionsIcon />}>
                Manage Integrations
              </Button>
            </Box>
          </StyledPaper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
