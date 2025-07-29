import typing

import sqlalchemy
import sqlalchemy.orm

from turbobt.simulator import db

from ._base import Pallet


class Extrinsic(typing.TypedDict):
    extrinsic_hash: str
    extrinsic_length: int
    # call


class Header(typing.TypedDict):
    number: int
    # ...


class Block(typing.TypedDict):
    extrinsics: Extrinsic
    header: Header


class SignedBlock(typing.TypedDict):
    block: Block
    # justifications


class Chain(Pallet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with sqlalchemy.orm.Session(self.substrate.engine) as session:
            # TODO 0?
            block0 = db.Block(
                number=0,
                hash="0x" + bytes([69] * 32).hex(),
            )
            block = db.Block(
                number=1,
                hash="0x3fe8c77075d8194ed0bb7fd70d7b8cc91c12826c7f04df9f04c4235f0f6a966b",
            )

            session.add(block0)
            session.add(block)
            session.commit()

        self._extrinsics = []

    async def getBlock(self, hash: str | None = None) -> SignedBlock | None:
        extrinsics = [
            extrinsic.data.to_hex()
            for extrinsic in self._extrinsics
        ]

        self._extrinsics.clear()

        with self.substrate.session() as session:
            block = session.scalars(
                sqlalchemy.select(db.Block).where(db.Block.hash == hash),
            ).first()

        if block is None:
            return None

        return {
            "block": {
                "header": {
                    "parentHash": "0x3fe8c77075d8194ed0bb7fd70d7b8cc91c12826c7f04df9f04c4235f0f6a966b",
                    "number": hex(block.number),
                    "stateRoot": "0x7e08c53c205b2d7766884935e96dab4cdd11e7055024603b42023894bec3c33d",
                    "extrinsicsRoot": "0x937ca90d15a79bf046edeb94a02ccc65de71b7985e9bb215d5e31bd5fea3b962",
                    "digest": {
                        "logs": [
                            "0x066175726120694fd0a001000000",
                            "0x0466726f6e88010b5bab658f24b6f14179a5d50e59a7901785c97358ebcd910a8186ba6ba79f9800",
                            "0x05617572610101f6a1e1e554fd7a9bc6adaf7fdbab553771bdc8ce354c95c38ce03c76d130797de48a244d8dc06d1c9c84ba82b02ed0dcc1dd3e88fd4e10271003cb402c1bbc8f",
                        ]
                    },
                },
                "extrinsics": extrinsics,
            },
            "justifications": None,
        }

    async def getBlockHash(self, hash: int | None = None) -> str | None:
        return "0xf0aa135ddac82c7b5ea0de2b021945381bc6a449fdd44386d9956fa0a5ee1e05"

    async def getHeader(self, hash) -> Header | None:
        with self.substrate.session() as session:
            block = session.scalars(
                sqlalchemy.select(db.Block).order_by(db.Block.number.desc()).limit(1),
            ).first()
            prev = session.scalars(
                sqlalchemy.select(db.Block).where(db.Block.number == block.number - 1),
            ).first()
            # TODO hash

        return {
            "parentHash": prev.hash,
            "number": hex(block.number),
            "stateRoot": "0xfb9e07dd769d95a30ab04e1e801b1400df1261487cddab93dc64628ad95cec56",
            "extrinsicsRoot": "0xe5b4ae1cda6591fa8a8026bef64c5d712f7dc6c0dc700f74d1670139e55c220d",
            "digest": {
                "logs": [
                    # "0x066175726120c65dd0a001000000",
                    # "0x0466726f6e88016cf22a0277ba8ff8e59961a06a8d069319b70310036243621a257f53a12c1c2700",
                    # "0x0561757261010106b919906a40cc0db25fb60404f5323902641f4696b0a83b8f0b5d08a1ccb3303d2153015f0451901bcf50867bf182d991876176c8ccc9bf55aed1748085ac8d",
                ]
            },
        }
