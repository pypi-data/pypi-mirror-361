#!/usr/bin/env python3
"""Tests for the core FactCheckr functionality."""

import json
import pytest
from unittest.mock import Mock, patch
from factcheckr.core import CompleteFactCheckr


class TestCompleteFactCheckr:
    """Test cases for CompleteFactCheckr class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fact_checker = CompleteFactCheckr()
    
    def test_initialization(self):
        """Test that FactCheckr initializes correctly."""
        assert self.fact_checker is not None
        assert hasattr(self.fact_checker, 'api_url')
        assert hasattr(self.fact_checker, 'ai_available')
    
    def test_extract_claims_single_sentence(self):
        """Test claim extraction from single sentence."""
        text = "Cats have 9 lives"
        claims = self.fact_checker.extract_claims(text)
        assert len(claims) == 1
        assert claims[0] == "Cats have 9 lives"
    
    def test_extract_claims_multiple_sentences(self):
        """Test claim extraction from multiple sentences."""
        text = "Cats have 9 lives. Dogs are loyal animals. Birds can fly."
        claims = self.fact_checker.extract_claims(text)
        assert len(claims) <= 3  # Should limit to 3 claims
        assert "Cats have 9 lives" in claims
    
    def test_extract_claims_empty_text(self):
        """Test claim extraction from empty text."""
        text = ""
        claims = self.fact_checker.extract_claims(text)
        assert len(claims) == 1
        assert claims[0] == ""
    
    def test_fallback_cats_nine_lives(self):
        """Test fallback fact-checking for cats nine lives claim."""
        result = self.fact_checker._fallback_fact_check("Cats have 9 lives")
        parsed = json.loads(result)
        
        assert "claims" in parsed
        assert len(parsed["claims"]) == 1
        
        claim_result = parsed["claims"][0]
        assert claim_result["claim"] == "Cats have 9 lives"
        assert claim_result["verdict"] == "False"
        assert claim_result["confidence"] == 0.9
        assert "myth" in claim_result["evidence"].lower()
    
    def test_fallback_earth_flat(self):
        """Test fallback fact-checking for flat earth claim."""
        result = self.fact_checker._fallback_fact_check("The Earth is flat")
        parsed = json.loads(result)
        
        claim_result = parsed["claims"][0]
        assert claim_result["verdict"] == "False"
        assert claim_result["confidence"] == 1.0
        assert "spherical" in claim_result["evidence"].lower()
    
    def test_fallback_water_boiling(self):
        """Test fallback fact-checking for water boiling point."""
        result = self.fact_checker._fallback_fact_check("Water boils at 100 degrees Celsius")
        parsed = json.loads(result)
        
        claim_result = parsed["claims"][0]
        assert claim_result["verdict"] == "True"
        assert claim_result["confidence"] == 1.0
        assert "100°C" in claim_result["evidence"]
    
    def test_fallback_unknown_claim(self):
        """Test fallback fact-checking for unknown claim."""
        result = self.fact_checker._fallback_fact_check("Some random unknown claim")
        parsed = json.loads(result)
        
        claim_result = parsed["claims"][0]
        assert claim_result["verdict"] == "Error"
        assert claim_result["confidence"] == 0.1
        assert "unavailable" in claim_result["evidence"].lower()
    
    def test_fact_check_empty_input(self):
        """Test fact-checking with empty input."""
        result = self.fact_checker.fact_check("")
        parsed = json.loads(result)
        
        claim_result = parsed["claims"][0]
        assert claim_result["verdict"] == "Error"
        assert "No text provided" in claim_result["evidence"]
    
    def test_fact_check_whitespace_input(self):
        """Test fact-checking with whitespace-only input."""
        result = self.fact_checker.fact_check("   \n\t   ")
        parsed = json.loads(result)
        
        claim_result = parsed["claims"][0]
        assert claim_result["verdict"] == "Error"
        assert "No text provided" in claim_result["evidence"]
    
    @patch('factcheckr.core.requests.post')
    def test_ai_connection_success(self, mock_post):
        """Test successful AI connection."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        fc = CompleteFactCheckr()
        assert fc._test_ai_connection() is True
    
    @patch('factcheckr.core.requests.post')
    def test_ai_connection_failure(self, mock_post):
        """Test failed AI connection."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        fc = CompleteFactCheckr()
        assert fc._test_ai_connection() is False
    
    @patch('factcheckr.core.requests.post')
    def test_ai_connection_exception(self, mock_post):
        """Test AI connection with exception."""
        mock_post.side_effect = Exception("Network error")
        
        fc = CompleteFactCheckr()
        assert fc._test_ai_connection() is False
    
    @patch('factcheckr.core.requests.post')
    def test_fact_check_with_ai_success(self, mock_post):
        """Test successful AI fact-checking."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        "claims": [{
                            "claim": "Test claim",
                            "verdict": "True",
                            "evidence": "Test evidence",
                            "confidence": 0.9
                        }]
                    })
                }
            }]
        }
        mock_post.return_value = mock_response
        
        fc = CompleteFactCheckr()
        fc.ai_available = True
        result = fc.fact_check_with_ai("Test claim")
        parsed = json.loads(result)
        
        assert "claims" in parsed
        assert parsed["claims"][0]["verdict"] == "True"
    
    @patch('factcheckr.core.requests.post')
    def test_fact_check_with_ai_json_error(self, mock_post):
        """Test AI fact-checking with JSON parsing error."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': "Invalid JSON response"
                }
            }]
        }
        mock_post.return_value = mock_response
        
        fc = CompleteFactCheckr()
        fc.ai_available = True
        result = fc.fact_check_with_ai("Test claim")
        parsed = json.loads(result)
        
        # Should fall back to heuristic checking
        assert "claims" in parsed
        claim_result = parsed["claims"][0]
        assert claim_result["claim"] == "Test claim"
    
    @patch('factcheckr.core.requests.post')
    def test_fact_check_with_ai_code_blocks(self, mock_post):
        """Test AI fact-checking with code block wrapped response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '```json\n{"claims": [{"claim": "Test", "verdict": "True", "evidence": "Test", "confidence": 0.9}]}\n```'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        fc = CompleteFactCheckr()
        fc.ai_available = True
        result = fc.fact_check_with_ai("Test claim")
        parsed = json.loads(result)
        
        assert "claims" in parsed
        assert parsed["claims"][0]["verdict"] == "True"
    
    def test_json_output_format(self):
        """Test that all outputs are valid JSON."""
        test_claims = [
            "Cats have 9 lives",
            "The Earth is flat",
            "Water boils at 100 degrees Celsius",
            "Random unknown claim",
            ""
        ]
        
        for claim in test_claims:
            result = self.fact_checker.fact_check(claim)
            # Should not raise JSONDecodeError
            parsed = json.loads(result)
            assert "claims" in parsed
            assert isinstance(parsed["claims"], list)
            
            for claim_result in parsed["claims"]:
                assert "claim" in claim_result
                assert "verdict" in claim_result
                assert "evidence" in claim_result
                assert "confidence" in claim_result
                assert isinstance(claim_result["confidence"], (int, float))
                assert 0.0 <= claim_result["confidence"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__])