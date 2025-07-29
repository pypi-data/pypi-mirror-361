import turbobt
import bittensor_wallet


async def main():
    wallet = bittensor_wallet.Wallet("alice", "default")

    async with turbobt.Bittensor("ws://localhost:8000", wallet=wallet) as bt:
        subnet = bt.subnet(2)
        neurons = await subnet.list_neurons()

        print(neurons)

        await bt.subtensor.admin_utils.sudo_set_commit_reveal_weights_enabled(
            netuid=2,
            enabled=True,
            wallet=wallet,
        )

        await subnet.weights.commit({
            0: 0.2,
            1: 0.8,
        })


import asyncio

asyncio.run(main())