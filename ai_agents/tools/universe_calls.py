from enum import Enum
import requests
from typing import Dict, List

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
    


class HitCategory(Enum):
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

class GetIdsByTermHit:
    def __init__(self, name: str, category: HitCategory, id: int):
        self.name = name
        self.category = category
        self.id = id

    def to_dict(self) -> Dict:
        return {"name": self.name, "category": self.category.value, "id": self.id}

    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.name == other.name and self.category == other.category and self.id == other.id
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.name, self.category, self.id))

class GetIdsByTermHits:
    def __init__(self, search_term: str, hits: Dict[str, List[GetIdsByTermHit]] = None):
        self.searchTerm = search_term
        self.hits = hits if hits else {category.value: [] for category in HitCategory}

    def add_hit(self, category: HitCategory, hit: GetIdsByTermHit):
        if category.value in self.hits:
            self.hits[category.value].append(hit)
        else:
            raise ValueError(f"Unknown category: {category}")
        
    def get_hits(self, category: HitCategory) -> List[GetIdsByTermHit]:
        return self.hits[category.value]
    
    def to_dict(self) -> Dict:
        hits_dict = {str(category): [hit.to_dict() for hit in hits] for category, hits in self.hits.items()}
        return {"search_term": self.searchTerm, "hits": hits_dict}
    
    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        return self.searchTerm == other.searchTerm and self.hits == other.hits
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash((self.searchTerm, self.hits))

class GetIdsByTermsResult:
    def __init__(self, search_terms: List[str], raw_result: Dict):
        self.search_terms = search_terms
        self.raw_result = raw_result

    def get_hits(self, search_term: str) -> GetIdsByTermHits:
        hits = GetIdsByTermHits(search_term)
        for category, hits_list in self.raw_result.items():
            for hit in hits_list:
                if search_term.lower() in hit["name"].lower():
                    hits.add_hit(HitCategory(category), GetIdsByTermHit(hit["name"], HitCategory(category), hit["id"]))
        return hits
    
    def to_dict(self) -> Dict:
        return {search_term: self.get_hits(search_term).to_dict() for search_term in self.search_terms}
    
    def __str__(self) -> str:
        return str(self.to_dict())
    
    def __repr__(self) -> str:
        return str(self)
    
    def __eq__(self, other) -> bool:
        return self.search_terms == other.search_terms and self.raw_result == other.raw_result
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash((self.search_terms, self.raw_result))





    


def get_ids_by_terms(search_terms: List[str]) -> GetIdsByTermsResult:
    url =  EVE_REST_URL + "universe/ids/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.post(url, headers=headers, json=search_terms)

    if response.status_code == 200:
        return GetIdsByTermsResult(search_terms, response.json())
    else:
        raise HttpError(response.status_code, f"Request failed with status code: {response.status_code}")