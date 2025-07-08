def build_full_google_address(full_street_address, city, state, zip_code, apt=None):
    """
    Builds a full address string formatted for Google Geocoding validation,
    including apartment prefix if applicable.
    """
    city = city.strip() if city else ''
    state = state.strip() if state else ''
    zip_code = zip_code.strip() if zip_code else ''
    apt = apt.strip() if apt else ''

    # Format apartment with prefix if present and not N/A
    if apt and apt.lower() not in ['n/a', 'na']:
        apt_formatted = f"Apt {apt}"
    else:
        apt_formatted = ''

    # Build final full address
    full_address = f"{full_street_address}, {city}, {state} {zip_code} {apt_formatted}".strip()
    
    return full_address