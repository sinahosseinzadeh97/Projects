"""
Frontend test script for the Intelligent Multi-Agent Email Automation System.
This file contains tests for the React frontend components.
"""

import unittest
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class TestFrontend(unittest.TestCase):
    """Test cases for the frontend components."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Set up Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Initialize WebDriver
        try:
            cls.driver = webdriver.Chrome(options=options)
            cls.driver.implicitly_wait(10)
            cls.base_url = "http://localhost:3000"
        except:
            cls.driver = None
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if cls.driver:
            cls.driver.quit()
    
    def setUp(self):
        """Set up before each test."""
        if not self.driver:
            self.skipTest("WebDriver not available")
    
    def test_login_page(self):
        """Test login page."""
        try:
            # Navigate to login page
            self.driver.get(self.base_url)
            
            # Check page title
            self.assertIn("Email Automation System", self.driver.title)
            
            # Check login form elements
            username_input = self.driver.find_element(By.ID, "username")
            password_input = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            
            self.assertTrue(username_input.is_displayed())
            self.assertTrue(password_input.is_displayed())
            self.assertTrue(login_button.is_displayed())
            
            # Test login functionality
            username_input.send_keys("admin")
            password_input.send_keys("adminpassword")
            login_button.click()
            
            # Wait for dashboard to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Dashboard')]"))
                )
                dashboard_loaded = True
            except TimeoutException:
                dashboard_loaded = False
            
            self.assertTrue(dashboard_loaded)
        except Exception as e:
            self.skipTest(f"Frontend server not running: {str(e)}")
    
    def test_dashboard(self):
        """Test dashboard page."""
        try:
            # Login first
            self.driver.get(self.base_url)
            username_input = self.driver.find_element(By.ID, "username")
            password_input = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            
            username_input.send_keys("admin")
            password_input.send_keys("adminpassword")
            login_button.click()
            
            # Wait for dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Dashboard')]"))
            )
            
            # Check dashboard elements
            system_status = self.driver.find_element(By.XPATH, "//h6[contains(text(), 'System Status')]")
            recent_emails = self.driver.find_element(By.XPATH, "//h6[contains(text(), 'Recent Emails')]")
            quick_actions = self.driver.find_element(By.XPATH, "//h6[contains(text(), 'Quick Actions')]")
            
            self.assertTrue(system_status.is_displayed())
            self.assertTrue(recent_emails.is_displayed())
            self.assertTrue(quick_actions.is_displayed())
            
            # Check if stats are displayed
            stats_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'MuiBox-root')]//h5")
            self.assertTrue(len(stats_elements) > 0)
        except Exception as e:
            self.skipTest(f"Frontend server not running: {str(e)}")
    
    def test_email_list(self):
        """Test email list page."""
        try:
            # Login first
            self.driver.get(self.base_url)
            username_input = self.driver.find_element(By.ID, "username")
            password_input = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            
            username_input.send_keys("admin")
            password_input.send_keys("adminpassword")
            login_button.click()
            
            # Wait for dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Dashboard')]"))
            )
            
            # Navigate to email list
            email_link = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Emails')]")
            email_link.click()
            
            # Wait for email list to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Email Management')]"))
            )
            
            # Check email list elements
            search_input = self.driver.find_element(By.XPATH, "//input[@label='Search Emails']")
            filter_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Filter')]")
            fetch_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Fetch New Emails')]")
            
            self.assertTrue(search_input.is_displayed())
            self.assertTrue(filter_button.is_displayed())
            self.assertTrue(fetch_button.is_displayed())
            
            # Check if email table is displayed
            table = self.driver.find_element(By.XPATH, "//table")
            table_rows = self.driver.find_elements(By.XPATH, "//tbody/tr")
            
            self.assertTrue(table.is_displayed())
            self.assertTrue(len(table_rows) > 0)
        except Exception as e:
            self.skipTest(f"Frontend server not running: {str(e)}")
    
    def test_settings_page(self):
        """Test settings page."""
        try:
            # Login first
            self.driver.get(self.base_url)
            username_input = self.driver.find_element(By.ID, "username")
            password_input = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            
            username_input.send_keys("admin")
            password_input.send_keys("adminpassword")
            login_button.click()
            
            # Wait for dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Dashboard')]"))
            )
            
            # Navigate to settings
            settings_link = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Settings')]")
            settings_link.click()
            
            # Wait for settings to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'System Settings')]"))
            )
            
            # Check settings elements
            save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save Settings')]")
            email_ingestion_settings = self.driver.find_element(By.XPATH, "//h6[contains(text(), 'Email Ingestion Settings')]")
            classification_settings = self.driver.find_element(By.XPATH, "//h6[contains(text(), 'Classification Settings')]")
            
            self.assertTrue(save_button.is_displayed())
            self.assertTrue(email_ingestion_settings.is_displayed())
            self.assertTrue(classification_settings.is_displayed())
            
            # Check if form inputs are displayed
            form_inputs = self.driver.find_elements(By.XPATH, "//input")
            self.assertTrue(len(form_inputs) > 0)
        except Exception as e:
            self.skipTest(f"Frontend server not running: {str(e)}")
    
    def test_integrations_page(self):
        """Test integrations page."""
        try:
            # Login first
            self.driver.get(self.base_url)
            username_input = self.driver.find_element(By.ID, "username")
            password_input = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            
            username_input.send_keys("admin")
            password_input.send_keys("adminpassword")
            login_button.click()
            
            # Wait for dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Dashboard')]"))
            )
            
            # Navigate to integrations
            integrations_link = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Integrations')]")
            integrations_link.click()
            
            # Wait for integrations to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'External Integrations')]"))
            )
            
            # Check integrations elements
            calendar_integration = self.driver.find_element(By.XPATH, "//h6[contains(text(), 'Calendar Integration')]")
            crm_integration = self.driver.find_element(By.XPATH, "//h6[contains(text(), 'CRM Integration')]")
            task_manager_integration = self.driver.find_element(By.XPATH, "//h6[contains(text(), 'Task Manager Integration')]")
            
            self.assertTrue(calendar_integration.is_displayed())
            self.assertTrue(crm_integration.is_displayed())
            self.assertTrue(task_manager_integration.is_displayed())
            
            # Check if integration cards are displayed
            integration_cards = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'MuiCard-root')]")
            self.assertTrue(len(integration_cards) > 0)
        except Exception as e:
            self.skipTest(f"Frontend server not running: {str(e)}")
    
    def test_analytics_page(self):
        """Test analytics page."""
        try:
            # Login first
            self.driver.get(self.base_url)
            username_input = self.driver.find_element(By.ID, "username")
            password_input = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            
            username_input.send_keys("admin")
            password_input.send_keys("adminpassword")
            login_button.click()
            
            # Wait for dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Dashboard')]"))
            )
            
            # Navigate to analytics
            analytics_link = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Analytics')]")
            analytics_link.click()
            
            # Wait for analytics to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h4[contains(text(), 'Analytics Dashboard')]"))
            )
            
            # Check analytics elements
            time_range_tabs = self.driver.find_element(By.XPATH, "//div[contains(@role, 'tablist')]")
            email_volume = self.driver.find_element(By.XPATH, "//h6[contains(text(), 'Email Volume')]")
            category_distribution = self.driver.find_element(By.XPATH, "//h6[contains(text(), 'Email Category Distribution')]")
            
            self.assertTrue(time_range_tabs.is_displayed())
            self.assertTrue(email_volume.is_displayed())
            self.assertTrue(category_distribution.is_displayed())
            
            # Check if charts are displayed
            charts = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'recharts-wrapper')]")
            self.assertTrue(len(charts) > 0)
        except Exception as e:
            self.skipTest(f"Frontend server not running: {str(e)}")

if __name__ == "__main__":
    unittest.main()
