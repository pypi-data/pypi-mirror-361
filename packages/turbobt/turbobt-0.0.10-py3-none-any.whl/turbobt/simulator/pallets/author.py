import asyncio

import scalecodec
import scalecodec.utils.ss58
from turbobt.substrate.pallets._base import Pallet


class Author(Pallet):
    def __init__(self, substrate):
        super().__init__(substrate)

        self._subscriptions = {}

    async def unwatchExtrinsic(self, bytes):
        self._subscriptions.pop(bytes, None)
        return None

    async def submitAndWatchExtrinsic(self, bytes):
        extrinsic_cls = self.substrate._registry.get_decoder_class("Extrinsic")
        extrinsic = extrinsic_cls(
            data=scalecodec.ScaleBytes(bytes),
            metadata=self.substrate._metadata,
        )
        extrinsic.decode()

        self.substrate.chain._extrinsics.append(extrinsic)

        extrinsic = extrinsic.value

        call_module = getattr(self.substrate, extrinsic["call"]["call_module"])
        call_function = getattr(call_module, extrinsic["call"]["call_function"])

        await call_function(
            scalecodec.utils.ss58.ss58_encode(extrinsic["address"]),
            **{
                arg["name"]: (
                    scalecodec.utils.ss58.ss58_encode(arg["value"])
                    if arg["type"] == "AccountId"
                    else arg["value"]
                )
                for arg in extrinsic["call"]["call_args"]
            }
        )

        subscription = asyncio.Queue()
        subscription.put_nowait("ready")
        subscription.put_nowait({"broadcast":["12D3KooWQgG8BL8VB6aXdzvnadkbJiQ6HnoxjSjrD9kuXuGGhP46"]})
        subscription.put_nowait({"inBlock":"0xf0aa135ddac82c7b5ea0de2b021945381bc6a449fdd44386d9956fa0a5ee1e05"})
        subscription.put_nowait({"finalized":"0xf0aa135ddac82c7b5ea0de2b021945381bc6a449fdd44386d9956fa0a5ee1e05"})

        self._subscriptions["0x53364b7062576d6853326a5341736338"] = subscription

        return "0x53364b7062576d6853326a5341736338"
