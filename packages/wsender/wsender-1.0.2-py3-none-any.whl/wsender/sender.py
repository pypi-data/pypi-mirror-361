import re
import json
import requests
from urllib.parse import quote

def send_to_whatsapp(data: dict):
    """
    data = {
        "url": "https://chat.laxicon.in",             # Required
        "access_token": "682c166340257",              # Required
        "instance_id": "686B4D9D7EFA6",                # Required
        "number": "+919999999999",
        "message": "Hello!",
        "filename": "hello.jpg",                      # Optional
        "media_url": "https://example.com/hello.jpg"  # Optional
    }
    """

    # Get credentials from data
    instance_id = data.get("instance_id")
    access_token = data.get("access_token")
    whatsapp_url = data.get("url")
    number = re.sub(r'\D', '', data.get("number", "").strip().replace("+", ""))
   
    if not (instance_id and access_token and whatsapp_url and number):
        raise ValueError("Missing required fields: instance_id, access_token,number, or url")

    message = data.get("message", "")

    filename = data.get("filename", "")
    media_url = data.get("media_url", None)

    # Encode media URL if present
    encode_media_url = ''
    if media_url:
        url_parts = media_url.split("/")
        encoded_url = quote(url_parts[0], safe='')  # e.g., https
        encoded_url += "/" + "/".join(quote(part, safe='') for part in url_parts[1:])
        encode_media_url = encoded_url

    # Build request URL
    url = f"{whatsapp_url}/api/send?instance_id={instance_id}&access_token={access_token}"
    url += f"&number={number}&message={message}"
    url += f"&type={'media' if media_url else 'text'}"
    if media_url:
        url += f"&media_url={encode_media_url}&filename={filename}"

    # Send request
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url, headers=headers)

    if res.status_code == 200:
        print("MESSAGE SENT")
        response_data = json.loads(res.text)
        if isinstance(response_data, dict) and response_data.get('status') == 'success':
            return True
    print("FAILED:", res.text)
    return False



#RESET INSTANCES
import requests

def reset_instance(url_with_token):
    print("CREATING INSTANCE...")

    try:
        response = requests.get(url_with_token)
        # print("Status Code:", response.status_code)

        if response.headers.get("Content-Type", "").startswith("application/json"):
            data = response.json()
            instance_id = data.get("instance_id")
            if instance_id:
                print(" Instance ID:", instance_id)
                return instance_id
            else:
                print("'instance_id' not found in response:", data)
        else:
            print(" Response is not JSON")
            print("Raw Response:", response.text)

    except Exception as e:
        print("Request failed:", str(e))



#POST REBOOT

import requests

def reboot_instance(instance_id, access_token):
    url = "https://chat.laxicon.in/api/reboot"
    payload = {
        "instance_id": instance_id,
        "access_token": access_token
    }

    print("REBOOTING INSTANCE...")

    try:
        response = requests.post(url, data=payload)
        print("Status Code:", response.status_code)

        if response.status_code == 200:
            print("Reboot command sent successfully.")
        else:
            print("Failed to send reboot command.")

        # Removed raw HTML output

    except Exception as e:
        print("Request failed:", str(e))



#get pairing code

import requests

def get_pairing_code(instance_id, access_token, phone, base_url="https://chat.laxicon.in"):
    auth_url = f"{base_url}/api/get_paircode?instance_id={instance_id}&access_token={access_token}&phone={phone}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.get(auth_url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            pair_code = response_data.get('code')
            if not pair_code:
                print("Pair code not found in response.")
                return None
            print("Pairing Code (Scan in WhatsApp Web):", pair_code)
            return pair_code
        else:
            print("Failed to get pairing code. Status code:", response.status_code)
            print("Response:", response.text)
    except Exception as e:
        print("Request failed:", str(e))
        return None

#QR CODE

import requests
import base64
import json

def get_qr_code(whatsapp_url, instance_id, access_token):
    # 1. Build the API URL
    auth_url = f"{whatsapp_url}/api/get_qrcode?instance_id={instance_id}&access_token={access_token}"
    headers = {'Content-Type': 'application/json'}

    try:
        # 2. Send the GET request
        response = requests.get(auth_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        return {"status": "error", "message": f"Request failed: {e}"}

    try:
        # 3. Parse JSON response
        response_data = response.json()
    except Exception as e:
        return {"status": "error", "message": f"Invalid JSON response: {e}"}

    # 4. Check success status
    if response_data.get('status') != 'success':
        return {"status": "error", "message": f"API Error: {response_data.get('message')}"}

    # 5. Extract base64 string
    base64_img = response_data.get('base64')
    if not base64_img:
        return {"status": "error", "message": "QR code not found in response."}

    # 6. Clean base64 string if it has a prefix
    if base64_img.startswith("data:image"):
        base64_img = base64_img.split(",", 1)[1]

    # 7. Validate base64
    try:
        base64.b64decode(base64_img)
    except Exception as e:
        return {"status": "error", "message": f"Base64 decode failed: {e}"}

    # 8. Return final structured output
    return {
        "status": "success",
        "message": "Success",
        "base64": f"data:image/png;base64,{base64_img}"
    }

# Example usage
if __name__ == "__main__":
    whatsapp_url = "https://chat.laxicon.in"
    instance_id = "your_instance_id_here"
    access_token = "your_access_token_here"

    result = get_qr_code(whatsapp_url, instance_id, access_token)
    print(json.dumps(result, indent=2))

#create instance
import requests

def create_instance(access_token: str, base_url: str = "https://chat.laxicon.in") -> str:
    """
    Creates a new WhatsApp instance using the access token and returns the instance ID.
    The instance ID can be used like an OTP to fetch the QR code.

    Args:
        access_token (str): Your API access token.
        base_url (str): Base URL of the WhatsApp API provider.

    Returns:
        str: Newly created instance ID.

    Raises:
        Exception: If instance creation fails.
    """
    url = f"{base_url}/api/create_instance?access_token={access_token}"
    headers = {'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"HTTP Error: {response.status_code}")

    data = response.json()

    if data.get("status") != "success":
        raise Exception(f"API Error: {data.get('message')}")

    instance_id = data.get("instance_id")
    if not instance_id:
        raise Exception(" Instance ID not found in response.")

    print(f" Your Instance ID : {instance_id}")
    return instance_id
