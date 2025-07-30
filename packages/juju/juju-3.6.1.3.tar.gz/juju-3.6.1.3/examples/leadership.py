# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

"""This example:

1. Connects to the current model.
2. Prints out leadership status for all deployed units in the model.
3. Cleanly disconnects.

"""

import asyncio

from juju.model import Model


async def report_leadership():
    model = Model()
    await model.connect()

    print("Leadership: ")
    for app in model.applications.values():
        for unit in app.units:
            print(f"{unit.name}: {await unit.is_leader_from_status()}")

    await model.disconnect()


if __name__ == "__main__":
    asyncio.run(report_leadership())
