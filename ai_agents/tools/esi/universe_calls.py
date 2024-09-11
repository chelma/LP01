from enum import Enum
import requests
from typing import Dict, List

from tools.esi.rest import HttpError

EVE_REST_URL = "https://esi.evetech.net/latest"

def get_systems() -> List[int]:
    url =  f"{EVE_REST_URL}/universe/systems/"
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
    url =  f"{EVE_REST_URL}/universe/names/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.post(url, headers=headers, json=system_ids)

    if response.status_code == 200:
        return [entry['name'] for entry in response.json()]
    else:
        raise HttpError(response.status_code, f"Request failed with status code: {response.status_code}")
    

# The possible categories of results when searching by term
class TermsHitCategory(Enum):
    AGENTS = "agents"
    ALLIANCES = "alliances"
    CHARACTERS = "characters"
    CONSTELLATIONS = "constellations"
    CORPORATIONS = "corporations"
    FACTIONS = "factions"
    INVENTORY_TYPES = "inventory_types"
    REGIONS = "regions"
    STATIONS = "stations"
    SYSTEMS = "systems"

class TermSearchHit:
    def __init__(self, name: str, category: TermsHitCategory, id: int):
        self.name = name
        self.category = category
        self.id = id

    def to_dict(self) -> Dict:
        return {"name": self.name, "category": self.category.value, "id": self.id}

    def __str__(self):
        return str(self.to_dict())

class TermSearchHits:
    def __init__(self, search_term: str, hits: Dict[str, List[TermSearchHit]] = None):
        self.search_term = search_term
        self.hits = hits if hits else {category.value: [] for category in TermsHitCategory}

    def add_hit(self, category: TermsHitCategory, hit: TermSearchHit):
        if category.value in self.hits:
            self.hits[category.value].append(hit)
        else:
            raise ValueError(f"Unknown category: {category}")
        
    def get_hits_for_category(self, category: TermsHitCategory) -> List[TermSearchHit]:
        return self.hits[category.value]
    
    def to_dict(self) -> Dict:
        hits_dict = {str(category): [hit.to_dict() for hit in hits] for category, hits in self.hits.items()}
        return {"search_term": self.search_term, "hits": hits_dict}
    
    def __str__(self):
        return str(self.to_dict())

class GetIdsByTermsResult:
    def __init__(self, search_terms: List[str], raw_result: Dict):
        self.search_terms = search_terms
        self.raw_result = raw_result

    def get_hits_for_term(self, search_term: str) -> TermSearchHits:
        hits = TermSearchHits(search_term)
        for category, hits_list in self.raw_result.items():
            for hit in hits_list:
                if search_term.lower() in hit["name"].lower():
                    hits.add_hit(TermsHitCategory(category), TermSearchHit(hit["name"], TermsHitCategory(category), hit["id"]))
        return hits
    
    def to_dict(self) -> Dict:
        return {search_term: self.get_hits_for_term(search_term).to_dict() for search_term in self.search_terms}
    
    def __str__(self) -> str:
        return str(self.to_dict())

def get_ids_by_terms(search_terms: List[str]) -> GetIdsByTermsResult:
    url =  f"{EVE_REST_URL}/universe/ids/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.post(url, headers=headers, json=search_terms)

    if response.status_code == 200:
        return GetIdsByTermsResult(search_terms, response.json())
    else:
        raise HttpError(response.status_code, f"Request failed with status code: {response.status_code}")
    
def get_route_by_ids(starting_system: int, ending_system: int, flag="shortest") -> List[int]:
    url =  f"{EVE_REST_URL}/route/{str(starting_system)}/{str(ending_system)}/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.get(url, headers=headers, params={"flag": flag})

    if response.status_code == 200:
        return response.json()
    else:
        raise HttpError(response.status_code, f"Request failed with status code: {response.status_code}")
    
# The possible categories of results when searching by Id
class IdsHitCategory(Enum):
    ALLIANCE = "alliance"
    CHARACTER = "character"
    CONSTELLATION = "constellation"
    CORPORATION = "corporation"
    FACTION = "faction"
    INVENTORY_TYPE = "inventory_type"
    REGION = "region"
    SOLAR_SYSTEM = "solar_system"
    STATION = "station"
    
class IdSearchHit:
    def __init__(self, name: str, category: IdsHitCategory, id: int):
        self.name = name
        self.category = category
        self.id = id

    def to_dict(self) -> Dict:
        return {"name": self.name, "category": self.category.value, "id": self.id}

    def __str__(self):
        return str(self.to_dict())
    
class GetNamesByIdsResult:
    def __init__(self, ids: List[int], raw_result: List[Dict]):
        self.ids = ids
        self.raw_result = raw_result

    def get_hit_for_id(self, id: int) -> IdSearchHit:
        for entry in self.raw_result:
            if id == entry["id"]:
                return IdSearchHit(entry["name"], IdsHitCategory(entry["category"]), entry["id"])
        return None
    
    def to_dict(self) -> Dict:
        return {id: self.get_hits_for_id(id).to_dict() for id in self.ids}
    
    def __str__(self) -> str:
        return str(self.to_dict())
    
def get_names_by_ids(ids: List[int]) -> GetNamesByIdsResult:
    url =  f"{EVE_REST_URL}/universe/names/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.post(url, headers=headers, json=ids)

    if response.status_code == 200:
        return GetNamesByIdsResult(ids, response.json())
    else:
        raise HttpError(response.status_code, f"Request failed with status code: {response.status_code}")
    
def get_system_jumps() -> List[Dict]:
    url =  f"{EVE_REST_URL}/universe/system_jumps/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HttpError(response.status_code, f"Request failed with status code: {response.status_code}")
    
def get_system_kills() -> List[Dict]:
    url =  f"{EVE_REST_URL}/universe/system_kills/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HttpError(response.status_code, f"Request failed with status code: {response.status_code}")