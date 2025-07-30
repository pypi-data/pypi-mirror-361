import requests
import json

def verify_api_key(api_key):
    """
    Verify if the API key is valid by sending a POST request to the Next.js API route
    
    Args:
        api_key (str): The API key to verify
        
    Returns:
        dict: The response from the API
    """
    # API endpoint URL
    url = "http://localhost:3000/api/verify"
    
    # Request headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Request payload
    payload = {
        "apiKey": api_key
    }
    
    # Send the POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    # Parse and return the response
    return response.json()

# Example usage
if __name__ == "__main__":
    # Replace with your actual API key
    api_key = "JINGKEVNxapXMBQEWxPnBY-JINGKEPmCPibSD-JINGKE8VUU-JINGKE7dKQ-JINGKEp8qgTAkwCKP9"
    
    result = verify_api_key(api_key)
    
    if result.get("success"):
        print(f"API key is valid!")
        print(f"Endpoint: {result.get('endpointName')}")
        print(f"Model: {result.get('model')}")
    else:
        print(f"Error: {result.get('message')}")