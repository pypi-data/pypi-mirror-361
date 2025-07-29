import os
from autosubmit_api.config.basicConfig import APIBasicConfig


class ExperimentPaths:
    """
    Helper class that builds related directories/files paths of an experiment
    """

    def __init__(self, expid: str) -> None:
        self._expid = expid

    @property
    def expid(self):
        return self._expid

    @property
    def exp_dir(self):
        return os.path.join(APIBasicConfig.LOCAL_ROOT_DIR, self.expid)

    @property
    def pkl_dir(self):
        return os.path.join(self.exp_dir, "pkl")

    @property
    def job_list_pkl(self):
        filename = f"job_list_{self.expid}.pkl"
        return os.path.join(self.pkl_dir, filename)

    @property
    def job_packages_db(self):
        filename = f"job_packages_{self.expid}.db"
        return os.path.join(self.pkl_dir, filename)

    @property
    def tmp_dir(self):
        """
        tmp dir
        """
        return os.path.join(self.exp_dir, APIBasicConfig.LOCAL_TMP_DIR)

    @property
    def tmp_log_dir(self):
        """
        tmp/LOG_{expid} dir
        """
        return os.path.join(self.tmp_dir, f"LOG_{self.expid}")

    @property
    def tmp_as_logs_dir(self):
        """
        tmp/ASLOGS dir
        """
        return os.path.join(self.tmp_dir, APIBasicConfig.LOCAL_ASLOG_DIR)

    @property
    def job_data_db(self):
        return os.path.join(APIBasicConfig.JOBDATA_DIR, f"job_data_{self.expid}.db")

    @property
    def structure_db(self):
        return os.path.join(APIBasicConfig.STRUCTURES_DIR, f"structure_{self.expid}.db")

    @property
    def user_metric_db(self):
        return os.path.join(self.tmp_dir, f"metrics_{self.expid}.db")

    @property
    def graph_data_db(self):
        return os.path.join(APIBasicConfig.GRAPHDATA_DIR, f"graph_data_{self.expid}.db")
