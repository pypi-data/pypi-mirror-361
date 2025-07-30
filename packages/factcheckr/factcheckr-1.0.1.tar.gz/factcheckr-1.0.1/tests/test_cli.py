#!/usr/bin/env python3
"""
Test cases for CLI functionality.
"""

import unittest
import sys
import json
from io import StringIO
from unittest.mock import patch, Mock

# Add the src directory to the path
sys.path.insert(0, 'src')
from factcheckr.cli import main, format_output


class TestCLI(unittest.TestCase):
    """Test cases for CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_checker = Mock()
        self.mock_checker.fact_check.return_value = json.dumps({
            'claims': [{
                'claim': 'Test claim',
                'verdict': 'True',
                'evidence': 'Test evidence',
                'confidence': 0.9
            }]
        })
        self.mock_checker.ai_available = True
    
    @patch('sys.argv', ['factcheckr', '--help'])
    def test_main_help(self):
        """Test help argument."""
        with self.assertRaises(SystemExit):
            main()
    
    @patch('sys.argv', ['factcheckr', '--version'])
    def test_main_version(self):
        """Test version argument."""
        with self.assertRaises(SystemExit):
            main()
    
    @patch('factcheckr.cli.CompleteFactCheckr')
    @patch('sys.argv', ['factcheckr', 'Test claim'])
    def test_main_single_claim(self, mock_checker_class):
        """Test single claim processing."""
        mock_checker_class.return_value = self.mock_checker
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            self.assertIn('Test claim', output)
            self.assertIn('True', output)
    
    @patch('factcheckr.cli.CompleteFactCheckr')
    @patch('sys.argv', ['factcheckr', '--json', 'Test claim'])
    def test_main_json_output(self, mock_checker_class):
        """Test JSON output mode."""
        mock_checker_class.return_value = self.mock_checker
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue().strip()
            # Should output raw JSON
            self.assertTrue(output.startswith('{'))
    
    @patch('factcheckr.cli.CompleteFactCheckr')
    @patch('sys.stdin', StringIO('Test stdin claim\n'))
    @patch('sys.argv', ['factcheckr', '--stdin'])
    def test_main_stdin_input(self, mock_checker_class):
        """Test stdin input mode."""
        mock_checker_class.return_value = self.mock_checker
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue()
            self.assertIn('Test claim', output)
    
    @patch('sys.argv', ['factcheckr'])
    def test_main_no_arguments(self):
        """Test main function with no arguments (should show help)."""
        with self.assertRaises(SystemExit):
            main()
    
    def test_format_output(self):
        """Test output formatting function."""
        test_json = json.dumps({
            'claims': [{
                'claim': 'Test claim',
                'verdict': 'True',
                'evidence': 'Test evidence',
                'confidence': 0.9
            }]
        })
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            format_output(test_json)
            output = fake_out.getvalue()
            self.assertIn('Test claim', output)
            self.assertIn('True', output)
            self.assertIn('Test evidence', output)
            self.assertIn('0.9', output)
    
    def test_format_output_invalid_json(self):
        """Test format_output with invalid JSON."""
        invalid_json = "This is not JSON"
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            format_output(invalid_json)
            output = fake_out.getvalue()
            self.assertIn('Error', output)
    
    def test_format_output_multiple_claims(self):
        """Test format_output with multiple claims."""
        test_json = json.dumps({
            'claims': [
                {
                    'claim': 'Claim 1',
                    'verdict': 'True',
                    'evidence': 'Evidence 1',
                    'confidence': 0.9
                },
                {
                    'claim': 'Claim 2',
                    'verdict': 'False',
                    'evidence': 'Evidence 2',
                    'confidence': 0.8
                }
            ]
        })
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            format_output(test_json)
            output = fake_out.getvalue()
            self.assertIn('Claim 1', output)
            self.assertIn('Claim 2', output)
            self.assertIn('True', output)
            self.assertIn('False', output)


if __name__ == '__main__':
    unittest.main()