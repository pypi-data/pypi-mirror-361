# simt-py-fly-machines

[![Python checks](https://github.com/cepro/simt-py-fly-machines/actions/workflows/python-checks.yml/badge.svg)](https://github.com/cepro/simt-py-fly-machines/actions/workflows/python-checks.yml)

A python API to start, stop and list Fly.io machines using the [Machines REST API](https://docs.machines.dev/#description/introduction).

## Local Development

```
> python3 -m venv .venv
> source .venv/bin/activate

(.venv)> pip install -U pip setuptools
(.venv)> pip install poetry

(.venv)> poetry install
```

## Publish

Use account `damonrand` and publishing to test-pypi for now.

```
poetry publish --build -r test-pypi
```

## Local Testing CLI (Fire)

Locally fire is available to invoke the API from CLI.

Example invocation:
```sh
# List machines
python -m simt_fly_machines.cli list mediators-hmce

# Create new machine
python -m simt_fly_machines.cli \
    create \
        mediators-hmce \
        simt-emlite:0.9.4 \
        '["simt_emlite.orchestrate.mediators"]' \
            --name "mediator-100.79.244.203" \
            --env_vars '{"EMLITE_HOST": "100.79.244.203"}' \
            --metadata '{"meter_id": "a4d636c3-9b13-4261-89ab-c018e86120e8"}'

# Destroy machine
python -m simt_fly_machines.cli destroy mediators-hmce d8dd67ea074138
```
