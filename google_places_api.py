import googlemaps

gmaps = googlemaps.Client(key="AIzaSyA9nQeB9wXGd64qYJxCdHuO5Ty4vBbHVAI")

def search_google_places(place_name):
    """
    Searches Google Places API for a place name.
    Returns dict with 'found' boolean and 'address' string.
    """
    places = gmaps.places(place_name + " Rhode Island")
    if places['status'] == 'OK' and places['results']:
        result = places['results'][0]
        address = result.get('formatted_address')
        return {"found": True, "address": address}
    else:
        return {"found": False, "address": None}

def validate_google_address(address):
    """
    Validates an address using Google Geocoding API.
    Returns dict with 'valid' boolean and 'formatted_address' string.
    """
    if not address or str(address).strip().lower() in ['n/a', 'na']:
        return {"valid": False, "formatted_address": None, "error": "Address missing or invalid"}

    geocode_result = gmaps.geocode(address)

    if geocode_result:
        formatted_address = geocode_result[0].get('formatted_address')
        return {"valid": True, "formatted_address": formatted_address}
    else:
        return {"valid": False, "formatted_address": None}