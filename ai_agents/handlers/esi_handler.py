import logging
from typing import List

from tools.esi.rest import HttpError
from tools.check_route import check_route, AmbiguousRouteError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def main():
    event_check_route = {
        "actionGroup": "ag-esi-api",
        "apiPath": "/checkRoute",
        "httpMethod": "POST",
        "requestBody": {
            "content": {
                "application/json": {
                    "properties": [{
                        "name": "startingSystem",
                        "type": "string",
                        "value": "Jita"
                    }, {
                        "name": "endingSystem",
                        "type": "string",
                        "value": "Amarr"
                    }]
                }
            }
        }
    }

    results = lambda_handler(event_check_route, None)
    print(results)

def lambda_handler(event: dict, context: dict) -> dict:
    logger.debug(f"event body:\n{event}")
    logger.debug(f"context body:\n{context}")

    api_path = event.get("apiPath", "UNKNOWN")
    parameters = event.get("requestBody", {}).get("content", {}).get("application/json", {}).get("properties", [])
    parameters_dict = {param["name"]: param["value"] for param in parameters}

    logger.debug(f"api_path: {api_path}")
    logger.debug(f"parameters_dict: {parameters_dict}")

    status_code = None
    response_body = None

    try:
        if api_path == "/checkRoute":
            startingTerm = parameters_dict.get("startingSystem", "")
            logger.debug(f"startingTerm: {startingTerm}")
            endingTerm = parameters_dict.get("endingSystem", "")
            logger.debug(f"endingTerm: {endingTerm}")
            all_terms_defined = startingTerm and endingTerm

            if not all_terms_defined:
                status_code = 400
                response_body = "Invalid inputs; both the starting and ending systems must be defined"
            else:
                status_code = 200
                response_body = str(check_route(startingTerm, endingTerm).to_dict())
        else:
            status_code = 400
            response_body = "No function specified"
    except AmbiguousRouteError as e:
        status_code = 404
        response_body = str(e)
    except HttpError as e:
        status_code =  e.status_code
        response_body = str(e)

    response = {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup", "UNKNOWN"),
            "apiPath": event.get("apiPath", "UNKNOWN"),
            "httpMethod": event.get("httpMethod", "UNKNOWN"),
            "httpStatusCode": status_code,
            "responseBody": {
                "application/json": {
                    "body": response_body
                }
            }
        },
    }
    logger.debug(f"Response: {response}")

    return response

if __name__ == "__main__":
    main()