import React from 'react';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Toolbar, Divider } from '@mui/material';
import { Link } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import EmailIcon from '@mui/icons-material/Email';
import SettingsIcon from '@mui/icons-material/Settings';
import IntegrationInstructionsIcon from '@mui/icons-material/IntegrationInstructions';
import BarChartIcon from '@mui/icons-material/BarChart';

const drawerWidth = 240;

function Sidebar() {
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <div>
        <List>
          <ListItem button component={Link} to="/">
            <ListItemIcon>
              <DashboardIcon />
            </ListItemIcon>
            <ListItemText primary="Dashboard" />
          </ListItem>
          
          <ListItem button component={Link} to="/emails">
            <ListItemIcon>
              <EmailIcon />
            </ListItemIcon>
            <ListItemText primary="Emails" />
          </ListItem>
          
          <ListItem button component={Link} to="/integrations">
            <ListItemIcon>
              <IntegrationInstructionsIcon />
            </ListItemIcon>
            <ListItemText primary="Integrations" />
          </ListItem>
          
          <ListItem button component={Link} to="/analytics">
            <ListItemIcon>
              <BarChartIcon />
            </ListItemIcon>
            <ListItemText primary="Analytics" />
          </ListItem>
        </List>
        
        <Divider />
        
        <List>
          <ListItem button component={Link} to="/settings">
            <ListItemIcon>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItem>
        </List>
      </div>
    </Drawer>
  );
}

export default Sidebar;
