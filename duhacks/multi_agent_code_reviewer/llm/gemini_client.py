"""
Gemini LLM Client
Wrapper for Google Gemini API calls.
"""

from typing import Dict, Any
import json


class GeminiClient:
    """
    Client for interacting with Google Gemini LLM.
    Used ONLY by agents, NEVER by orchestrator.
    """
    
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        """
        Initialize Gemini client.
        """
        import os
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or "PLACEHOLDER_API_KEY"
        self.model_name = model
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model)
            self.client_ready = True
        except Exception:
            self.model = None
            self.client_ready = False
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate response from Gemini.
        """
        if self.client_ready and self.api_key != "PLACEHOLDER_API_KEY":
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        'max_output_tokens': max_tokens,
                        'temperature': 0.1, # Lower temperature for stable JSON
                    }
                )
                return self.parse_json_response(response.text)
            except Exception as e:
                import logging
                logging.error(f"Gemini API call failed: {e}")
                return self._mock_generate(prompt)
        
        return self._mock_generate(prompt)
    
    def _call_gemini_api(self, prompt: str, max_tokens: int) -> str:
        """
        Call actual Gemini API.
        
        Args:
            prompt: Input prompt
            max_tokens: Max tokens
        
        Returns:
            Raw response text
        """
        if not self.client:
            raise RuntimeError("Gemini client not initialized")
        
        # Production code:
        # response = self.client.generate_content(
        #     prompt,
        #     generation_config={
        #         'max_output_tokens': max_tokens,
        #         'temperature': 0.7,
        #     }
        # )
        # return response.text
        
        return ""
    
    def _mock_generate(self, prompt: str) -> Dict[str, Any]:
        """
        Mock Gemini response for skeleton.
        
        Args:
            prompt: Input prompt
        
        Returns:
            Mock response
        """
        # Detect prompt type and return appropriate mock
        # Note: Check LOGIC first because logic prompts often contain 'Do NOT check security'
        if "LOGIC" in prompt.upper():
            return {
                "findings": [
                    {
                        "issue": "infinite_loop",
                        "severity": "high",
                        "description": "Unconditional while True loop may cause infinite execution"
                    },
                    {
                        "issue": "unreachable_code",
                        "severity": "medium",
                        "description": "Code after break statement may be unreachable"
                    }
                ],
                "confidence": 0.75
            }
        elif "SECURITY" in prompt.upper():
            return {
                "findings": [
                    {
                        "type": "sql_injection",
                        "severity": "critical",
                        "description": "Potential SQL injection in user authentication",
                        "line": "query = f\"SELECT * FROM users WHERE username='{username}'...\""
                    },
                    {
                        "type": "input_validation",
                        "severity": "high",
                        "description": "Missing input validation on user_id parameter",
                        "line": "return database.query(user_id)"
                    }
                ],
                "confidence": 0.85
            }
        else:
            return {
                "findings": [],
                "confidence": 0.6
            }
    
    def parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response.
        
        Args:
            response_text: Raw response text
        
        Returns:
            Parsed JSON dictionary
        """
        try:
            # Try to find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_text = response_text[start:end]
                return json.loads(json_text)
            else:
                return {"error": "No JSON found in response"}
        
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in response"}
