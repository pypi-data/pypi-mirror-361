
import base64
import json
import sqlite3

import scalecodec
import sqlalchemy
import sqlalchemy.ext.asyncio

from turbobt.simulator.pallets.author import Author
from turbobt.simulator.pallets.chain import Chain
from turbobt.simulator.pallets.state import State
from turbobt.simulator.pallets.system import System
from turbobt.simulator.runtime.metadata import Metadata
from turbobt.simulator.runtime.neuron_info import NeuronInfoRuntimeApi
from turbobt.simulator.runtime.subnet_info import SubnetInfoRuntimeApi
from turbobt.simulator.runtime.subtensor_module import SubtensorModule
from turbobt.substrate._scalecodec import load_type_registry_v15_types
from turbobt.subtensor.client import Subtensor


class MockedSubtensor(Subtensor):
    
    def __call__(self, rpc, **params):
        api_name, method_name = rpc.split("_", 1)

        api = getattr(self, api_name)
        method = getattr(api, method_name)

        return method(**params)

    def __init__(self):
        self._block = 1
        self.db = sqlite3.connect(":memory:")   # TODO uri
        self.db.row_factory = sqlite3.Row

        self.engine = sqlalchemy.create_engine(
            "sqlite:///:memory:",
            echo=True,
        )
        self.session = sqlalchemy.orm.sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            # class_=sqlalchemy.ext.asyncio.AsyncSession,
        )

        from .db import Base

        Base.metadata.create_all(self.engine)

        # @spy
        self.chain = Chain(self)
        self.author = Author(self)
        self.state = State(self)
        self.system = System(self)

        self.SubtensorModule = SubtensorModule(self)
        self.Metadata = Metadata(self)
        self.NeuronInfoRuntimeApi = NeuronInfoRuntimeApi(self)
        self.SubnetInfoRuntimeApi = SubnetInfoRuntimeApi(self)

    async def init(self):
        response = await self.Metadata.metadata_at_version("0xff0000")

        runtime_config = scalecodec.base.RuntimeConfigurationObject()
        runtime_config.update_type_registry(
            scalecodec.type_registry.load_type_registry_preset(name="core"),
        )

        # patching-in MetadataV15 support
        runtime_config.update_type_registry_types(load_type_registry_v15_types())
        runtime_config.type_registry["types"]["metadataall"].type_mapping.append(
            ["V15", "MetadataV15"],
        )

        self._registry = runtime_config

        metadata = self._registry.create_scale_object(
            "Option<Vec<u8>>",
            data=scalecodec.ScaleBytes(response),
        )
        metadata.decode()

        if not metadata.value:
            return None

        metadata = self._registry.create_scale_object(
            "MetadataVersioned",
            data=scalecodec.ScaleBytes(metadata.value),
        )
        metadata.decode()

        self._metadata = metadata

        metadata15 = metadata.value[1]["V15"]

        runtime_config.add_portable_registry(metadata)

        self._apis = {
            api["name"]: api | {
                "methods": {
                    api_method["name"]: api_method
                    for api_method in api["methods"]
                }
            }
            for api in metadata15["apis"]
        }

    def subscribe(self, subscription_id):
        return self.author._subscriptions[subscription_id]
    
    def unsubscribe(self, subscription_id):
        return self.author._subscriptions.pop(subscription_id, None)

    async def wait_for_epoch(self):
        await self._on_epoch()

    async def _on_epoch(self):
        for netuid in (12,):
            # https://github.com/opentensor/subtensor/blob/4c9836f8cc199bc323956509f59d86d1761dd021/pallets/subtensor/src/coinbase/run_coinbase.rs#L858
            reveal_epoch = 0

            

            for (who, commit, round_number) in self.state._CRV3WeightCommits[(netuid, reveal_epoch)]:
                commit = base64.b64decode(commit).decode()
                commit = json.loads(commit)

                uid = 0

                self.state._Weights[(netuid, uid)] = list(zip(commit["uids"], commit["weights"]))

            self.state._CRV3WeightCommits[(netuid, reveal_epoch)].clear()
