from typing import Dict, List

from tools.esi.universe_calls import get_ids_by_terms, GetIdsByTermHit, HitCategory

class AmbiguousRouteError(Exception):
    def __init__(self, ambigious_hits: Dict[str, List[GetIdsByTermHit]], systems_not_found: List[str]):
        message = "Ambiguous route."
        if ambigious_hits:
            message += f"\nThe following named systems had multiple matches: {str(ambigious_hits)}"
        if systems_not_found:
            message += f"\nThe following named systems had no matches: {str(systems_not_found)}"
        
        super().__init__(message)
        ambigious_hits = ambigious_hits
        systems_not_found = systems_not_found

"""
Searches for systems containing the specified search terms and returns a list of hits for each term
"""
def get_systems_by_terms(search_terms: List[str]) -> Dict[str, List[GetIdsByTermHit]]:
    search_results = get_ids_by_terms(search_terms)

    systems = {}
    for search_term in search_terms:
        hits_for_name = search_results.get_hits_for_term(search_term)
        if hits_for_name:
            systems[search_term] = [hit.to_dict() for hit in hits_for_name.get_hits_for_category(HitCategory.SYSTEMS)]
        else:
            systems[search_term] = []

    return systems

def check_route(system_names: List[str]):
    # First get the system details for the specified system names
    systems = get_systems_by_terms(system_names)

    # Confirm that each system name had one, and only one, result


    ambiguous_hits = {}
    systems_not_found = []
    for system_name, system_hits in systems.items():
        if len(system_hits) > 1:
            ambiguous_hits[system_name] = system_hits
        elif len(system_hits) == 0:
            systems_not_found.append(system_name)
    if ambiguous_hits or systems_not_found:
        raise AmbiguousRouteError(ambiguous_hits, systems_not_found)
    
    

    return get_systems_by_terms(system_names)