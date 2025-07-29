import requests

# API base endpoint for sending events to Theera
API_ENDPOINT = "https://theera.netlify.app/api/v1/events"

def send_event(api_key, category, fields):
    """
    Send a custom event to Theera's Event Tracking API.

    This function allows developers to send any category of event (e.g., 'sale',
    'signup', 'feedback') with custom key-value pairs (e.g., user ID, email, product name).

    Parameters:
        api_key (str): 
            Your Theera API key for authentication. 
            This should be kept secret and never exposed on the frontend.

        category (str): 
            A short label identifying the event type. 
            Example values: 'signup', 'purchase', 'form_submit'.

        fields (dict): 
            A dictionary of additional custom fields to associate with the event.
            Example:
                {
                    "user_id": "12345",
                    "email": "user@example.com",
                    "plan": "pro"
                }

    Returns:
        dict: Parsed JSON response from the Theera API.

    Raises:
        Exception: If the request fails or the API returns an error status.
    """

    # Set required HTTP headers including authorization
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Prepare the payload with category and custom fields
    payload = {
        "category": category,
        "fields": fields
    }

    print(f"[Theera SDK] Sending event to: {API_ENDPOINT}")
    print(f"[Theera SDK] Category: {category}")
    print(f"[Theera SDK] Fields: {fields}")

    # Send POST request to the Theera API
    response = requests.post(API_ENDPOINT, json=payload, headers=headers)

    # Raise exception if the response code is not successful
    if response.status_code != 200:
        print(f"[Theera SDK] Failed with status: {response.status_code}")
        print(f"[Theera SDK] Response: {response.text}")
        raise Exception(f"Error sending event: {response.status_code} - {response.text}")

    print("[Theera SDK] Event sent successfully!")

    # Return the parsed JSON response
    return response.json()
