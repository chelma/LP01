import requests
from typing import List

from tools.rest import HttpError

EVE_REST_URL = "https://esi.evetech.net/latest/"

def get_systems() -> List[int]:
    url =  EVE_REST_URL + "universe/systems/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HttpError(response.status_code, f"Request failed with status code: {response.status_code}")
    
def get_systems_names(system_ids: List[int]) -> List[str]:
    url =  EVE_REST_URL + "universe/names/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.post(url, headers=headers, json=system_ids)

    if response.status_code == 200:
        return [entry['name'] for entry in response.json()]
    else:
        raise HttpError(response.status_code, f"Request failed with status code: {response.status_code}")