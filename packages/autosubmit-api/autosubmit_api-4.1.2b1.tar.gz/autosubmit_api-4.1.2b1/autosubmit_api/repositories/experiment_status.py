from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List
from pydantic import BaseModel
from sqlalchemy import Engine, Table, delete, insert
from sqlalchemy.schema import CreateTable
from autosubmit_api.database import tables
from autosubmit_api.database.common import create_as_times_db_engine


class ExperimentStatusModel(BaseModel):
    exp_id: int
    name: str
    status: str
    seconds_diff: Any
    modified: Any


class ExperimentStatusRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[ExperimentStatusModel]:
        """
        Get all experiments status
        """

    @abstractmethod
    def get_by_expid(self, expid: str) -> ExperimentStatusModel:
        """
        Get experiment status by expid

        :param expid: Experiment name
        :return: Experiment status
        :raises ValueError: If the experiment status does not exist
        """

    @abstractmethod
    def upsert_status(self, exp_id: int, expid: str, status: str) -> int:
        """
        Delete and insert experiment status by expid
        """

    @abstractmethod
    def get_only_running_expids(self) -> List[str]:
        """
        Gets list of running experiments expids
        """

    @abstractmethod
    def delete_all(self) -> int:
        """
        Delete all experiment status
        """


class ExperimentStatusSQLRepository(ExperimentStatusRepository):
    def __init__(self, engine: Engine, table: Table):
        self.engine = engine
        self.table = table

        with self.engine.connect() as conn:
            conn.execute(CreateTable(self.table, if_not_exists=True))
            conn.commit()

    def get_all(self):
        with self.engine.connect() as conn:
            statement = self.table.select()
            result = conn.execute(statement).all()
        return [
            ExperimentStatusModel.model_validate(row, from_attributes=True)
            for row in result
        ]

    def get_by_expid(self, expid: str):
        with self.engine.connect() as conn:
            statement = self.table.select().where(self.table.c.name == expid)
            result = conn.execute(statement).first()
        if result is None:
            raise ValueError(f"Experiment status {expid} not found")
        return ExperimentStatusModel(
            exp_id=result.exp_id,
            name=result.name,
            status=result.status,
            seconds_diff=result.seconds_diff,
            modified=result.modified,
        )

    def upsert_status(self, exp_id: int, expid: str, status: str):
        with self.engine.connect() as conn:
            with conn.begin():
                try:
                    del_stmnt = delete(self.table).where(self.table.c.exp_id == exp_id)
                    ins_stmnt = insert(self.table).values(
                        exp_id=exp_id,
                        name=expid,
                        status=status,
                        seconds_diff=0,
                        modified=datetime.now().isoformat(sep="-", timespec="seconds"),
                    )
                    conn.execute(del_stmnt)
                    result = conn.execute(ins_stmnt)
                    conn.commit()
                    return result.rowcount
                except Exception as exc:
                    conn.rollback()
                    raise exc

    def get_only_running_expids(self):
        with self.engine.connect() as conn:
            statement = self.table.select().where(self.table.c.status == "RUNNING")
            result = conn.execute(statement).all()
        return [row.name for row in result]

    def delete_all(self):
        with self.engine.connect() as conn:
            statement = delete(self.table)
            result = conn.execute(statement)
            conn.commit()
        return result.rowcount


def create_experiment_status_repository() -> ExperimentStatusRepository:
    engine = create_as_times_db_engine()
    return ExperimentStatusSQLRepository(engine, tables.experiment_status_table)
