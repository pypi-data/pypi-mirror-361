# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""This example:

1. Connects to current controller.
2. Loads kube config from microk8s.
3. Adds a k8s cloud.
4. Adds a userpass credential for the cloud.

"""

import asyncio
import base64
import logging
import os

import yaml

from juju.client import client
from juju.controller import Controller


async def main():
    kubecfg = os.popen("microk8s.config").read()  # noqa: S607,S605
    cfg = yaml.safe_load(kubecfg)
    ctx = {v["name"]: v["context"] for v in cfg["contexts"]}[cfg["current-context"]]
    cluster = {v["name"]: v["cluster"] for v in cfg["clusters"]}[ctx["cluster"]]
    user = {v["name"]: v["user"] for v in cfg["users"]}[ctx["user"]]

    ep = cluster["server"]
    ca_cert = base64.b64decode(cluster["certificate-authority-data"]).decode("utf-8")

    controller = Controller()
    await controller.connect()

    cloud = client.Cloud(
        auth_types=["userpass"],
        ca_certificates=[ca_cert],
        endpoint=ep,
        host_cloud_region="microk8s/localhost",
        regions=[client.CloudRegion(endpoint=ep, name="localhost")],
        type_="kubernetes",
    )
    cloud = await controller.add_cloud("test", cloud)

    cred = client.CloudCredential(
        auth_type="userpass",
        attrs={"username": user["username"], "password": user["password"]},
    )
    await controller.add_credential("test", credential=cred, cloud="test")

    await controller.remove_cloud("test")
    await controller.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ws_logger = logging.getLogger("websockets.protocol")
    ws_logger.setLevel(logging.INFO)
    asyncio.run(main())
