import requests
import json
from typing import Dict, List, Optional

def get_all_pharmacies() -> List[Dict]:
    """
    Fetch all pharmacy data from the API endpoint.
    
    Returns:
        List[Dict]: A list of pharmacy data dictionaries
    """
    api_url = "https://67e14fb758cc6bf785254550.mockapi.io/pharmacies"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        pharmacies = response.json()
        return pharmacies
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching pharmacy data: {e}")
        return []

def find_pharmacy_by_phone(phone_number: str) -> Optional[Dict]:
    """
    Find a pharmacy by phone number.
    
    Args:
        phone_number (str): The phone number to search for
        
    Returns:
        Optional[Dict]: The pharmacy data if found, None otherwise
    """
    pharmacies = get_all_pharmacies()
    
    # Normalize the phone number for comparison (remove non-numeric characters)
    normalized_phone = ''.join(filter(str.isdigit, phone_number))
    
    for pharmacy in pharmacies:
        pharmacy_phone = ''.join(filter(str.isdigit, pharmacy.get('phone', '')))
        if pharmacy_phone == normalized_phone:
            return pharmacy
    
    return None

def mock_send_email(pharmacy_email: str, subject: str, body: str) -> bool:
    """
    Mock function to simulate sending an email to a pharmacy.
    
    Args:
        pharmacy_email (str): The recipient email address
        subject (str): The email subject
        body (str): The email body
        
    Returns:
        bool: True if the email would be sent successfully
    """
    print(f"Mock email sent to: {pharmacy_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return True

def mock_schedule_callback(pharmacy_name: str, phone_number: str, callback_time: str) -> bool:
    """
    Mock function to simulate scheduling a callback to a pharmacy.
    
    Args:
        pharmacy_name (str): The name of the pharmacy
        phone_number (str): The phone number to call back
        callback_time (str): The requested callback time
        
    Returns:
        bool: True if the callback would be scheduled successfully
    """
    print(f"Mock callback scheduled for: {pharmacy_name}")
    print(f"Phone: {phone_number}")
    print(f"Time: {callback_time}")
    return True

if __name__ == "__main__":
    # Example usage
    pharmacies = get_all_pharmacies()
    print(f"Found {len(pharmacies)} pharmacies")
    
    # Example: Find a pharmacy by phone number
    test_phone = "123-456-7890"  # Replace with a phone number from the actual API
    pharmacy = find_pharmacy_by_phone(test_phone)
    
    if pharmacy:
        print(f"Found pharmacy: {pharmacy['name']}")
        # Example follow-up actions
        mock_send_email(pharmacy.get('email', ''), 
                        "Follow-up from our call", 
                        f"Dear {pharmacy['name']}, thank you for your interest...")
        
        mock_schedule_callback(pharmacy['name'], 
                              pharmacy.get('phone', ''),
                              "Tomorrow at 2pm")
    else:
        print(f"No pharmacy found with phone number: {test_phone}")
