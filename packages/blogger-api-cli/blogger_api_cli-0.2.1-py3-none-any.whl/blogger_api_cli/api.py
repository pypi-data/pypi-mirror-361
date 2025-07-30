import requests
import json
import os
from typing import Dict, Any, Optional, Union


# --- Helper Function for API Calls ---
def blogger_api_request(method: str, url: str, data: Optional[Dict[str, Any]] = None, 
                        params: Optional[Dict[str, Any]] = None, 
                        return_json: bool = False) -> Union[requests.Response, Dict[str, Any], None]:
    """
    Makes an HTTP request to the Blogger API and prints the response.
    The API key is loaded from the BLOGGER_API_KEY environment variable.
    
    Parameters:
        method (str): HTTP method ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')
        url (str): The API endpoint URL
        data (dict, optional): The JSON data to send in the request body
        params (dict, optional): Additional query parameters to include
        return_json (bool): Whether to return the JSON response instead of the Response object
    
    Returns:
        Response object, JSON dict, or None if an error occurred
    """
    api_key = os.environ.get("BLOGGER_API_KEY")
    if not api_key:
        raise ValueError("API key must be set in the BLOGGER_API_KEY environment variable.")

    full_params = {"key": api_key}
    if params:
        full_params.update(params)

    headers = {'Content-Type': 'application/json'}

    print(f"\n--- Testing {method} request ---")
    print(f"URL: {url}")
    print(f"Params: {full_params}")
    if data:
        print(f"Body: {json.dumps(data, indent=2)}")

    try:
        if method == 'GET':
            response = requests.get(url, params=full_params, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, params=full_params, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, params=full_params, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, params=full_params, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, params=full_params, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return None

        print(f"Status Code: {response.status_code}")
        try:
            json_response = response.json()
            print(f"Response Body: {json.dumps(json_response, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response Body (raw): {response.text}")
            json_response = None

        if response.status_code == 200:
            print("SUCCESS: The request was successful.")
        elif response.status_code in [401, 403] and method != 'GET':
            print("FAILURE (Expected for API Key only): This indicates an authentication/authorization issue. "
                  "API keys are typically for read-only access. Write operations usually require OAuth 2.0.")
        else:
            print(f"FAILURE: Unexpected status code. Review the error details above.")

        print("-" * 30)
        return json_response if return_json and json_response else response

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        print("-" * 30)
        return None


# Convenience function for GET requests
def get_request(url: str, params: Optional[Dict[str, Any]] = None, 
                return_json: bool = False) -> Union[requests.Response, Dict[str, Any], None]:
    """
    Makes an HTTP GET request to the Blogger API and prints the response.
    This is a convenience wrapper around blogger_api_request.
    
    Parameters:
        url (str): The API endpoint URL
        params (dict, optional): Additional query parameters to include
        return_json (bool): Whether to return the JSON response instead of the Response object
    
    Returns:
        Response object, JSON dict, or None if an error occurred
    """
    return blogger_api_request('GET', url, params=params, return_json=return_json)
