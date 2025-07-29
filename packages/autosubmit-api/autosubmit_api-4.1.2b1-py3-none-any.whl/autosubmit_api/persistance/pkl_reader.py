import os
from typing import List, Union, Dict
import pickle
from networkx import DiGraph
from autosubmit_api.config.basicConfig import APIBasicConfig
from autosubmit_api.database.models import PklJobModel
from autosubmit_api.persistance.experiment import ExperimentPaths


class PklReader:
    def __init__(self, expid: str) -> None:
        self.expid = expid
        APIBasicConfig.read()
        self.pkl_path = ExperimentPaths(expid).job_list_pkl

    def read_pkl(self) -> Union[List, DiGraph, Dict]:
        with open(self.pkl_path, "rb") as f:
            return pickle.load(f, encoding="latin1")

    def get_modified_time(self) -> int:
        return int(os.stat(self.pkl_path).st_mtime)

    def parse_job_list(self) -> List[PklJobModel]:
        job_list = []
        obj = self.read_pkl()

        if isinstance(obj, DiGraph):
            for node in obj.nodes(data=True):
                job_content = node[1]["job"]
                jobpkl = PklJobModel(
                    name=job_content.name,
                    id=job_content.id,
                    status=job_content.status,
                    priority=job_content.priority,
                    section=job_content.section,
                    date=job_content.date,
                    member=job_content.member,
                    chunk=job_content.chunk,
                    out_path_local=job_content.local_logs[0],
                    err_path_local=job_content.local_logs[1],
                    out_path_remote=job_content.remote_logs[0],
                    err_path_remote=job_content.remote_logs[1],
                    wrapper_type=job_content.wrapper_type,
                )
                job_list.append(jobpkl)
        elif isinstance(obj, list):
            for item in obj:
                jobpkl = PklJobModel(
                    name=item[0],
                    id=item[1],
                    status=item[2],
                    priority=item[3],
                    section=item[4],
                    date=item[5],
                    member=item[6],
                    chunk=item[7],
                    out_path_local=item[8],
                    err_path_local=item[9],
                    out_path_remote=item[10],
                    err_path_remote=item[11],
                    wrapper_type=(item[12] if len(item) > 12 else None),
                )
                job_list.append(jobpkl)
        elif isinstance(obj, dict):
            for job_name, value in obj.items():
                local_logs = value.get("_local_logs") if value.get("_local_logs") else []
                remote_logs = value.get("_remote_logs") if value.get("_remote_logs") else []
                jobpkl = PklJobModel(
                    name=job_name,
                    id=value.get("id"),
                    status=value.get("_status"),
                    priority=value.get("priority"),
                    section=value.get("_section"),
                    date=value.get("date"),
                    member=value.get("_member"),
                    chunk=value.get("_chunk"),
                    out_path_local=local_logs[0] if len(local_logs) > 0 else None,
                    err_path_local=local_logs[1] if len(local_logs) > 1 else None,
                    out_path_remote=remote_logs[0] if len(remote_logs) > 0 else None,
                    err_path_remote=remote_logs[1] if len(remote_logs) > 1 else None,
                    wrapper_type=value.get("wrapper_type"),
                )
                job_list.append(jobpkl)
        else:
            raise ValueError("Unknown type of object in the pkl file")

        return job_list
