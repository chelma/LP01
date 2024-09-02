import requests

def main():
    results = lambda_handler(None, None)
    print(results)

def lambda_handler(event: dict, context: dict) -> dict:
    url = "https://esi.evetech.net/latest/universe/systems/"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return {
            'statusCode': 200,
            'body': response.json()
        }
    else:
        return {
            'statusCode': response.status_code,
            'body': f"Request failed with status code: {response.status_code}"
        }

if __name__ == "__main__":
    main()