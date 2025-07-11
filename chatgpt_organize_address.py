from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint="https://whoplaysopenstudio.openai.azure.com/",
    api_key="57cf6f74ba1145b5876b7550aa8d8d1d",
)



def organize_address_with_chatgpt(row):
    """
    Uses ChatGPT to parse messy address data into:
    - structured address fields
    - place/organization name if any
    - possible alternative spellings or addresses

    Returns dict with:
    street_number, street_name, apt, city, state, zip, ref, place_name, alternative_addresses[]
    """
    nearby_zipcodes = []

    # If city is Riverside, ensure 02915 and 02914 are included
    if row.get('tx_town', '').strip().lower() == 'riverside':
       for zip_candidate in ['02915', '02914']:
           if zip_candidate not in nearby_zipcodes and zip_candidate != row.get('cd_zip', '').strip():
              nearby_zipcodes.append(zip_candidate)



    prompt = f"""
You are an advanced address parsing assistant. Given the following address fields from a spreadsheet row:

TX_TOWN: {row.get('tx_town', '')}
CD STATE: {row.get('cd_state', '')}
CD_ZIP: {row.get('cd_zip', '')}
AD_STRT_NBR: {row.get('ad_strt_nbr', '')}
AD_STRT_NME: {row.get('ad_strt_nme', '')}
AD_Line2: {row.get('ad_line2', '')}
AD_Line3: {row.get('ad_line3', '')}
Apt: {row.get('apt', '')}

Perform the following:

1. Determine the **most likely structured address information**.  
2. Identify any **place or organization name** if it exists in any of the fields.  
3. Detect any potential **misspellings** and provide alternative spellings or similar address suggestions.

If the street number contains a decimal like '45.5', convert it to USPS-compliant fraction format (e.g. '45 1/2').

Additionally, provide an array of 5-7 nearby ZIP codes for the given city/state, even if the address includes a ZIP code. These will be used as alternative ZIP codes for address validation.

"""

    # Conditionally add your pre-added ZIP codes if they exist
    if nearby_zipcodes:
        prompt += f"""

Here are some nearby ZIP codes that must be included if relevant:
{', '.join(nearby_zipcodes)}.

"""
    # Continue with your prompt JSON return instructions
    prompt += """    
Return your response in **JSON format** with keys:
- street_number
- street_name
- apt
- city
- state (default to 'RI' if missing)
- zip
- ref (1=AD_STRT_NME, 2=AD_Line2, 3=AD_Line3, 4=Apt)
- place_name (if any, else 'N/A')
- alternative_addresses (array of alternative address strings, can be empty [])
- nearby_zipcodes (array of 5-7 possible ZIP codes for the zipcode/city/state)

If all fields are blank, return null.

Please output only valid raw JSON, without any markdown code block formatting.

Example output:
{{
  "street_number": "123",
  "street_name": "Main St",
  "apt": "2B",
  "city": "Providence",
  "state": "RI",
  "zip": "02903",
  "ref": 2,
  "place_name": "CVS Pharmacy",
  "alternative_addresses": ["123 Main Street", "123 Main St."]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a precise, structured data parser."},
            {"role": "user", "content": prompt}
        ]
    )

    import json
    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print("Error parsing ChatGPT response:", e)
        return None
