from typing import List

from tools.esi.rest import HttpError
from tools.esi.universe_calls import get_ids_by_terms, get_systems, get_systems_names

def main():
    event_get_systems = {
        "function": "get_systems",
        "parameters": []
    }

    event_get_systems_names = {
        "function": "get_systems_names",
        "parameters": [
            {
                "name": "system_ids",
                "value": [30000142, 30000144, 30000146]
            }
        ]
    }

    event_get_ids_by_terms = {
        "function": "get_ids_by_terms",
        "parameters": [
            {
                "name": "terms",
                "value": ["Jita", "Tengu"]
            }
        ]
    }

    results = lambda_handler(event_get_ids_by_terms, None)
    print(results)

def lambda_handler(event: dict, context: dict) -> dict:
    function_name = event.get("function", "UNKNOWN")
    parameters = event.get("parameters", [])
    parameters_dict = {param["name"]: param["value"] for param in parameters}

    try:
        if function_name == "get_systems":
            return get_systems()    
        elif function_name == "get_systems_names":
            # Grab our parameters and validate them
            system_ids = parameters_dict.get("system_ids", [])
            is_a_list = isinstance(system_ids, list)
            contains_ints = all(isinstance(x, int) for x in system_ids)

            if not system_ids or is_a_list and not contains_ints:
                return {
                    "statusCode": 400,
                    "body": "Invalid system_ids parameter; must exist and be a list of integers"
                }
            return get_systems_names(system_ids)
        
        elif function_name == "get_ids_by_terms":
            terms = parameters_dict.get("terms", [])
            is_a_list = isinstance(terms, list)
            contains_strings = all(isinstance(x, str) for x in terms)

            if not terms or is_a_list and not contains_strings:
                return {
                    "statusCode": 400,
                    "body": "Invalid terms parameter; must exist and be a list of strings"
                }
            return get_ids_by_terms(terms).to_dict()

        else:
            return {
                "statusCode": 400,
                "body": "No function specified"
            }
    except HttpError as e:
        return {
            "statusCode": e.status_code,
            "body": str(e)
        }

if __name__ == "__main__":
    main()