import re

def build_full_google_address(full_street_address, city, state, zip_code, apt=None):
    """
    Builds a full address string formatted for Google Geocoding validation,
    including apartment prefix if applicable.
    Omits empty fields and avoids redundant commas.
    """
    def safe(val):
        return val.strip() if val else ''
    
    parts = [
        safe(full_street_address),
        safe(city),
        safe(state),
        safe(zip_code)
    ]
    
    # Only add apartment if present and not N/A
    if apt and apt.strip() and apt.strip().lower() not in ['n/a', 'na']:
        parts.append(f"Apt {apt.strip()}")
    
    # Filter out empty parts and join
    full_address = ', '.join(part for part in parts if part)
    return full_address


def extract_google_address_components(components):
    result = {}
    type_map = {
        'street_number': 'street_number',
        'route': 'street_name',
        'locality': 'city',
        'neighborhood': 'neighborhood',
        'sublocality': 'sublocality',
        'administrative_area_level_1': 'state',
        'postal_code': 'zip',
        'country': 'country',
        'subpremise': 'apt',
        # add more if you need
    }

    for comp in components:
        for t in comp['types']:
            if t in type_map:
                result[type_map[t]] = comp['long_name']

    return result




def extract_unit_number(subpremise):
    """
    Extract just the number/number+letter from a subpremise string.
    Examples:
      'Apt 4A' → '4A'
      'Suite 101' → '101'
      'Apartment 9B' → '9B'
      'B2' → 'B2'
    """
    if not subpremise or not isinstance(subpremise, str):
        return None
    # Search for patterns like '4A', '101', '9B', etc.
    match = re.search(r'(\d+\w*)$', subpremise.strip())
    if match:
        return match.group(1)
    return subpremise.strip()  # fallback: return the whole string

