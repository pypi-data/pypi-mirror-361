import collections

import scalecodec.utils.ss58

class NeuronInfoRuntimeApi:
    def __init__(self, substrate):
        self.substrate = substrate

        self.substrate.db.execute(
            """
            CREATE TABLE IF NOT EXISTS neurons (
                block INTEGER NOT NULL,
                netuid INTEGER,
                uid INTEGER,
                coldkey TEXT,
                hotkey TEXT,
                active BOOL,

                consensus INTEGER,
                dividends INTEGER,
                emission INTEGER,
                incentive INTEGER,
                last_update INTEGER,
                pruning_score INTEGER,
                rank INTEGER,
                trust INTEGER,
                validator_permit BOOL,
                validator_trust INTEGER,

                PRIMARY KEY (block, netuid)
            );
            """
        )

        # "axon_info": {
                #     "block": 0,
                #     "version": 0,
                #     "ip": 0,
                #     "port": 0,
                #     "ip_type": 0,
                #     "protocol": 0,
                #     "placeholder1": 0,
                #     "placeholder2": 0,
                # },
                # "prometheus_info": {
                #     "block": 0,
                #     "version": 0,
                #     "ip": 0,
                #     "port": 0,
                #     "ip_type": 0,
                # },
                # "stake": [
                #     (
                #         "0x" + scalecodec.utils.ss58.ss58_decode(hotkey), # coldkey?
                #         0,
                #     )
                # ],
                # "weights": [],
                # "bonds": [],

        self._neurons = collections.defaultdict(list)

    async def get_neurons_lite(self, netuid):
        neurons = self.substrate.db.execute(
            "SELECT * FROM Neurons WHERE netuid = ?",
            (netuid,),
        )
        neurons = neurons.fetchall()

        return [
            {
                "active": neuron["active"],
                "coldkey": "0x" + scalecodec.utils.ss58.ss58_decode(neuron[3]),
                "hotkey": "0x" + scalecodec.utils.ss58.ss58_decode(neuron[4]),
                "uid": neuron["uid"],
                "netuid": neuron["netuid"],
                "stake": [
                    (
                        "0x" + scalecodec.utils.ss58.ss58_decode(neuron[3]), # coldkey?
                        0,
                    ),
                ],
                "axon_info": {
                    "ip": "192.168.0.2",
                    "port": 1983,
                    "protocol": 1,
                },
                "consensus": 0,
                "dividends": 0,
                "emission": 0,
                "incentive": 0,
                "last_update": 0,
                "prometheus_info": {
                    "ip": "192.168.0.2",
                    "port": 1000,    
                },
                "pruning_score": 0,
                "rank": 0,
                "trust": 0,
                "validator_permit": False,
                "validator_trust": 0,
            }
            for neuron in neurons
        ]
    