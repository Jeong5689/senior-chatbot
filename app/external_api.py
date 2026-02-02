import requests
import os

def get_nearby_pharmacy(city_name: str, area_name: str):
    api_key = os.getenv("PUBLIC_DATA_API_KEY")
    url = os.getenv("PHARMACY_API_URL")
    
    params = {
        'serviceKey': api_key,
        'Q0': city_name,
        'Q1': area_name,
        '_type': 'json'
    }
    response = requests.get(url, params=params)
    return response.json()