import requests

EVE_REST_URL = "https://esi.evetech.net/latest/"


def main():
    event_get_systems = {
        'function': 'get_systems',
    }

    event_get_systems_names = {
        'function': 'get_systems_names',
        'parameters': [
            {
                'name': 'system_ids',
                'value': [30000142, 30000144, 30000146]
            }
        ]
    }

    results = lambda_handler(event_get_systems_names, None)
    print(results)

def lambda_handler(event: dict, context: dict) -> dict:
    function_name = event.get('function', "UNKNOWN")
    parameters = event.get('parameters', [])
    parameters_dict = {param['name']: param['value'] for param in parameters}

    if function_name == "get_systems":
        return get_systems()    
    elif function_name == "get_systems_names":
        # Grab our parameters and validate them
        system_ids = parameters_dict.get('system_ids', [])
        is_a_list = isinstance(system_ids, list)
        contains_ints = all(isinstance(x, int) for x in system_ids)

        if not system_ids or is_a_list and not contains_ints:
            return {
                'statusCode': 400,
                'body': "Invalid system_ids parameter; must exist and be a list of integers"
            }
        return get_systems_names(system_ids)

    else:
        return {
            'statusCode': 400,
            'body': "No function specified"
        }
    
def get_systems() -> dict:
    url =  EVE_REST_URL + "universe/systems/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            'statusCode': response.status_code,
            'body': f"Request failed with status code: {response.status_code}"
        }
    
def get_systems_names(system_ids: list) -> dict:
    url =  EVE_REST_URL + "universe/names/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.post(url, headers=headers, json=system_ids)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            'statusCode': response.status_code,
            'body': f"Request failed with status code: {response.status_code}"
        }

if __name__ == "__main__":
    main()