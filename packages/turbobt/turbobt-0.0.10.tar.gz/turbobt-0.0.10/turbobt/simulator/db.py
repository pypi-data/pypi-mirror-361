from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    pass


class Block(Base):
    __tablename__ = 'Blocks'

    number: Mapped[int] = mapped_column(primary_key=True)
    hash: Mapped[str] = mapped_column(nullable=False, unique=True)


class Extrinsic(Base):
    __tablename__ = 'Extrinsics'

    block: Mapped[int] = mapped_column(ForeignKey('Blocks.number'), primary_key=True)   # TODO
    call_function: Mapped[str]
    call_module: Mapped[str]
    call_args: Mapped[str] # TODO
    extrinsic_hash: Mapped[str]
