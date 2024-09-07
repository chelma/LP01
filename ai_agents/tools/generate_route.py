from typing import List

from tools.esi.universe_calls import get_ids_by_terms, GetIdsByTermHit, HitCategory

"""
Searches for systems containing the specified search terms and returns a list of hits
"""
def get_systems_by_terms(search_terms: List[str]) -> List[GetIdsByTermHit]:
    # Start by checking for ids with the listed names
    search_results = get_ids_by_terms(search_terms)

    # Now we need to filter out the system ids
    system_ids = {}
    for system_name in search_terms:
        hits_for_name = search_results.get_hits_for_term(system_name)
        if hits_for_name:
            system_ids[system_name] = [hit.to_dict() for hit in hits_for_name.get_hits_for_category(HitCategory.SYSTEMS)]
        else:
            system_ids[system_name] = []

    return system_ids


