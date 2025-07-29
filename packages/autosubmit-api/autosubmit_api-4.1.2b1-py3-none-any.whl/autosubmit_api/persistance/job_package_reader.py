from typing import Dict, List
from autosubmit_api.logger import logger
from autosubmit_api.repositories.job_packages import create_job_packages_repository


class JobPackageReader:

    def __init__(self, expid: str) -> None:
        self.expid = expid
        self._content: List[Dict] = []
        self._job_to_package: Dict[str, str] = {}
        self._package_to_jobs: Dict[str, List[str]] = {}
        self._package_to_package_id: Dict[str, str] = {}
        self._package_to_symbol: Dict[str, str] = {}

    def read(self):
        try:
            raw_content = create_job_packages_repository(self.expid).get_all()
            self._content = [x.model_dump() for x in raw_content]
            if len(self._content) == 0:
                raise Warning("job_packages table empty, trying wrapper_job_packages")
        except Exception as exc:
            logger.warning(exc)
            raw_content = create_job_packages_repository(
                self.expid, wrapper=True
            ).get_all()
            self._content = [x.model_dump() for x in raw_content]

        self._build_job_to_package()
        self._build_package_to_jobs()
        self._build_package_to_package_id()
        self._build_package_to_symbol()

        return self

    def _build_job_to_package(self):
        try:
            for row in self._content:
                package_name: str = row.get("package_name")
                job_name: str = row.get("job_name")

                if len(str(package_name).strip()) > 0:
                    self._job_to_package[job_name] = package_name
        except Exception:
            logger.warning("Error while building job_to_package")

        return self._job_to_package

    def _build_package_to_jobs(self):
        try:
            for job_name, package_name in self._job_to_package.items():
                self._package_to_jobs.setdefault(package_name, []).append(job_name)
        except Exception:
            logger.warning("Error while building package_to_jobs")

        return self._package_to_jobs

    def _build_package_to_package_id(self):
        try:
            for package_name in self._package_to_jobs:
                splitted_name = package_name.split("_")
                if len(splitted_name) >= 3:
                    self._package_to_package_id[package_name] = package_name.split("_")[
                        2
                    ]
        except Exception:
            logger.warning("Error while building package_to_package_id")

        return self._package_to_package_id

    def _build_package_to_symbol(self):
        try:
            list_packages = list(self._job_to_package.values())
            for i in range(len(list_packages)):
                if i % 2 == 0:
                    self._package_to_symbol[list_packages[i]] = "square"
                else:
                    self._package_to_symbol[list_packages[i]] = "hexagon"
        except Exception:
            logger.warning("Error while building package_to_symbol")

        return self._package_to_symbol

    @property
    def job_to_package(self):
        return self._job_to_package

    @property
    def package_to_jobs(self):
        return self._package_to_jobs

    @property
    def package_to_package_id(self):
        return self._package_to_package_id

    @property
    def package_to_symbol(self):
        return self._package_to_symbol
