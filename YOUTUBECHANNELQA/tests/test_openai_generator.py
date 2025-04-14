"""
Test script for OpenAI Generator module

This script tests the functionality of the OpenAI integration module.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.openai_integration.openai_generator import OpenAIGenerator

class TestOpenAIGenerator(unittest.TestCase):
    """Test cases for OpenAIGenerator class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a patcher for the OpenAI client
        self.openai_patcher = patch('src.openai_integration.openai_generator.OpenAI')
        self.mock_openai = self.openai_patcher.start()
        
        # Create mock client
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client
        
        # Create OpenAIGenerator instance with test API key
        self.test_api_key = "test_api_key"
        self.generator = OpenAIGenerator(api_key=self.test_api_key, model="gpt-3.5-turbo")
    
    def tearDown(self):
        """Clean up after tests."""
        self.openai_patcher.stop()
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        self.assertEqual(self.generator.api_key, self.test_api_key)
        self.assertEqual(self.generator.model, "gpt-3.5-turbo")
        self.mock_openai.assert_called_once_with(api_key=self.test_api_key)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'env_api_key'})
    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        generator = OpenAIGenerator()
        self.assertEqual(generator.api_key, 'env_api_key')
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                OpenAIGenerator()
    
    def test_generate_answer(self):
        """Test generate_answer method."""
        # Mock OpenAI API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is the answer."
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call the method
        result = self.generator.generate_answer(
            question="What is the recommended valuation multiple?",
            context="The recommended valuation multiple is typically 4-6x EBITDA for most businesses.",
            temperature=0.3,
            max_tokens=500
        )
        
        # Verify the results
        self.assertEqual(result, "This is the answer.")
        
        # Verify the API call
        self.mock_client.chat.completions.create.assert_called_once()
        call_args = self.mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args['model'], "gpt-3.5-turbo")
        self.assertEqual(call_args['temperature'], 0.3)
        self.assertEqual(call_args['max_tokens'], 500)
        self.assertEqual(len(call_args['messages']), 2)
        self.assertEqual(call_args['messages'][0]['role'], "system")
        self.assertEqual(call_args['messages'][1]['role'], "user")
    
    def test_generate_answer_error(self):
        """Test generate_answer method with error."""
        # Mock OpenAI API error
        self.mock_client.chat.completions.create.side_effect = Exception("API error")
        
        # Call the method
        result = self.generator.generate_answer(
            question="What is the recommended valuation multiple?",
            context="The recommended valuation multiple is typically 4-6x EBITDA for most businesses."
        )
        
        # Verify the results
        self.assertTrue(result.startswith("Sorry, I encountered an error"))
    
    def test_format_context_from_segments(self):
        """Test format_context_from_segments method."""
        # Test segments
        segments = [
            {
                'text': 'The recommended valuation multiple is typically 4-6x EBITDA for most businesses.',
                'video_title': 'Business Valuation Explained',
                'start_time': 135.5
            },
            {
                'text': 'For service businesses, expect multiples between 4-6 times EBITDA depending on growth rate.',
                'video_title': 'Selling Your Business',
                'start_time': 930.2
            }
        ]
        
        # Call the method
        result = self.generator.format_context_from_segments(segments, max_context_length=1000)
        
        # Verify the results
        self.assertIn("Business Valuation Explained", result)
        self.assertIn("02:15", result)
        self.assertIn("Selling Your Business", result)
        self.assertIn("15:30", result)
        self.assertIn("4-6x EBITDA", result)
    
    def test_format_context_from_segments_max_length(self):
        """Test format_context_from_segments method with max length constraint."""
        # Create a very long segment
        long_text = "This is a very long segment text. " * 100
        segments = [
            {
                'text': long_text,
                'video_title': 'Long Video',
                'start_time': 10.0
            },
            {
                'text': 'This should not be included due to max length.',
                'video_title': 'Another Video',
                'start_time': 20.0
            }
        ]
        
        # Call the method with small max length
        result = self.generator.format_context_from_segments(segments, max_context_length=200)
        
        # Verify the results
        self.assertIn("Long Video", result)
        self.assertNotIn("Another Video", result)
        self.assertTrue(len(result) <= 200)
    
    def test_format_time(self):
        """Test _format_time method."""
        # Test various times
        self.assertEqual(self.generator._format_time(0), "00:00")
        self.assertEqual(self.generator._format_time(65), "01:05")
        self.assertEqual(self.generator._format_time(3661), "61:01")
    
    def test_generate_answer_with_references(self):
        """Test generate_answer_with_references method."""
        # Mock generate_answer method
        self.generator.generate_answer = MagicMock(return_value="This is the answer.")
        
        # Mock format_context_from_segments method
        self.generator.format_context_from_segments = MagicMock(return_value="Formatted context")
        
        # Test segments
        segments = [
            {
                'video_id': 'abc123',
                'text': 'The recommended valuation multiple is typically 4-6x EBITDA for most businesses.',
                'video_title': 'Business Valuation Explained',
                'start_time': 135.5
            },
            {
                'video_id': 'def456',
                'text': 'For service businesses, expect multiples between 4-6 times EBITDA depending on growth rate.',
                'video_title': 'Selling Your Business',
                'start_time': 930.2
            }
        ]
        
        # Call the method
        result = self.generator.generate_answer_with_references(
            question="What is the recommended valuation multiple?",
            segments=segments
        )
        
        # Verify the results
        self.assertEqual(result['question'], "What is the recommended valuation multiple?")
        self.assertEqual(result['answer'], "This is the answer.")
        self.assertEqual(len(result['references']), 2)
        self.assertEqual(result['references'][0]['video_id'], "abc123")
        self.assertEqual(result['references'][1]['video_id'], "def456")
        self.assertTrue(result['references'][0]['link'].startswith("https://www.youtube.com/watch?v=abc123"))
        
        # Verify method calls
        self.generator.format_context_from_segments.assert_called_once_with(segments)
        self.generator.generate_answer.assert_called_once_with("What is the recommended valuation multiple?", "Formatted context")

if __name__ == '__main__':
    unittest.main()
