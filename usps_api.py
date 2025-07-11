import requests
from usps_auth import get_usps_token
import re

# USPS API setup
USPS_API_BASE_URL = "https://apis.usps.com/addresses/v3"



def parse_street_address(raw_address):
    """
    Converts decimal half addresses to USPS fraction format (e.g. 45.5 -> 45 1/2)
    and splits street number from street name.
    Returns (street_number, street_name).
    """

    raw_address = raw_address.strip()
    # Convert decimal .5 to 1/2 before splitting
    raw_address = re.sub(r'(\d+)\.5\b', r'\1 1/2', raw_address)

    # New precise regex:
    match = re.match(
        r'^(\d+(?:-\d+)?(?: [1-9]/[0-9])?(?:[A-Za-z])?)\s+(.*)$',
        raw_address
    )

    if match:
        street_number = match.group(1).strip()
        street_name = match.group(2).strip()
    else:
        street_number = ''
        street_name = raw_address

    return street_number, street_name



def validate_usps(address, city=None, state=None, zip5=None, apt=None):
    """
    Validates an address using USPS new REST API (Developer Portal).
    Returns dict with 'valid' boolean and 'corrected_address' string.
    """

    # Early exit if address or zip is missing or marked as N/A
    if not address or address.strip().lower() in ['n/a', 'na'] or not zip5 or zip5.strip().lower() in ['n/a', 'na']:
        return {
            "valid": False,
            "corrected_address": None,
            "error": "Address or ZIP missing or invalid (N/A)"
        }


    #token = get_usps_token()

    token = "eyJraWQiOiJIdWpzX2F6UnFJUzBpSE5YNEZIRk96eUwwdjE4RXJMdjNyZDBoalpNUnJFIiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYifQ.eyJlbnRpdGxlbWVudHMiOlt7Im5hbWUiOiJGQVNUIiwiY3JpZHMiOiI1MzEwODA5MiJ9XSwic3ViIjoiNDU5Mzk1Njk5IiwiY3JpZCI6IjUzMTA4MDkyIiwic3ViX2lkIjoiNDU5Mzk1Njk5Iiwicm9sZXMiOltdLCJwYXltZW50X2FjY291bnRzIjp7InBlcm1pdHMiOltdfSwiaXNzIjoiaHR0cHM6Ly9rZXljLnVzcHMuY29tL3JlYWxtcy9VU1BTIiwiY29udHJhY3RzIjp7InBheW1lbnRBY2NvdW50cyI6e30sInBlcm1pdHMiOltdfSwiYXVkIjpbInBheW1lbnRzIiwicHJpY2VzIiwic3Vic2NyaXB0aW9ucy10cmFja2luZyIsIm9yZ2FuaXphdGlvbnMiXSwiYXpwIjoiQURhRHZSUW4ySVJidjhRRTNtTkh0QXpCWmZza2dnNW5WeENNQ3RhaEFHU1pvTEFaIiwibWFpbF9vd25lcnMiOlt7ImNyaWQiOiI1MzEwODA5MiIsIm1pZHMiOiI5MDM5MzExOTcsIDkwMzkzMTE5OCwgOTAzOTMxMTk0LCA5MDM5MzExOTYifV0sInNjb3BlIjoiYWRkcmVzc2VzIiwiY29tcGFueV9uYW1lIjoiV2hvcGxheXMgVVMiLCJleHAiOjE3NTIxODU0NjcsImlhdCI6MTc1MjE1NjY2NywianRpIjoiYjgzZTNiMzItMDIzMS00NjdiLTk3MTAtNTU0M2U2Mzg4ZTIwIn0.OXK7vj3kO1KgSE8KXoU0-ZMtE4zzrwZIX33infTfValviVVlK0rFwdnlDG3CuqYaszJ6n3nzP_Slnm_MKy6xa10yStNKXqFOrU2VVbIIZN_y4a8jQ4ipNEJ3Y42HdHSdEjs9uHvY0OgVv5ufXcIisI-pRUKR1slk-8kzqjpg7mZWHCthKzU0azjXLrIMVWvUaBZplPIgHm-p0KWHeSemSunj1vuQA0_Tik1qaHai2kj8cQiKzSd1BkuSnnf9kWxS8OuGzVJJfdl2wSeUpflN8Qe4iDrcuDbbzXxjxCmUByWFslElE3_dlFIIJ6URF2p_Uz4sdtENd7mc8xDb9L9D-A"

    endpoint = f"{USPS_API_BASE_URL}/address"

    params = {
        "streetAddress": address,
        "state": state
    }

    if city:
        params["city"] = city
    if zip5:
        params["ZIPCode"] = zip5
    if apt:
        params["secondaryAddress"] = apt

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(endpoint, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Extract standardized address
        addr = data.get('address', {})
        additionalInfo = data.get('additionalInfo', {})
        street_number, street_name = parse_street_address(addr.get('streetAddress', ''))

        corrected_address = f"{addr.get('streetAddress', '')}, {addr.get('city', '')}, {addr.get('state', '')} {addr.get('ZIPCode', '')}-{addr.get('ZIPPlus4', '')}"

        suggested_address = f"{street_number} {street_name}, {addr.get('city', '')}, {addr.get('state', '')} {addr.get('ZIPCode', '')}-{addr.get('ZIPPlus4', '')}"

        # Display options to user
        print("\n")
        print(f"Suggested address: {suggested_address}")
        print("\n")
        decision = input("Choose action: (A)ccept / (S)kip: ").strip().lower()

        if decision == 'a':

            return {
                "valid": True,
                "corrected_address": corrected_address,
                "standardized_address": {
                "street_number": street_number,
                "street": street_name,
                "city": addr.get('city', ''),
                "state": addr.get('state', ''),
                "zip5": addr.get('ZIPCode', ''),
                "zip4": addr.get('ZIPPlus4', ''),
                "apt": addr.get('secondaryAddress', ''),
                }
            }
            
        else:
            print("Address skipped by the user.")

            return {
                "valid": False,
                "corrected_address": None,
                "error": "reviewed and skipped by user"
            }        


    else:
        # Log error details
        # print("USPS REST API error:", response.status_code, response.text)
        return {
            "valid": False,
            "corrected_address": None,
            "error": response.text
        }
