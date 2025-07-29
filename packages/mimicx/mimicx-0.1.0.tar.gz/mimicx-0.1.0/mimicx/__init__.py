"""
MimicX AI
Human-like AI for everyone.
"""

__version__ = "0.1.0"
__author__ = 'Hamadi Camara'
__credits__ = 'AI Researcher at MimicX'

import requests
import json
from typing import Dict, Any, Optional



class MimicText:
    """
    Client for interacting with the SpeedPresta API document correction service.
    """
    
    def __init__(self, base_url: str = "https://api.speedpresta.com/api/v1"):
        """
        Initialize the SpeedPresta client.
        
        Args:
            base_url (str): Base URL for the API
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def correct_document(self, query: str, model: str = "DOCUMENT", 
                        correction_type: str = "CORRECT") -> Dict[str, Any]:
        """
        Send a document correction request to the API.
        
        Args:
            query (str): The text to be corrected
            model (str): The model type (default: "DOCUMENT")
            correction_type (str): The type of correction (default: "CORRECT")
            
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}/mimicx/document/correct"
        
        payload = {
            "model": model,
            "type": correction_type,
            "data": {
                "query": query
            }
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (4xx, 5xx)
            error_detail = {
                "status_code": response.status_code,
                "error": str(e),
                "response_body": response.text
            }
            if response.status_code >= 400:
                try:
                    error_detail["json_response"] = response.json()
                except json.JSONDecodeError:
                    pass
            raise requests.exceptions.HTTPError(f"HTTP {response.status_code}: {error_detail}")
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Request failed: {str(e)}")
    
    def set_auth_header(self, auth_token: str, auth_type: str = "Bearer"):
        """
        Set authentication header if required.
        
        Args:
            auth_token (str): Authentication token
            auth_type (str): Type of authentication (default: "Bearer")
        """
        self.session.headers.update({
            'Authorization': f"{auth_type} {auth_token}"
        })
    
    def add_custom_header(self, key: str, value: str):
        """
        Add custom header to the session.
        
        Args:
            key (str): Header key
            value (str): Header value
        """
        self.session.headers.update({key: value})

