from typing import List

import requests
import random

FLY_API_HOST = "api.machines.dev"
FLY_ORG = "cepro"
# FLY_REGION = "lhr"  # London, United Kingdom
FLY_REGION = "ams"  # Amsterdam


class API:
    def __init__(self, fly_api_token: str):
        self.headers = {
            "Authorization": f"Bearer {fly_api_token}",
            "Content-Type": "application/json",
        }

    def create(
        self,
        app: str,
        image: str,
        cmd: List[str],
        name=None,
        # If port is not provided a random port between 51000 and 59000 will be assigned
        port=None,
        additional_internal_port=None,
        env_vars: dict = {},
        metadata: dict = {},
        # additional config that can be merged into, and override the main config using Python's union operator
        extra_config: dict = {},
    ):
        port = random.randint(51000, 59000) if port is None else port

        services_config = [
            {
                "autostart": True,
                "autostop": True,
                "internal_port": 50051,
                "ports": [{"port": port}],
            }
        ]

        if additional_internal_port:
            services_config.append(
                {
                    "autostart": True,
                    "autostop": True,
                    "internal_port": additional_internal_port,
                }
            )

        machine_config = {
            "name": name,
            "region": FLY_REGION,
            "config": {
                "image": image,
                "env": env_vars,
                "metadata": metadata,
                "processes": [{"cmd": cmd}],
                "services": services_config,
            },
        }

        if extra_config:
            machine_config |= extra_config

        response = requests.post(
            self._uri(app), headers=self.headers, json=machine_config
        )

        return response.json()

    def list(self, app: str, metadata_filter: tuple[str, str] | None = None):
        response = requests.get(
            f"{self._uri(app)}?region={FLY_REGION}", headers=self.headers
        )
        response_json = response.json()

        if metadata_filter is not None:
            filtered_machines = list(
                filter(
                    lambda m: m["config"]["metadata"][metadata_filter[0]]
                    == metadata_filter[1],
                    response_json,
                )
            )
        else:
            filtered_machines = response_json

        return filtered_machines

    def get(self, app: str, machine_id: str):
        response = requests.get(
            self._uri(app, machine_id),
            headers=self.headers,
        )
        return response.json()

    def wait(self, app: str, machine_id: str, instance_id: str, state: str):
        response = requests.get(
            f"{self._uri(app, machine_id)}/wait?state={state}&instance_id={instance_id}",
            headers=self.headers,
        )
        return response.json()

    def destroy(
        self,
        app: str,
        machine_id: str | None = None,
        machine_name: str | None = None,
        force: bool = False,
    ):
        matching = list(
            filter(
                lambda m: m["id"] == machine_id or m["name"] == machine_name,
                self.list(app),
            )
        )
        if len(matching) == 0:
            print("no matching machine")
            return

        machine_id = matching[0]["id"]

        # needs a lowercase t so set it explicitly like this:
        force_value = "true" if force else "false"

        response = requests.delete(
            f"{self._uri(app, machine_id)}?force={force_value}", headers=self.headers
        )
        return response.json()

    def start(self, app: str, machine_id: str):
        print(self._uri(app, machine_id))
        response = requests.post(
            f"{self._uri(app, machine_id)}/start", headers=self.headers
        )
        return response.json()

    def stop(self, app: str, machine_id: str):
        response = requests.post(
            f"{self._uri(app, machine_id)}/stop", headers=self.headers
        )
        return response.json()

    def _uri(self, app, machine_id=None) -> str:
        base_uri = f"https://{FLY_API_HOST}/v1/apps/{app}/machines"
        if machine_id is not None:
            base_uri = base_uri + f"/{machine_id}"
        return base_uri
