import logging
from typing import Dict, List

from tools.esi.universe_calls import get_ids_by_terms, TermSearchHit, TermsHitCategory, get_route_by_ids, get_names_by_ids, get_system_jumps, get_system_kills, GetNamesByIdsResult, IdSearchHit

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class AmbiguousRouteError(Exception):
    def __init__(self, ambigious_hits: Dict[str, List[TermSearchHit]], systems_not_found: List[str]):
        message = "Ambiguous route."
        if ambigious_hits:
            message += f"\nThe following named systems had multiple matches: {str(ambigious_hits)}"
        if systems_not_found:
            message += f"\nThe following named systems had no matches: {str(systems_not_found)}"
        
        super().__init__(message)
        ambigious_hits = ambigious_hits
        systems_not_found = systems_not_found


class RouteEntry:
    def __init__(self, id: int, system_name: str, kills: int = None, jumps: int = None):
        self.system_id = id
        self.system_name = system_name
        self.kills = kills
        self.jumps = jumps

    def to_dict(self) -> Dict:
        return {"system_id": self.system_id, "system_name": self.system_name, "kills": self.kills, "jumps": self.jumps}

    def __str__(self):
        return str(self.to_dict())
    
class Route:
    def __init__(self, entries: List[RouteEntry] = []):
        self.route_ordered = entries
        self.entries_dict = {entry.system_id: entry for entry in entries}

    def add_entry(self, entry: RouteEntry):
        self.route_ordered.append(entry)
        self.entries_dict[entry.system_id] = entry

    def to_dict(self) -> Dict:
        return [entry.to_dict() for entry in self.route_ordered]

    def __str__(self):
        return str(self.to_dict())

"""
Searches for systems containing the specified search terms and returns a list of hits for each term
"""
def get_systems_by_terms(search_terms: List[str]) -> Dict[str, List[TermSearchHit]]:
    search_results = get_ids_by_terms(search_terms)

    systems = {}
    for search_term in search_terms:
        hits_for_name = search_results.get_hits_for_term(search_term)
        if hits_for_name:
            systems[search_term] = [hit for hit in hits_for_name.get_hits_for_category(TermsHitCategory.SYSTEMS)]
        else:
            systems[search_term] = []

    return systems

def construct_route(route_ids: List[int], get_names_result: GetNamesByIdsResult, raw_system_jumps: List[Dict], raw_system_kills: List[Dict]) -> Route:
    route = Route()

    for system_id in route_ids:
        kills = None
        jumps = None
        for system in raw_system_kills:
            if system["system_id"] == system_id:
                kills = system["ship_kills"]
                break
        for system in raw_system_jumps:
            if system["system_id"] == system_id:
                jumps = system["ship_jumps"]
                break
        system_name = get_names_result.get_hit_for_id(system_id).name
        logger.info(f"Adding route entry for {system_name} / {system_id} with {kills} kills and {jumps} jumps")
        route.add_entry(RouteEntry(system_id, system_name, kills, jumps))
    return route

def check_route(starting_system: str, ending_system: str) -> List[Dict]:
    # First get the system details for the specified system names
    systems = get_systems_by_terms([starting_system, ending_system])

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
    
    starting_system_id = systems[starting_system][0].id
    ending_system_id = systems[ending_system][0].id
    logger.info(f"Starting System ({starting_system} / {starting_system_id}) and Ending System ({ending_system} / {ending_system_id}) found")
    
    # Now that we have the system IDs, we can retrieve the raw route ids
    raw_route_ids = get_route_by_ids(starting_system_id, ending_system_id)
    logger.info(f"Raw Route IDs: {raw_route_ids}")

    # Now get the names for each of those system IDs
    get_names_result = get_names_by_ids(raw_route_ids)

    # Now retrieve the supplemental information
    raw_system_jumps = get_system_jumps()
    raw_system_kills = get_system_kills()

    # Construct/return the route
    route = construct_route(raw_route_ids, get_names_result, raw_system_jumps, raw_system_kills)
    return route.to_dict()