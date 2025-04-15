import React from 'react';
import { AppBar, Toolbar, Typography, Button, IconButton, Switch, FormControlLabel } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import AccountCircle from '@mui/icons-material/AccountCircle';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';

function Header({ onLogout, darkMode, toggleDarkMode }) {
  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Email Automation System
        </Typography>
        
        <FormControlLabel
          control={
            <Switch
              checked={darkMode}
              onChange={toggleDarkMode}
              color="default"
            />
          }
          label={darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
        />
        
        <IconButton
          color="inherit"
          aria-label="account"
          sx={{ ml: 2 }}
        >
          <AccountCircle />
        </IconButton>
        
        <Button color="inherit" onClick={onLogout}>Logout</Button>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
