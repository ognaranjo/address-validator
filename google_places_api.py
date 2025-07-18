from unittest import result
import googlemaps
import re
import pandas as pd
from utils import extract_google_address_components, extract_unit_number



gmaps = googlemaps.Client(key="AIzaSyA9nQeB9wXGd64qYJxCdHuO5Ty4vBbHVAI")

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

def parse_usps_address(formatted_address, apt=None):
    """
    Parse a USPS or Google-style address into street, city, state, zip.
    Handles addresses ending with "United States" or "USA".
    """
    # Remove the country part if present
    address = re.sub(r',?\s*(United States|USA)\.?$', '', formatted_address.strip(), flags=re.IGNORECASE)
    
    # Try to match the standard pattern
    match = re.match(
        r'^(.*?),\s*([\w\s\-\.]+),\s*([A-Z]{2})\s*(\d{5})(?:-\d{4})?$',
        address
    )
    if match:
        street, city, state, zip5 = match.groups()
        street_number, street_name = parse_street_address(street)
        return {
            "street": street.strip(),
            "street_number": street_number.strip(),
            "street_name": street_name.strip(),
            "city": city.strip(),
            "state": state.strip(),
            "zip5": zip5.strip(),
            "apt": apt.strip() if apt else ""
        }
    else:
        # If address is only "United States" or something unparseable
        if address in ["", "United States", "USA"]:
            return {"street": "", "street_number": "", "street_name": "", "city": "", "state": "", "zip5": ""}
        # Otherwise return what we have
        return {"street": address, "street_number": "", "street_name": "", "city": "", "state": "", "zip5": ""}


def search_google_places(place_name, google_places_cache, state="RI"):
    """
    Searches Google Places API for a place name.
    Prints a list of candidates and lets the user select one.
    Returns a dict with keys: found, address, parsed_address
    """

    if (
        state is None
        or (isinstance(state, float) and pd.isna(state))
        or str(state).strip().lower() in ("", "n/a", "nan", "none")
    ):
        state = "RI"

    place_name = place_name.strip() + " state: " + state

    # Use cache if available
    cache_key = place_name.strip().lower()
    if cache_key in google_places_cache:
        print(f"\n[Cache hit] Using previously selected place for '{place_name}':")
        prev_result = google_places_cache[cache_key]
        if prev_result["found"]:
            print(f"✔ Selected: {prev_result['name']} - {prev_result['address']}")
        else:
            print("✖ No match selected last time.")
        return prev_result
    

    # Optionally limit to Rhode Island for your use case
    places = gmaps.places(place_name)
    results = places.get('results', [])
    if places['status'] == 'OK' and results:
        print("\nGoogle found the following possible matches:")
        for i, result in enumerate(results):
            print(f"{i+1}. {result.get('name', '(no name)')} - {result.get('formatted_address', '(no address)')}")
        print("0. None of these")

        # Get user selection
        while True:
            try:
                choice = int(input("Select the best match by number (or 0 to skip): "))
                if 0 <= choice <= len(results):
                    break
            except ValueError:
                pass
            print("Invalid input. Please enter a number from the list.")

        if choice == 0:
           out = {"found": False, "address": None, "parsed_address": None}
        else:
           selected = results[choice-1]
           address = selected.get('formatted_address')
           parsed = parse_usps_address(address)
           out = {
               "found": True,
               "address": address,
               "parsed_address": parsed,
               "name": selected.get('name'),
               "place_id": selected.get('place_id')
           }

        # Cache the result for this place_name (even if not found, so you don't ask again)
        google_places_cache[cache_key] = out
        return out

    else:
        out = {"found": False, "address": None, "parsed_address": None}
        google_places_cache[cache_key] = out
        return out


def validate_google_address(address):
    """
    Validates an address using Google Geocoding API.
    Returns dict with 'valid' boolean and 'formatted_address' string.
    """
    if not address or str(address).strip().lower() in ['n/a', 'na']:
        return {"valid": False, "formatted_address": None, "error": "Address missing or invalid"}

    geocode_result = gmaps.geocode(address)

    if geocode_result:
        
        if geocode_result and 'partial_match' in geocode_result[0] and geocode_result[0]['partial_match']:
            return {
                "valid": False,
                "corrected_address": None,
                "error": "Partial match found (Google)"
            }   
        
        formatted_address = geocode_result[0].get('formatted_address')

        address_components = extract_google_address_components(geocode_result[0].get('address_components', []))


        if geocode_result and 'geometry' in geocode_result[0] and 'location' in geocode_result[0]['geometry']:
           lat = geocode_result[0]['geometry']['location']['lat']
           lng = geocode_result[0]['geometry']['location']['lng']
           google_maps_url = f"https://www.google.com/maps?q={lat},{lng}"
        else:
          lat = None
          lng = None
          google_maps_url = ""

        neighborhood = address_components.get('neighborhood', '')
        sublocality = address_components.get('sublocality', '')
        subpremise = address_components.get('apt', '')

        if subpremise:
            apt = extract_unit_number(subpremise)
        else:
            apt = ''


        # Display options to user
        print("\n")
        print(f"Suggested address: {formatted_address}" + (f" (Neighborhood: {neighborhood}, Sublocality: {sublocality}, Subpremise: {subpremise})" if neighborhood or sublocality or subpremise else ""))
        print(f"Google Maps URL: {google_maps_url}")
        print("\n")
        decision = input("Choose action: (A)ccept / (S)kip: ").strip().lower()

        if decision == 'a':


            # Parse the standardized address components
            addr = parse_usps_address(formatted_address, apt)

            return {
                "valid": True,
                "corrected_address": formatted_address,
                "google_maps_url": google_maps_url,
                "parsed_address": addr
            }
            
        else:
            print("Address skipped by the user. (Google) ")

            return {
                "valid": False,
                "corrected_address": None,
                "error": "reviewed and skipped by user (Google)"
            }    
      
      
      
      
      
      
        return {"valid": True, "formatted_address": formatted_address}
    else:
        return {"valid": False, "formatted_address": None}