import logging
from typing import List

from tools.esi.rest import HttpError
from tools.generate_route import get_systems_by_terms

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set to DEBUG level to capture all messages

def main():
    event_check_route = {
        "function": "check_route",
        "parameters": [
            {
                "name": "system_names",
                "value": ["Jita", "Amarr"]
            }
        ]
    }

    results = lambda_handler(event_check_route, None)
    print(results)

def lambda_handler(event: dict, context: dict) -> dict:
    logger.debug(f"event body:\n{event}")
    logger.debug(f"context body:\n{context}")

    function_name = event.get("function", "UNKNOWN")
    parameters = event.get("parameters", [])
    parameters_dict = {param["name"]: param["value"] for param in parameters}

    logger.debug(f"function_name: {function_name}")
    logger.debug(f"parameters_dict: {parameters_dict}")

    try:
        if function_name == "check_route":
            terms = parameters_dict.get("system_names", [])
            is_a_list = isinstance(terms, list)
            contains_strings = all(isinstance(x, str) for x in terms)

            if not terms or is_a_list and not contains_strings:
                return {
                    "statusCode": 400,
                    "body": "Invalid terms parameter; must exist and be a list of strings"
                }
            return get_systems_by_terms(terms)
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