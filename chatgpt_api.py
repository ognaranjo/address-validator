from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint = "https://whoplaysopenstudio.openai.azure.com/",
    api_key = "57cf6f74ba1145b5876b7550aa8d8d1d",
    api_version = "2024-07-18"
)

def analyze_with_chatgpt(text):
    """
    Uses ChatGPT to analyze if text is an address or place name.
    Returns dict with 'is_place_name' boolean and 'place_name' string.
    """
    prompt = f"""
    Determine if the following text is an address or a place name (e.g. hospital, store, school).
    If it's a place name, output its name.
    If it's an address, output 'address'.

    Text: "{text}"

    Response format:
    is_place_name: true/false
    place_name: name if place, else 'N/A'
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "You are an assistant for text classification."},
            {"role": "user", "content": prompt}
        ]
    )

    result_text = response.choices[0].message.content

    # Parse result
    is_place = 'true' in result_text.lower()
    place_name_line = [line for line in result_text.splitlines() if 'place_name' in line.lower()]
    place_name = place_name_line[0].split(':')[1].strip() if place_name_line else 'N/A'

    return {"is_place_name": is_place, "place_name": place_name}
