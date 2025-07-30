#!/usr/bin/env python3
"""
Core fact-checking functionality for FactCheckr.
"""

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

import json
import re

SYSTEM_PROMPT = """
You are an expert fact-checking assistant with comprehensive knowledge across all domains. You MUST provide definitive verdicts for claims.

For each claim, analyze it thoroughly and respond with valid JSON in this exact format:
{
  "claims": [
    {
      "claim": "[original claim text]",
      "verdict": "[True/False/Likely True/Likely False/Possibly True/Possibly False]",
      "evidence": "[detailed explanation with reasoning]",
      "confidence": [0.1-1.0]
    }
  ]
}

IMPORTANT RULES:
- NEVER use "Unsupported" - always make a determination
- Use "True" for definitively correct claims (e.g., "Water boils at 100°C")
- Use "False" for definitively incorrect claims (e.g., "Cats have 6 legs")
- Use "Likely True/False" for claims with strong evidence
- Use "Possibly True/False" for claims with weaker evidence
- Always provide detailed evidence explaining your reasoning
- Set confidence between 0.1-1.0 (never 0.0)
- Draw upon your knowledge of science, history, geography, biology, physics, etc.

Examples:
- "Cats have 6 legs" → "False" (mammals have 4 legs)
- "Humans can fly" → "False" (humans cannot fly without assistance)
- "Python was created by Guido van Rossum" → "True" (well-documented fact)
- "Birds can fly" → "Likely True" (most birds can fly, some exceptions exist)

Be decisive and thorough in your analysis.
"""

class CompleteFactCheckr:
    """AI-powered fact-checking tool using Hack Club AI API."""
    
    def __init__(self, api_key: str = None):
        # Use free Hack Club AI API - no API key needed
        self.api_url = "https://ai.hackclub.com/chat/completions"
        self.ai_available = REQUESTS_AVAILABLE and self._test_ai_connection()

    
    def _test_ai_connection(self) -> bool:
        """Test if AI service is available"""
        try:
            # Test with a simple request to Hack Club AI
            response = requests.post(
                self.api_url,
                headers={"Content-Type": "application/json"},
                json={
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    
    def extract_claims(self, text: str) -> list:
        """Extract potential factual claims from text"""
        sentences = re.split(r'[.!?]+', text)
        claims = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and len(claims) < 3:
                claims.append(sentence)
        
        return claims if claims else [text.strip()]
    
    def fact_check_with_ai(self, claim: str) -> str:
        """Fact-check using AI service with enhanced error handling"""
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Fact-check this claim: {claim}"}
            ]
            
            payload = {
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 500
            }
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data['choices'][0]['message']['content'].strip()
                
                # Clean up the response if it's wrapped in code blocks
                if ai_response.startswith('```json'):
                    ai_response = ai_response[7:]
                if ai_response.startswith('```'):
                    ai_response = ai_response[3:]
                if ai_response.endswith('```'):
                    ai_response = ai_response[:-3]
                ai_response = ai_response.strip()
                
                try:
                    parsed_response = json.loads(ai_response)
                    return json.dumps(parsed_response, indent=2)
                except json.JSONDecodeError as e:
                    # If AI service is having issues, use fallback logic
                    return self._fallback_fact_check(claim, f"JSON parse error: {str(e)}")
            else:
                return self._fallback_fact_check(claim, f"API returned status {response.status_code}")
                
        except Exception as e:
            return self._fallback_fact_check(claim, f"AI service error: {str(e)}")
    
    def _fallback_fact_check(self, claim: str, error_detail: str = "") -> str:
        """Fallback fact-checking using basic heuristics when AI fails"""
        claim_lower = claim.lower()
        
        # Basic pattern matching for common false claims
        if "cats have 9 lives" in claim_lower or "cats have nine lives" in claim_lower:
            return json.dumps({
                "claims": [{
                    "claim": claim,
                    "verdict": "False",
                    "evidence": "This is a myth. Cats have only one life like all living creatures. The saying 'cats have nine lives' refers to their agility and ability to survive dangerous situations, but it's not literally true.",
                    "confidence": 0.9
                }]
            }, indent=2)
        
        elif "earth is flat" in claim_lower:
            return json.dumps({
                "claims": [{
                    "claim": claim,
                    "verdict": "False",
                    "evidence": "The Earth is spherical (oblate spheroid). This has been proven through satellite imagery, physics, astronomy, and direct observation from space.",
                    "confidence": 1.0
                }]
            }, indent=2)
        
        elif "water boils at 100" in claim_lower and "celsius" in claim_lower:
            return json.dumps({
                "claims": [{
                    "claim": claim,
                    "verdict": "True",
                    "evidence": "Water boils at 100°C (212°F) at standard atmospheric pressure (1 atmosphere or 101.325 kPa) at sea level.",
                    "confidence": 1.0
                }]
            }, indent=2)
        
        else:
            # Generic error response
            return json.dumps({
                "claims": [{
                    "claim": claim,
                    "verdict": "Error",
                    "evidence": f"AI service unavailable. {error_detail}" if error_detail else "AI service unavailable",
                    "confidence": 0.1
                }]
            }, indent=2)
    
    def fact_check(self, text: str) -> str:
        """Main fact-checking method"""
        if not text or not text.strip():
            return json.dumps({
                "claims": [{
                    "claim": "",
                    "verdict": "Error",
                    "evidence": "No text provided",
                    "confidence": 0.0
                }]
            }, indent=2)
        
        claims = self.extract_claims(text)
        
        if self.ai_available:
            # Use AI for fact-checking
            if len(claims) == 1:
                return self.fact_check_with_ai(claims[0])
            else:
                # Handle multiple claims
                all_results = []
                for claim in claims:
                    result = self.fact_check_with_ai(claim)
                    try:
                        parsed = json.loads(result)
                        if parsed.get('claims'):
                            all_results.extend(parsed['claims'])
                    except json.JSONDecodeError:
                        all_results.append({
                            "claim": claim,
                            "verdict": "Error",
                            "evidence": "Failed to process claim",
                            "confidence": 0.1
                        })
                
                return json.dumps({"claims": all_results}, indent=2)
        else:
            # AI not available
            return json.dumps({
                "claims": [{
                    "claim": text,
                    "verdict": "Error",
                    "evidence": "AI service unavailable. Please check your internet connection.",
                    "confidence": 0.0
                }]
            }, indent=2)

def main():
    """Command line interface for testing"""
    fc = CompleteFactCheckr()
    
    if not fc.ai_available:
        print("AI service is not available. Please check your internet connection.")
        return
    
    print("FactCheckr AI Service Ready!")
    print("Enter claims to fact-check (or 'quit' to exit):")
    
    while True:
        try:
            claim = input("\n> ").strip()
            if claim.lower() in ['quit', 'exit', 'q']:
                break
            
            if claim:
                result = fc.fact_check(claim)
                print("\nResult:")
                print(result)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()