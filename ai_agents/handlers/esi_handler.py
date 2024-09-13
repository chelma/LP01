import logging
from typing import List

from tools.esi.rest import HttpError
from tools.check_route import check_route, AmbiguousRouteError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def main():
    event_check_route = {
        "function": "checkRoute",
        "parameters": [
            {
                "name": "startingSystem",
                "value": "Jita"
            },
            {
                "name": "endingSystem",
                "value": "Mahtista"
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
        if function_name == "checkRoute":
            startingTerm = parameters_dict.get("startingSystem", "")
            logger.debug(f"startingTerm: {startingTerm}")
            endingTerm = parameters_dict.get("endingSystem", "")
            logger.debug(f"endingTerm: {endingTerm}")
            all_terms_defined = startingTerm and endingTerm

            if not all_terms_defined:
                return {
                    "statusCode": 400,
                    "body": "Invalid inputs; both the starting and ending systems must be defined"
                }
            return check_route(startingTerm, endingTerm).to_dict()
        else:
            return {
                "statusCode": 400,
                "body": "No function specified"
            }
    except AmbiguousRouteError as e:
        return {
            "statusCode": 404,
            "body": str(e)
        }    
    except HttpError as e:
        return {
            "statusCode": e.status_code,
            "body": str(e)
        }

if __name__ == "__main__":
    main()