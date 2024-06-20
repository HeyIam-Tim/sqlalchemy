from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base, str_256
from enum import Enum
from datetime import datetime
from typing import Annotated


intpk = Annotated[int, mapped_column(primary_key=True)]
created = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)]


class WorkersOrm(Base):
    __tablename__ = 'workers'

    id: Mapped[intpk]
    username: Mapped[str_256]
    created: Mapped[created]
    updated: Mapped[updated]

    resumes: Mapped[list['Resume']] = relationship()


class WorkLoad(Enum):
    part_time = 'part_time'
    full_time = 'full_time'


class Resume(Base):
    __tablename__ = 'resume'

    worker_id: Mapped[int] = mapped_column(ForeignKey('workers.id', ondelete='CASCADE'))

    id: Mapped[intpk]
    title: Mapped[str_256]
    compensation: Mapped[int | None]
    workload: Mapped[WorkLoad]
    created: Mapped[created]
    updated: Mapped[updated]

    worker: Mapped['WorkersOrm'] = relationship( )


metadata_obj = MetaData()

workers_table = Table(
    'workers',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('username', String),
)
