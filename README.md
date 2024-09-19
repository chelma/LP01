# LP01
A project to learn more about generative AI

This particular project demonstrates the ability to define and deploy an Amazon Bedrock Agent that can use a single Lambda Function as a Tool to check the danger-level of routes between starsystems in the MMORPG EVE Online's in-game universe.  To answer these questions, the Tool uses the EVE Swagger Interface (ESI) for REST calls against the game universe.  You can either invoke the Lambda directly by running the code locally (as explained below), or you can deploy using Terraform and chat with the Agent in the AWS Console (also explained below).

### Running the code

#### Locally
To run the code locally, use a Python virtual environment:

```
# Start in the repo root

python3 -m venv venv
source venv/bin/activate

cd ai_agents
pipenv sync --dev
python3 -m handlers.check_route_handler
```

#### In AWS
The package uses Terraform to manage its cloud deployments.  You'll need valid AWS Credentials in your keyring (check using `aws sts get-caller-identity`).

```
cd ai_agents

./package.sh

terraform init
terraform plan
terraform apply
```

You can then run the Lambda manually in the AWS console using test events.

### Dependencies
`pipenv` is used to managed dependencies within the project.  The `Pipefile` and `Pipefile.lock` handle the local environment.  You can add dependencies like so:

```
pipenv install boto3
```

This updates the `Pipfile`/`Pipfile.lock` with the new dependency.  To create a local copy of the dependencies, such as for bundling a distribution, you can use pip like so:

```
pipenv requirements > requirements.txt
python3 -m pip install -r requirements.txt -t ./package --upgrade

zip -r9 ai_agents.zip tools/ package/
```