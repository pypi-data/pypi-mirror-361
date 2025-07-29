from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pydantic import BaseModel
from sqlalchemy import Engine, Table
from autosubmit_api.database import tables
from autosubmit_api.database.common import create_autosubmit_db_engine


class ExperimentDetailsModel(BaseModel):
    exp_id: Any
    user: Any
    created: Any
    model: Any
    branch: Any
    hpc: Any


class ExperimentDetailsRepository(ABC):
    @abstractmethod
    def insert_many(self, values: List[Dict[str, Any]]) -> int:
        """
        Insert many rows into the details table.
        """

    @abstractmethod
    def delete_all(self) -> int:
        """
        Clear the details table.
        """

    @abstractmethod
    def get_by_exp_id(self, exp_id: int) -> ExperimentDetailsModel:
        """
        Get the experiment details by exp_id

        :param exp_id: The numerical experiment id
        :return experiment: The experiment details
        :raises ValueError: If the experiment detail is not found
        """

    @abstractmethod
    def upsert_details(
        self, exp_id: int, user: str, created: str, model: str, branch: str, hpc: str
    ) -> int:
        """
        Upsert the experiment details

        :param exp_id: The numerical experiment id
        :param user: The user who created the experiment
        :param created: The creation date of the experiment
        :param model: The model used in the experiment
        :param branch: The branch of the model
        :param hpc: The HPC used in the experiment
        :return: The number of rows affected
        """


class ExperimentDetailsSQLRepository(ExperimentDetailsRepository):
    def __init__(self, engine: Engine, table: Table):
        self.engine = engine
        self.table = table

    def insert_many(self, values: List[Dict[str, Any]]) -> int:
        with self.engine.connect() as conn:
            statement = self.table.insert()
            result = conn.execute(statement, values)
            conn.commit()
        return result.rowcount

    def delete_all(self) -> int:
        with self.engine.connect() as conn:
            statement = self.table.delete()
            result = conn.execute(statement)
            conn.commit()
        return result.rowcount

    def get_by_exp_id(self, exp_id: int):
        with self.engine.connect() as conn:
            statement = self.table.select().where(self.table.c.exp_id == exp_id)
            result = conn.execute(statement).first()
        if not result:
            raise ValueError(f"Experiment detail with exp_id {exp_id} not found")
        return ExperimentDetailsModel(
            exp_id=result.exp_id,
            user=result.user,
            created=result.created,
            model=result.model,
            branch=result.branch,
            hpc=result.hpc,
        )

    def upsert_details(self, exp_id, user, created, model, branch, hpc):
        with self.engine.connect() as conn:
            with conn.begin():
                try:
                    del_stmnt = self.table.delete().where(self.table.c.exp_id == exp_id)
                    ins_stmnt = self.table.insert().values(
                        exp_id=exp_id,
                        user=user,
                        created=created,
                        model=model,
                        branch=branch,
                        hpc=hpc,
                    )
                    conn.execute(del_stmnt)
                    result = conn.execute(ins_stmnt)
                    conn.commit()
                    return result.rowcount
                except Exception as exc:
                    conn.rollback()
                    raise exc


def create_experiment_details_repository() -> ExperimentDetailsRepository:
    engine = create_autosubmit_db_engine()
    return ExperimentDetailsSQLRepository(engine, tables.details_table)
