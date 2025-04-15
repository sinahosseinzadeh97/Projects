import React, { useState } from 'react';
import { Container, Typography, Grid, Paper, Box, Button, TextField, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, IconButton } from '@mui/material';
import { styled } from '@mui/material/styles';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ReplyIcon from '@mui/icons-material/Reply';
import DeleteIcon from '@mui/icons-material/Delete';
import FilterListIcon from '@mui/icons-material/FilterList';

// Styled components
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
}));

function EmailList() {
  // Mock data - in a real app, this would come from API calls
  const [emails, setEmails] = useState([
    { 
      id: 1, 
      subject: 'Project Update Meeting', 
      from: 'john.doe@example.com', 
      category: 'important', 
      timestamp: '2025-04-14T06:30:00Z',
      summary: 'Weekly project update meeting scheduled for Tuesday at 2 PM.',
      hasResponse: true
    },
    { 
      id: 2, 
      subject: 'Weekly Newsletter', 
      from: 'newsletter@company.com', 
      category: 'promotional', 
      timestamp: '2025-04-14T05:45:00Z',
      summary: 'Company newsletter with updates on new products and events.',
      hasResponse: false
    },
    { 
      id: 3, 
      subject: 'Support Request #12345', 
      from: 'customer@client.org', 
      category: 'support', 
      timestamp: '2025-04-14T04:20:00Z',
      summary: 'Customer reporting issues with login functionality on mobile app.',
      hasResponse: true
    },
    { 
      id: 4, 
      subject: 'Invoice for April 2025', 
      from: 'billing@vendor.net', 
      category: 'important', 
      timestamp: '2025-04-14T03:15:00Z',
      summary: 'Monthly invoice for services provided in April 2025.',
      hasResponse: true
    },
    { 
      id: 5, 
      subject: 'Special Offer - 50% Off', 
      from: 'marketing@retailer.com', 
      category: 'promotional', 
      timestamp: '2025-04-14T02:10:00Z',
      summary: 'Limited time offer with 50% discount on selected products.',
      hasResponse: false
    },
    { 
      id: 6, 
      subject: 'Meeting Minutes - Strategy Session', 
      from: 'secretary@company.com', 
      category: 'important', 
      timestamp: '2025-04-14T01:05:00Z',
      summary: 'Minutes from yesterday\'s strategy planning session with action items.',
      hasResponse: true
    },
    { 
      id: 7, 
      subject: 'System Maintenance Notification', 
      from: 'it@company.com', 
      category: 'other', 
      timestamp: '2025-04-13T23:30:00Z',
      summary: 'Scheduled system maintenance on Saturday from 10 PM to 2 AM.',
      hasResponse: false
    },
  ]);

  // Function to format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Get category color
  const getCategoryColor = (category) => {
    switch(category) {
      case 'important':
        return 'error';
      case 'promotional':
        return 'info';
      case 'support':
        return 'warning';
      case 'spam':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Email Management
      </Typography>

      <StyledPaper>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <TextField
            label="Search Emails"
            variant="outlined"
            size="small"
            sx={{ width: '40%' }}
          />
          <Box>
            <Button 
              variant="outlined" 
              startIcon={<FilterListIcon />}
              sx={{ mr: 2 }}
            >
              Filter
            </Button>
            <Button 
              variant="contained"
            >
              Fetch New Emails
            </Button>
          </Box>
        </Box>

        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }} aria-label="email table">
            <TableHead>
              <TableRow>
                <TableCell>Subject</TableCell>
                <TableCell>From</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Summary</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {emails.map((email) => (
                <TableRow
                  key={email.id}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    {email.subject}
                  </TableCell>
                  <TableCell>{email.from}</TableCell>
                  <TableCell>
                    <Chip 
                      label={email.category} 
                      color={getCategoryColor(email.category)} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>{email.summary}</TableCell>
                  <TableCell>{formatDate(email.timestamp)}</TableCell>
                  <TableCell>
                    <IconButton size="small" aria-label="view">
                      <VisibilityIcon fontSize="small" />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      aria-label="reply"
                      color={email.hasResponse ? "primary" : "default"}
                    >
                      <ReplyIcon fontSize="small" />
                    </IconButton>
                    <IconButton size="small" aria-label="delete" color="error">
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </StyledPaper>
    </Container>
  );
}

export default EmailList;
