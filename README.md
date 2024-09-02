# LP01
A project to learn more about generative AI


### Running the code



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