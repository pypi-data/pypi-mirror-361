import collections
import typing

import scalecodec.utils.ss58

from turbobt.subtensor.exceptions import HotKeyAlreadyRegisteredInSubNet, HotKeyNotRegisteredInNetwork


AccountId = typing.TypeAlias = str


class SubtensorModule:
    def __init__(self, substrate):
        self.substrate = substrate

        self.substrate.db.execute(
            """
            CREATE TABLE IF NOT EXISTS NeuronCertificates (
                block INTEGER NOT NULL,
                netuid INTEGER NOT NULL,
                hotkey TEXT NOT NULL,
                algorithm INTEGER,
                public_key BLOB,
                PRIMARY KEY (block, netuid, hotkey)
            );
            """
        )

        self.NeuronCertificates = collections.defaultdict(dict)
    
    async def burned_register(self, who, netuid: int, hotkey: AccountId):
        neuron = self.substrate.db.execute(
            "SELECT * FROM Neurons WHERE netuid = ? AND hotkey = ?",
            (netuid, hotkey),
        )
        neuron = neuron.fetchone()

        if neuron is not None:
            raise HotKeyAlreadyRegisteredInSubNet
        
        self.substrate.db.execute(
            "INSERT INTO Neurons VALUES (1, :netuid, :uid, :coldkey, :hotkey, :active, :consensus, :dividends, :emission, :incentive, :last_update, :pruning_score, :rank, :trust, :validator_permit, :validator_trust)",
            {
                "coldkey": who,
                "hotkey": hotkey,
                "uid": 0,
                "netuid": 12,
                "active": True,
                "axon_info": {
                    "block": 0,
                    "version": 0,
                    "ip": 0,
                    "port": 0,
                    "ip_type": 0,
                    "protocol": 0,
                    "placeholder1": 0,
                    "placeholder2": 0,
                },
                "prometheus_info": {
                    "block": 0,
                    "version": 0,
                    "ip": 0,
                    "port": 0,
                    "ip_type": 0,
                },
                "stake": [
                    (
                        "0x" + scalecodec.utils.ss58.ss58_decode(hotkey), # coldkey?
                        0,
                    )
                ],
                "rank": 0,
                "emission": 0,
                "incentive": 0,
                "consensus": 0,
                "trust": 0,
                "validator_trust": 0,
                "dividends": 0,
                "last_update": 0,
                "validator_permit": True,
                "weights": [],
                "bonds": [],
                "pruning_score": 65535,
            }
        )

    async def commit_crv3_weights(self, who, netuid: int, commit: bytes, reveal_round: int):
        # TODO who

        current_epoch = 0

        try:
            commits = self.substrate.state._CRV3WeightCommits[(netuid, current_epoch)]
        except KeyError:
            commits = self.substrate.state._CRV3WeightCommits[(netuid, current_epoch)] = []

        unrevealed_commits_for_who = [
            account
            for (account, _, _) in commits
            if account == who
        ]

        if len(unrevealed_commits_for_who) >= 10:
            raise RuntimeError("TooManyUnrevealedCommits")
        
        commits.append((
            who,
            commit,
            reveal_round,
        ))

        # https://github.com/opentensor/subtensor/blob/4c9836f8cc199bc323956509f59d86d1761dd021/pallets/subtensor/src/subnets/weights.rs#L229

    async def serve_axon(
        self,
        who,
        netuid: int,
        version: int,
        ip: int,
        port: int,
        ip_type: int,
        protocol: int,
        placeholder1: int,
        placeholder2: int,
    ):
        return
        try:
            neuron = self.substrate.NeuronInfoRuntimeApi._neurons[netuid][0]    # TODO
        except IndexError:
            raise HotKeyNotRegisteredInNetwork

        neuron["axon_info"] = {
            "block": 0,
            "version": version,
            "ip": ip,
            "port": port,
            "ip_type": ip_type,
            "protocol": protocol,
            "placeholder1": placeholder1,
            "placeholder2": placeholder2,
        }

    async def serve_axon_tls(
        self,
        who,
        netuid: int,
        version: int,
        ip: int,
        port: int,
        ip_type: int,
        protocol: int,
        placeholder1: int,
        placeholder2: int,
        certificate: bytes,
    ):
        await self.serve_axon(
            who,
            netuid,
            version,
            ip,
            port,
            ip_type,
            protocol,
            placeholder1,
            placeholder2,
        )
        self.substrate.db.execute(
            "INSERT INTO NeuronCertificates VALUES (?, ?, ?, ?, ?)",
            (1, netuid, who, ord(certificate[0]), certificate[1:]), # TODO block
        )
