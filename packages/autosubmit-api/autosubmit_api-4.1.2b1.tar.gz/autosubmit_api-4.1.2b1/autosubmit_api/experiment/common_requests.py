#!/usr/bin/env python

# Copyright 2015 Earth Sciences Department, BSC-CNS

# This file is part of Autosubmit.

# Autosubmit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Autosubmit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Autosubmit.  If not, see <http://www.gnu.org/licenses/>.

"""
Module containing functions to manage autosubmit's experiments.
"""
import datetime
import json
import locale
import os
import re
import subprocess
import time
import traceback
from collections import deque
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from autosubmitconfigparser.config.configcommon import (
    AutosubmitConfig as Autosubmit4Config,
)
from bscearth.utils.config_parser import ConfigParserFactory

from autosubmit_api.autosubmit_legacy.job.job_list import JobList
from autosubmit_api.builders.configuration_facade_builder import (
    AutosubmitConfigurationFacadeBuilder,
    ConfigurationFacadeDirector,
)
from autosubmit_api.builders.experiment_history_builder import (
    ExperimentHistoryBuilder,
    ExperimentHistoryDirector,
)
from autosubmit_api.builders.joblist_loader_builder import (
    JobListLoaderBuilder,
    JobListLoaderDirector,
)
from autosubmit_api.common import utils as common_utils
from autosubmit_api.components.experiment.file_metadata import FileMetadata
from autosubmit_api.components.experiment.pkl_organizer import PklOrganizer
from autosubmit_api.components.jobs import utils as JUtils
from autosubmit_api.components.jobs.job_factory import SimpleJob
from autosubmit_api.components.jobs.job_support import JobSupport
from autosubmit_api.components.representations.graph.graph import (
    GraphRepresentation,
    GroupedBy,
    Layout,
)
from autosubmit_api.components.representations.tree.tree import TreeRepresentation
from autosubmit_api.config.basicConfig import APIBasicConfig
from autosubmit_api.config.confConfigStrategy import confConfigStrategy
from autosubmit_api.config.config_common import AutosubmitConfigResolver
from autosubmit_api.database import db_common as db_common
from autosubmit_api.database import db_jobdata as JobData
from autosubmit_api.experiment import common_db_requests as DbRequests
from autosubmit_api.experiment.utils import get_files_from_dir_with_pattern, read_tail
from autosubmit_api.logger import logger
from autosubmit_api.monitor.monitor import Monitor
from autosubmit_api.performance.utils import calculate_SYPD_perjob
from autosubmit_api.persistance.experiment import ExperimentPaths
from autosubmit_api.persistance.job_package_reader import JobPackageReader
from autosubmit_api.persistance.pkl_reader import PklReader
from autosubmit_api.repositories.experiment import create_experiment_repository
from autosubmit_api.statistics.statistics import Statistics

APIBasicConfig.read()

SAFE_TIME_LIMIT = 300
SAFE_TIME_LIMIT_STATUS = 180


def get_experiment_stats(expid: str, filter_period: int, filter_type: str) -> Dict[str, Any]:
    """
    Lite version of the stats generator from Autosubmit autosubmit.py
    """
    error = False
    error_message = ""
    period_fi = ""
    period_ini = ""
    considered_jobs = list()
    result = None
    summary = None
    try:
        if filter_period:
            filter_period = int(filter_period)

        job_list_loader = JobListLoaderDirector(JobListLoaderBuilder(expid)).build_loaded_joblist_loader()
        considered_jobs = job_list_loader.jobs
        if filter_type and filter_type != 'Any':
            considered_jobs = [job for job in job_list_loader.jobs if job.section == filter_type]

        period_fi = datetime.datetime.now(tz=common_utils.LOCAL_TZ).replace(
            second=0, microsecond=0
        )
        if filter_period and filter_period > 0:
            period_ini = period_fi - datetime.timedelta(hours=filter_period)
            filtered_jobs = []
            for job in considered_jobs:
                job_support = JobSupport(expid, job, APIBasicConfig)
                if job_support.check_started_after(period_ini) or job_support.check_running_after(period_ini):
                    filtered_jobs.append(job)
            considered_jobs = filtered_jobs
        else:
            period_ini = None

        if len(considered_jobs) > 0:
            statistics = Statistics(expid=expid, jobs=considered_jobs, start=period_ini, end=period_fi, queue_time_fix={}, basic_config=APIBasicConfig)
            result = statistics.get_statistics()
            statistics.calculate_summary()
            summary = statistics.get_summary_as_dict()
        else:
            raise Exception("Autosubmit API couldn't find jobs that match your search critearia (Section: {0}) in the period from {1} to {2}.".format(filter_type, period_ini, period_fi))

    except Exception as e:
        print((traceback.format_exc()))
        error_message = str(e)
        error = True

    return {
        'error': error,
        'error_message': error_message,
        'Statistics': result,
        'summary': summary,
    }


def get_experiment_data(expid: str) -> Dict[str, Any]:
    """
    Get data of the experiment. Depends on the databases and config files.
    """
    result = {
        "expid": expid,
        "path": "NA",
        "owner_id": 0,
        "owner": "NA",
        "time_last_access": "",
        "time_last_mod": "",
        "error_message": "",
        "description": "",
        "version": "",
        "model": "",
        "branch": "",
        "hpc": "",
        "updateTime": 0,
        "error": False,
        "running": False,
        "pkl_timestamp": int(time.time()),
        "chunk_size": 0,
        "chunk_unit": "default",
        "total_jobs": 0,
        "completed_jobs": 0,
        "db_historic_version": "NA",
    }

    # Get data from file metadata
    try:
        exp_paths = ExperimentPaths(expid)
        file_metadata = FileMetadata(exp_paths.exp_dir)

        result["path"] = exp_paths.exp_dir
        result["owner_id"] = file_metadata.owner_id
        result["owner"] = file_metadata.owner_name
        result["time_last_access"] = file_metadata.access_time
        result["time_last_mod"] = file_metadata.modified_time
    except Exception as exc:
        result["error"] = True
        result["error_message"] += f"{str(exc)}\n"
        logger.error((traceback.format_exc()))

    # Get info from as conf facade
    try:
        autosubmit_config_facade = ConfigurationFacadeDirector(
            AutosubmitConfigurationFacadeBuilder(expid)
        ).build_autosubmit_configuration_facade()

        # Get from parsing config files
        result["hpc"] = autosubmit_config_facade.get_main_platform()
        result["branch"] = autosubmit_config_facade.get_branch()
        result["model"] = autosubmit_config_facade.get_model()
        result["chunk_size"] = autosubmit_config_facade.chunk_size
        result["chunk_unit"] = autosubmit_config_facade.chunk_unit
        result["version"] = autosubmit_config_facade.get_autosubmit_version()
        result["updateTime"] = autosubmit_config_facade.get_safety_sleep_time()
        result["pkl_timestamp"] = (
            autosubmit_config_facade.get_pkl_last_modified_timestamp()
        )
        result["workflow_commit"] = autosubmit_config_facade.get_workflow_commit()
    except Exception as exc:
        result["error"] = True
        result["error_message"] += f"{str(exc)}\n"
        logger.error((traceback.format_exc()))

    # Get from experiment table
    try:
        experiment = create_experiment_repository().get_by_expid(expid)
        result["description"] = experiment.description
        # Overwrite version from conf
        result["version"] = experiment.autosubmit_version
    except Exception as exc:
        result["error"] = True
        result["error_message"] += f"{str(exc)}\n"
        logger.warning((traceback.format_exc()))
        logger.warning(
            (
                f"Warning: Error in get_experiment_data while retrieving experiment from DB by id: {exc}"
            )
        )

    # Get status
    try:
        _, experiment_status = DbRequests.get_specific_experiment_status(expid)
        result["running"] = experiment_status == "RUNNING"
    except Exception as exc:
        logger.warning((traceback.format_exc()))
        logger.warning(
            (
                f"Warning: Error in get_experiment_data while quickly get experiment status: {exc}."
                "Trying to get the status exhaustively. "
            )
        )
        try:
            _, _, is_running, _, _ = _is_exp_running(expid)
            result["running"] = is_running
        except Exception as exc:
            result["error"] = True
            result["error_message"] += f"{str(exc)}\n"
            logger.warning((traceback.format_exc()))
            logger.warning(
                (
                    f"Warning: Error in get_experiment_data while retrieving the status exhaustively: {exc}. "
                )
            )

    # Get historic data
    try:
        experiment_history = ExperimentHistoryDirector(
            ExperimentHistoryBuilder(expid)
        ).build_reader_experiment_history()
        experiment_run = experiment_history.manager.get_experiment_run_dc_with_max_id()
        if experiment_run and experiment_run.total > 0:
            result["total_jobs"] = experiment_run.total
            result["completed_jobs"] = experiment_run.completed
    except Exception as exc:
        logger.warning((traceback.format_exc()))
        logger.warning(
            (
                f"Warning: Error in get_experiment_data while reading historical data: {exc}"
            )
        )

    return result


def get_current_status_log_plus(expid):
    """
    Get the current status, name of current log, last time modified, and last 5 lines of the latest log of the experiment.
    Presents _is_exp_running as a JSON object.
    """
    error, error_message, is_running, timediff, log_path = _is_exp_running(
        expid)
    return {"error": error,
            "error_message": error_message,
            "is_running": is_running,
            "timediff": timediff,
            "log_path": log_path}


def _is_exp_running(expid: str, time_condition=300) -> Tuple[bool, str, bool, int, str]:
    """
    Tests if experiment is running
    :param expid: Experiment name
    :param time_condition: Time constraint, 120 by default. Represents max seconds before an experiment is considered as NOT RUNNING
    :return: (error (true if error is found, false otherwise), error_message, is_running (true if running, false otherwise), timediff, path_to_log)
    """
    is_running = False
    error = False
    error_message = ""
    timediff = 0
    definite_log_path = None
    try:
        APIBasicConfig.read()
        exp_paths = ExperimentPaths(expid)
        pathlog_aslog = exp_paths.tmp_as_logs_dir
        pathlog_tmp = exp_paths.tmp_dir
        # Basic Configuration
        look_old_folder = False
        current_version = None
        try:
            as_conf = AutosubmitConfigResolver(
                expid, APIBasicConfig, ConfigParserFactory())
            as_conf.reload()
            current_version = as_conf.get_version()
        except Exception as exc:
            logger.warning("Error in getting current_version: " + str(exc))
        look_old_folder = True if current_version is not None and (str(current_version).startswith(
            "3.11") or str(current_version).startswith("3.9") or str(current_version).startswith("3.12")) else False

        pathlog_first = pathlog_aslog if look_old_folder is False else pathlog_tmp
        pathlog_second = pathlog_aslog if look_old_folder is True else pathlog_tmp
        # print("Experiment {0} version {1} \nLook {2} \nLook {3}".format(
        #     expid, current_version, pathlog_first, pathlog_second))
        # print(pathlog)
        dir_files = []
        if os.path.exists(pathlog_first):
            dir_files = get_files_from_dir_with_pattern(pathlog_first, "_run.log")

        #print("Length {0}".format(len(reading)))
        if dir_files:
            log_file_name = dir_files[0]
            definite_log_path = pathlog_first + '/' + log_file_name
            current_stat = os.stat(definite_log_path)
            timest = current_stat.st_mtime
            # system_stat = os.stat(BasicConfig.LOCAL_ROOT_DIR)
            timesys = time.time()
            timediff = int(timesys - timest)
            # print(timediff)
            if (timediff < time_condition):
                is_running = True
            else:
                is_running = False
            return (error, error_message, is_running, timediff, definite_log_path)

        # print(pathlog)
        dir_files = []
        if os.path.exists(pathlog_second):
            dir_files = get_files_from_dir_with_pattern(pathlog_second, "_run.log")

        #print("Second reading {0}".format(reading))
        if dir_files:
            log_file_name = dir_files[0]
            definite_log_path = pathlog_second + '/' + log_file_name
            current_stat = os.stat(definite_log_path)
            timest = current_stat.st_mtime
            # system_stat = os.stat(BasicConfig.LOCAL_ROOT_DIR),
            timesys = time.time()
            timediff = int(timesys - timest)
            if (timediff < time_condition):
                is_running = True
            else:
                is_running = False
            return (error, error_message, is_running, timediff, definite_log_path)
        # If nothing is found
        return (error, error_message, is_running, timediff, definite_log_path)

    except Exception as ex:
        error = True
        is_running = False
        timediff = time_condition
        error_message = str(ex)
        # print(traceback.format_exc())
        # print("Error in test: " + error_message)
        return (error, error_message, is_running, timediff, definite_log_path)


def get_experiment_summary(expid: str, log):
    """
    Gets job summary for the experiment. Consider seconds.
    :param expid: Name of experiment
    :rtype expid: str
    :return: Object
    """
    APIBasicConfig.read()

    running = suspended = queuing = failed = submitted = total_q_time = total_r_time = 0
    q_count = r_count = 0
    # avg_q_time = avg_r_time = sim_avg_q_time = sim_avg_r_time =
    avg_q_time = avg_r_time = sim_avg_q_time = sim_avg_r_time = 0
    str_avg_q_time = str_avg_r_time = str_sim_avg_q_time = str_sim_avg_r_time = "NA"
    sim_q_count = sim_r_count = sim_total_q_time = sim_total_r_time = sim_count = 0
    # type_avg_q_time = type_avg_r_time = type_sim_avg_q_time = type_sim_avg_r_time = "min"
    failed_list = list()
    error = False
    error_message = ""
    try:
        # Basic paths
        APIBasicConfig.read()
        tmp_path = os.path.join(
            APIBasicConfig.LOCAL_ROOT_DIR, expid, APIBasicConfig.LOCAL_TMP_DIR)
        # Try to get packages
        job_package_reader = JobPackageReader(expid)
        try:
            job_package_reader.read()
        except Exception as exc:
            logger.warning(f"Failed to read job_packages: {exc}")
        # Basic data
        job_running_to_seconds = dict()
        job_running_to_runtext = dict()
        jobs_in_pkl = dict()
        fakeAllJobs = list()

        # Read PKL
        pkl_organizer = PklOrganizer(expid)
        for job_item in pkl_organizer.current_content:
            status_code = job_item.status
            job_name = job_item.name
            priority = job_item.priority
            id_number = job_item.id
            out = job_item.out_path_local
            err = job_item.err_path_local
            status_color = Monitor.color_status(status_code)
            status_text = str(common_utils.Status.VALUE_TO_KEY[status_code])
            jobs_in_pkl[job_name] = (
                status_code, status_color, status_text, out, err, priority, id_number)
            fakeAllJobs.append(
                SimpleJob(job_name, tmp_path, status_code))

        job_running_to_seconds, job_running_to_runtext, _ = (
            JobList.get_job_times_collection(
                APIBasicConfig,
                fakeAllJobs,
                expid,
                job_package_reader.job_to_package,
                job_package_reader.package_to_jobs,
                timeseconds=True,
            )
        )

        # Main Loop
        if len(list(job_running_to_seconds.keys())) > 0:
            for job_name in list(jobs_in_pkl.keys()):
                # print(value)
                job_info = job_running_to_seconds[job_name] if job_name in list(job_running_to_seconds.keys(
                )) else None
                queue_seconds = job_info.queue_time if job_info else 0
                running_seconds = job_info.run_time if job_info else 0
                status = job_info.status if job_info else "UNKNOWN"
                # Identifying SIM
                name_components = job_name.split('_')
                if "SIM" in name_components:
                    # print(name_components)
                    sim_count += 1
                    if status in ["QUEUING"]:
                        sim_q_count += 1
                        sim_total_q_time += queue_seconds
                        # print(sim_total_q_time)
                    elif status in ["COMPLETED", "RUNNING", "FAILED"]:
                        sim_q_count += 1
                        sim_r_count += 1
                        sim_total_q_time += queue_seconds
                        sim_total_r_time += running_seconds

                # print(str(key) + " ~ " + str(status))
                if status == "FAILED":
                    failed += 1
                    q_count += 1
                    r_count += 1
                    total_q_time += queue_seconds
                    total_r_time += running_seconds
                    failed_list.append(job_name)
                elif status == "SUBMITTED":
                    submitted += 1
                    q_count += 1
                    total_q_time += queue_seconds
                elif status == "QUEUING":
                    queuing += 1
                    q_count += 1
                    total_q_time += queue_seconds
                elif status == "SUSPENDED":
                    suspended += 1
                elif status == "RUNNING":
                    running += 1
                    q_count += 1
                    r_count += 1
                    total_q_time += queue_seconds
                    total_r_time += running_seconds
                elif status == "COMPLETED":
                    q_count += 1
                    r_count += 1
                    total_q_time += queue_seconds
                    total_r_time += running_seconds
        # All jobs: Average queuing time
        avg_q_time = int(total_q_time / q_count) if q_count > 0 else 0
        str_avg_q_time = str(datetime.timedelta(seconds=avg_q_time))

        # All jobs: Average running time
        avg_r_time = int(total_r_time / r_count) if r_count > 0 else 0
        str_avg_r_time = str(datetime.timedelta(seconds=avg_r_time))

        # Sim jobs: Average queuing time
        sim_avg_q_time = int(sim_total_q_time /
                             sim_q_count) if sim_q_count > 0 else 0
        str_sim_avg_q_time = str(datetime.timedelta(seconds=sim_avg_q_time))

        # Sim jobs: Average running time
        sim_avg_r_time = int(sim_total_r_time /
                             sim_r_count) if sim_r_count > 0 else 0
        str_sim_avg_r_time = str(datetime.timedelta(seconds=sim_avg_r_time))
    except Exception as exp:
        error = True
        error_message = str(exp)

    return {
        'n_running': running,
        'n_suspended': suspended,
        'n_queuing': queuing,
        'n_failed': failed,
        'n_submitted': submitted,
        'avg_queue_time': str_avg_q_time,
        'avg_run_time': str_avg_r_time,
        'n_sim': sim_count,
        'avg_sim_queue_time': str_sim_avg_q_time,
        'avg_sim_run_time': str_sim_avg_r_time,
        'sim_queue_considered': sim_q_count,
        'sim_run_considered': sim_r_count,
        'failed_jobs': failed_list,
        'error': error,
        'error_message': error_message
    }


def quick_test_run(expid):
    """
    Quick test run that queries the database
    :param expid: Experiment name
    :type expid: str
    :return: running status
    :rtype: JSON object
    """
    running = True
    error = False
    error_message = ""

    try:
        name, status = DbRequests.get_specific_experiment_status(expid)
        if status != "RUNNING":
            running = False
    except Exception as exp:
        error = True
        error_message = str(exp)
        print((traceback.format_exc()))

    return {
        'running': running,
        'error': error,
        'error_message': error_message
    }


def get_experiment_log_last_lines(expid):
    """
    Gets last 150 lines of the log content
    """
    # Initializing results:
    log_file_name = ""
    found = False
    log_file_lastmodified = ""
    timest = ""
    error = False
    error_message = ""
    logcontent = []

    try:
        APIBasicConfig.read()
        exp_paths = ExperimentPaths(expid)

        dir_files = []
        path = None

        # Try to read from the tmp_as_logs folder
        if os.path.exists(exp_paths.tmp_as_logs_dir):
            dir_files = get_files_from_dir_with_pattern(exp_paths.tmp_as_logs_dir, 'run.log')
            path = exp_paths.tmp_as_logs_dir

        # Try to read from the tmp folder
        if len(dir_files) == 0 and os.path.exists(exp_paths.tmp_dir):
            dir_files = get_files_from_dir_with_pattern(exp_paths.tmp_dir, 'run.log')
            path = exp_paths.tmp_dir

        if len(dir_files) > 0:
            log_file_name = dir_files[0]
            log_file_path = str(os.path.join(path, log_file_name))
            current_stat = os.stat(log_file_path)
            timest = int(current_stat.st_mtime)
            log_file_lastmodified = common_utils.timestamp_to_datetime_format(timest)
            found = True

            logcontent = read_tail(log_file_path, 150)
    except Exception as e:
        error = True
        error_message = str(e)

    return {
        'logfile': log_file_name,
        'found': found,
        'lastModified': log_file_lastmodified,
        'timeStamp': timest,
        'error': error,
        'error_message': error_message,
        'logcontent': logcontent}


def get_experiment_recovery_log_last_lines(expid: str) -> Dict[str, Any]:
    """
    Gets last lines of the last recovery log for each platform.
    """
    platform_files = {}
    error = False
    error_message = ""

    try:
        APIBasicConfig.read()
        exp_paths = ExperimentPaths(expid)

        # List all the files under the tmp_as_logs_dir directory
        files = [
            str(f.name)
            for f in Path(exp_paths.tmp_as_logs_dir).iterdir()
            if f.is_file()
        ]

        pattern = r"^(\d{8})_(\d{6})_(.*?)_log_recovery\.log$"

        for file in files:
            # Extract the date and time from the filename
            match = re.search(pattern, file)
            if match:
                # Get the date and time components
                date_str = match.group(1)
                time_str = match.group(2)
                platform = match.group(3)

                # Convert to datetime object
                dt = datetime.datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")

                # Check if the platform is already in the dictionary
                if platform not in platform_files:
                    platform_files[platform] = {"datetime": dt, "filename": file}
                else:
                    # Compare the datetime objects and keep the one with the latest date
                    if dt > platform_files[platform]["datetime"]:
                        platform_files[platform] = {"datetime": dt, "filename": file}

        # Get the last lines of each platform's log file
        for platform_name, log_data in platform_files.items():
            full_path = str(
                Path(exp_paths.tmp_as_logs_dir).joinpath(log_data["filename"])
            )
            log_data["platform"] = platform_name
            log_data["modified_date"] = common_utils.timestamp_to_datetime_format(
                int(os.stat(full_path).st_mtime)
            )
            log_data["content"] = read_tail(full_path, 150)

    except Exception as exc:
        error = True
        error_message = str(exc)
        logger.error(traceback.format_exc())
        logger.error(exc)

    return {
        "platform_recovery_logs": list(platform_files.values()),
        "error": error,
        "error_message": error_message,
    }


def get_job_log(expid, logfile, nlines=150):
    """
    Returns the last 150 lines of the log file. Targets out or err.
    :param logfilepath: path to the log file
    :type logfilepath: str
    :return: List of string
    :rtype: list
    """
    # Initializing results:
    found = False
    log_file_lastmodified = ""
    timest = ""
    error = False
    error_message = ""
    logcontent = []
    APIBasicConfig.read()
    exp_paths = ExperimentPaths(expid)
    logfilepath = os.path.join(exp_paths.tmp_log_dir, logfile)
    try:
        if os.path.exists(logfilepath):
            current_stat = os.stat(logfilepath)
            timest = int(current_stat.st_mtime)
            log_file_lastmodified = common_utils.timestamp_to_datetime_format(timest)
            found = True

            logcontent = read_tail(logfilepath, nlines)
    except Exception as e:
        error = True
        error_message = str(e)

    return {
        'logfile': logfilepath,
        'found': found,
        'lastModified': log_file_lastmodified,
        'timeStamp': timest,
        'error': error,
        'error_message': error_message,
        'logcontent': logcontent}


def _retrieve_pkl_data(expid: str, out_format: str = "tree"):
    """
    Retrieves pkl data for the experiment.
    """
    pkl_file_path = ""
    error = False
    error_message = ""
    pkl_content = list()
    package_to_jobs = dict()
    pkl_timestamp = 0

    try:
        pkl_reader = PklReader(expid)
        pkl_file_path = pkl_reader.pkl_path
        pkl_timestamp = pkl_reader.get_modified_time()

        if not os.path.exists(pkl_file_path):
            raise Exception("Pkl file {} not found.".format(pkl_file_path))

        # Get last run data for each job
        try:
            experiment_history = ExperimentHistoryDirector(
                ExperimentHistoryBuilder(expid)
            ).build_reader_experiment_history()
            last_jobs_run = experiment_history.get_all_jobs_last_run_dict()
        except Exception:
            last_jobs_run = {}

        job_list_loader = JobListLoaderDirector(
            JobListLoaderBuilder(expid)
        ).build_loaded_joblist_loader()
        package_to_jobs = job_list_loader.joblist_helper.package_to_jobs

        for job in job_list_loader.jobs:
            # Calculate SYPD
            SYPD = None
            last_run = last_jobs_run.get(job.name)
            if last_run and last_run.chunk_unit and last_run.chunk_size:
                SYPD = calculate_SYPD_perjob(
                    last_run.chunk_unit,
                    last_run.chunk_size,
                    job.chunk,
                    job.run_time,
                    job.status,
                )

            formatted_job_data = {
                "name": job.name,
                "rm_id": job.rm_id,
                "status_code": job.status,
                "SYPD": SYPD,
                "minutes": job.run_time,
                "minutes_queue": job.queue_time,
                "submit": common_utils.timestamp_to_datetime_format(job.submit),
                "start": common_utils.timestamp_to_datetime_format(job.start),
                "finish": common_utils.timestamp_to_datetime_format(job.finish),
                "running_text": job.running_time_text,
                "status": job.status_text,
                "status_color": job.status_color,
                "out": job.out_file_path,
                "err": job.err_file_path,
                "priority": job.priority,
                "workflow_commit": job.workflow_commit,
            }

            if out_format == "tree":
                formatted_job_data.update(
                    {
                        "wrapper": job.package,
                        "wrapper_tag": job.package_tag,
                        "wrapper_id": job.package_code,
                        "title": job.tree_title,
                    }
                )
            elif out_format == "graph":
                formatted_job_data.update(
                    {
                        "dashed": True if job.package else False,
                        "shape": job_list_loader.joblist_helper.package_to_symbol.get(
                            job.package, "dot"
                        ),
                        "package": job.package,
                    }
                )

            pkl_content.append(formatted_job_data)

    except Exception as exc:
        error = True
        error_message = str(exc)

    result = {
        "pkl_file_name": pkl_file_path,
        "error": error,
        "error_message": error_message,
        "has_changed": True,
        "pkl_content": pkl_content,
        "pkl_timestamp": pkl_timestamp,
        "packages": package_to_jobs,
    }

    if out_format == "tree":
        result.update(
            {
                "source_tag": JUtils.source_tag,
                "target_tag": JUtils.target_tag,
                "sync_tag": JUtils.sync_tag,
                "check_mark": JUtils.checkmark_tag,
            }
        )

    return result


def get_experiment_pkl(expid: str) -> Dict[str, Any]:
    """
    Gets the current state of the pkl in a format proper for graph update.
    """
    return _retrieve_pkl_data(expid, out_format="graph")


def get_experiment_tree_pkl(expid: str) -> Dict[str, Any]:
    """
    Gets the current state of the pkl in a format for tree update
    """
    return _retrieve_pkl_data(expid, out_format="tree")


def get_experiment_graph(expid, log, layout=Layout.STANDARD, grouped=GroupedBy.NO_GROUP):
    """
    Gets graph representation
    """
    try:
        APIBasicConfig.read()
        autosubmit_configuration_facade = AutosubmitConfigResolver(
            expid, APIBasicConfig, ConfigParserFactory())
        autosubmit_configuration_facade.reload()

        if common_utils.is_version_historical_ready(autosubmit_configuration_facade.get_version()):
            job_list_loader = JobListLoaderDirector(JobListLoaderBuilder(expid)).build_loaded_joblist_loader()
            graph = GraphRepresentation(expid, job_list_loader, layout, grouped)
            graph.perform_calculations()
            return graph.get_graph_representation_data()
        else:
            raise ValueError('Autosubmit version is not supported')

    except Exception as e:
        print((traceback.format_exc()))
        print(("New Graph Representation failed: {0}".format(e)))
        log.info("Could not generate Graph and recieved the following exception: " + str(e))
        return {'nodes': [],
                'edges': [],
                'fake_edges': [],
                'groups': [],
                'groups_data': {},
                'error': True,
                'error_message': str(e),
                'graphviz': False,
                'max_children': 0,
                'max_parents': 0,
                'total_jobs': 0,
                'pkl_timestamp': 0}


def get_experiment_tree_rundetail(expid, run_id):
    """
    """
    base_list = dict()
    pkl_timestamp = 10000000
    try:
        print(("Received Tree RunDetail " + str(expid)))
        APIBasicConfig.read()
        tree_structure, current_collection, reference = JobList.get_tree_structured_from_previous_run(expid, APIBasicConfig, run_id=run_id)
        base_list['tree'] = tree_structure
        base_list['jobs'] = current_collection
        base_list['total'] = len(current_collection)
        base_list['reference'] = reference
    except Exception as e:
        print((traceback.format_exc()))
        return {'tree': [], 'jobs': [], 'total': 0, 'reference': [], 'error': True, 'error_message': str(e), 'pkl_timestamp': 0}
    base_list['error'] = False
    base_list['error_message'] = ''
    base_list['pkl_timestamp'] = pkl_timestamp
    return base_list


def get_experiment_tree_structured(expid, log):
    """
    Current version of the tree visualization algorithm.
    :param expid: Name of experiment
    :type expid: String
    :return: Dictionary [Variable Name] to Value
    :rtype: Dictionary Key: String, Value: Object
    """

    try:
        APIBasicConfig.read()

        experiment_repo = create_experiment_repository()
        curr_exp_as_version = experiment_repo.get_by_expid(expid).autosubmit_version

        main, secondary = common_utils.parse_version_number(curr_exp_as_version)
        if main and main >= 4:
            as_conf = Autosubmit4Config(expid)
            as_conf.reload(True)
        else:
            as_conf = AutosubmitConfigResolver(expid, APIBasicConfig, ConfigParserFactory())
            as_conf.reload()

        if common_utils.is_version_historical_ready(as_conf.get_version()):
            job_list_loader = JobListLoaderDirector(JobListLoaderBuilder(expid)).build_loaded_joblist_loader(None)
            tree = TreeRepresentation(expid, job_list_loader)
            tree.perform_calculations()
            return tree.get_tree_structure()
        else:
            raise ValueError('Autosubmit version is not supported')
        
    except Exception as e:
        print((traceback.format_exc()))
        print(("New Tree Representation failed: {0}".format(e)))
        log.info("New Tree Representation failed: {0}".format(e))
        return {'tree': [], 'jobs': [], 'total': 0, 'reference': [], 'error': True, 'error_message': str(e), 'pkl_timestamp': 0}


def get_experiment_counters(expid: str):
    """
    Returns status counters of the experiment.
    """
    error = False
    error_message = ""
    total = 0
    experiment_counters = dict()
    APIBasicConfig.read()
    # Default counter per status
    experiment_counters = {name: 0 for name in common_utils.Status.STRING_TO_CODE}
    try:
        pkl_organizer = PklOrganizer(expid)
        for job_item in pkl_organizer.current_content:
            status_code = int(job_item.status)
            total += 1
            experiment_counters[common_utils.Status.VALUE_TO_KEY.get(status_code, "UNKNOWN")] = experiment_counters.get(
                common_utils.Status.VALUE_TO_KEY.get(status_code, "UNKNOWN"), 0) + 1
            
    except Exception as exc:
        error = True
        error_message = str(exc)
        logger.error(traceback.format_exc())
        logger.error(exc)
    return {"error": error, "error_message": error_message, "expid": expid, "total": total, "counters": experiment_counters}


# TODO: Update to current representation standards and classes
def get_quick_view(expid: str):
    """ Lighter View """
    error = False
    error_message = ""
    #quick_view = list()
    view_data = []
    quick_tree_view = deque()
    jobs_in_pkl = {}
    total_count = completed_count = failed_count = running_count = queuing_count = 0
    try:
        APIBasicConfig.read()
        exp_paths = ExperimentPaths(expid)
        path_to_logs = exp_paths.tmp_log_dir

        # Retrieving packages
        now_ = time.time()
        job_to_package = {}
        package_to_package_id = {}

        job_package_reader = JobPackageReader(expid)
        try:
            job_package_reader.read()
            job_to_package = job_package_reader.job_to_package
            package_to_package_id = job_package_reader.package_to_package_id
        except Exception as exc:
            logger.warning(f"Failed to read job_packages: {exc}")
        
        logger.debug(("Retrieving packages {0} seconds.".format(
            str(time.time() - now_))))
        
        # Reading PKL
        try:
            pkl_organizer = PklOrganizer(expid)
            for job_item in pkl_organizer.current_content:
                status_code = int(job_item.status)
                # counters
                if status_code == common_utils.Status.COMPLETED:
                    completed_count += 1
                elif status_code == common_utils.Status.FAILED:
                    failed_count += 1
                elif status_code == common_utils.Status.RUNNING:
                    running_count += 1
                elif status_code == common_utils.Status.QUEUING:
                    queuing_count += 1
                # end
                job_name = job_item.name
                priority = job_item.priority
                id_number = job_item.id
                out = job_item.out_path_local
                err = job_item.err_path_local
                status_color = Monitor.color_status(status_code)
                status_text = str(common_utils.Status.VALUE_TO_KEY[status_code])
                jobs_in_pkl[job_name] = (
                    status_code, status_color, status_text, out, err, priority, id_number)
        except Exception as exc:
            raise Exception(
                f"Autosubmit API couldn't open pkl file. If you are sure that your experiment is running correctly, try again: {exc}")

        total_count = len(list(jobs_in_pkl.keys()))

        if len(list(jobs_in_pkl.keys())) > 0:
            for job_name in list(jobs_in_pkl.keys()):
                status_code, status_color, status_text, out, err, priority, id_number = jobs_in_pkl[
                    job_name]
                wrapper_tag = ""
                wrapper_id = 0
                # wrapper_name = ""
                if job_name in list(job_to_package.keys()):
                    # wrapper_name = job_to_package[job_name]
                    wrapper_id = package_to_package_id[job_to_package[job_name]]
                    wrapper_tag = " <span class='badge' style='background-color:#94b8b8'>Wrapped " + \
                        wrapper_id + "</span>"

                view_data.append({'name': job_name,
                                    'path_log': path_to_logs,
                                    'out': "/" + out,
                                    'err': "/" + err,
                                    })
                tree_job = {'title': JUtils.generate_job_html_title(job_name, status_color, status_text) + wrapper_tag,
                            'refKey': job_name,
                            'data': 'Empty',
                            'children': [],
                            'status': status_text,
                            }
                if status_code in [common_utils.Status.COMPLETED, common_utils.Status.WAITING, common_utils.Status.READY]:
                    quick_tree_view.append(tree_job)
                else:
                    quick_tree_view.appendleft(tree_job)
            # return {}
            # quick_tree_view = list(quick_tree_view)
                    
    except Exception as exc:
        error_message = "Exception: {0}".format(str(exc))
        error = True
        logger.error(error_message)
        logger.error(traceback.format_exc())

    return {"error": error, "error_message": error_message, "view_data": view_data, "tree_view": list(quick_tree_view), "total": total_count, "completed": completed_count, "failed": failed_count, "running": running_count, "queuing": queuing_count}


def get_job_history(expid: str, job_name: str) -> Dict[str, Any]:
    error = False
    error_message = ""
    path_to_job_logs = ""
    result = None
    try:
        APIBasicConfig.read()
        exp_paths = ExperimentPaths(expid)
        path_to_job_logs = exp_paths.tmp_log_dir
        result = ExperimentHistoryDirector(ExperimentHistoryBuilder(expid)).build_reader_experiment_history().get_historic_job_data(job_name)
    except Exception as exp:
        print((traceback.format_exc()))
        error = True
        error_message = str(exp)
        pass
    return {"error": error, "error_message": error_message, "history": result, "path_to_logs": path_to_job_logs}


def get_current_configuration_by_expid(expid: str, user_id: Optional[str]):
    """
    Gets the current configuration by expid. The procedure queries the historical database and the filesystem.
    :param expid: Experiment Identifier
    :return: configuration content formatted as a JSON object
    """
    error = False
    warning = False
    error_message = ""
    warning_message = ""
    currentRunConfig = {}
    currentFileSystemConfig = {}
    ALLOWED_CONFIG_KEYS = ['conf', 'exp', 'jobs', 'platforms', 'proj']

    def removeParameterDuplication(currentDict: dict, keyToRemove: str, exceptionsKeys=[]):
        if "exp" in currentDict.keys() and isinstance(currentDict["exp"], dict):
            try:
                for k, nested_d in list(currentDict["exp"].items()):
                    if k not in exceptionsKeys and isinstance(nested_d, dict):
                        nested_d.pop(keyToRemove, None)
            except Exception as exc:
                logger.error(f"Error while trying to eliminate duplicated key from config: {exc}")
                logger.error(traceback.format_exc())

    def sideDifferences(base_dict: dict, comparing_dict: dict):
        diffs = set()
        for key, value in base_dict.items():
            comp_value = comparing_dict.get(key)
            if isinstance(value, dict) and isinstance(comp_value, dict):
                aux_diffs = sideDifferences(value, comp_value)
                if len(aux_diffs) > 0:
                    diffs.add(key)
                for d in aux_diffs:
                    diffs.add(f"{key}.{d}")
            else:
                if isinstance(value, str) and isinstance(comp_value, int) or isinstance(value, int) and isinstance(comp_value, str):
                    if str(value) != str(comp_value):
                        diffs.add(key)
                elif value != comp_value:
                    diffs.add(key)
        return list(diffs)

    try:
        APIBasicConfig.read()
        autosubmitConfig = AutosubmitConfigResolver(
            expid, APIBasicConfig, ConfigParserFactory())
        is_as3 = isinstance(autosubmitConfig._configWrapper, confConfigStrategy)
        
        historicalDatabase = JobData.JobDataStructure(expid, APIBasicConfig)
        experimentRun = historicalDatabase.get_max_id_experiment_run()
        currentMetadata = json.loads(
            experimentRun.metadata) if experimentRun and experimentRun.metadata else None
        # currentRunId = experimentRun.run_id if experimentRun else None
        # Main keys = conf, exp, jobs, platforms, proj
        # Can we ignore proj by now? Including it.
        # TODO: Define which keys should be included in the answer
        if currentMetadata:
            currentRunConfig = {
                key: currentMetadata[key] 
                for key in currentMetadata 
                if not is_as3 or (key.lower() in ALLOWED_CONFIG_KEYS)
            }
        currentRunConfig["contains_nones"] = (
            not currentMetadata or 
            None in list(currentMetadata.values())
        )

        APIBasicConfig.read()
        try:
            autosubmitConfig.reload()
            currentFileSystemConfigContent = autosubmitConfig.get_full_config_as_dict()
            if currentFileSystemConfigContent:
                currentFileSystemConfig = {
                    key: currentFileSystemConfigContent[key] 
                    for key in currentFileSystemConfigContent 
                    if not is_as3 or (key.lower() in ALLOWED_CONFIG_KEYS)
                }
            currentFileSystemConfig["contains_nones"] = ( 
                not currentFileSystemConfigContent or 
                ( None in list(currentFileSystemConfigContent.values()) ) 
            )

        except Exception as exc:
            warning = True
            warning_message = "The filesystem system configuration can't be retrieved because '{}'".format(
                exc)
            logger.warning(warning_message)
            logger.warning(traceback.format_exc())
            currentFileSystemConfig["contains_nones"] = True

        removeParameterDuplication(currentRunConfig, "EXPID", ["experiment"])
        removeParameterDuplication(currentFileSystemConfig, "EXPID", ["experiment"])

    except Exception as exc:
        error = True
        error_message = str(exc)
        currentRunConfig["contains_nones"] = True
        currentFileSystemConfig["contains_nones"] = True
        logger.error("Exception while generating the configuration: " + error_message)
        logger.error(traceback.format_exc())

    diffs = sideDifferences(currentFileSystemConfig, currentRunConfig)
    return {
        "error": error, 
        "error_message": error_message, 
        "warning": warning, 
        "warning_message": warning_message, 
        "configuration_current_run": currentRunConfig, 
        "configuration_filesystem": currentFileSystemConfig, 
        "are_equal": len(diffs) == 0,
        "differences": diffs
    }


def get_experiment_runs(expid):
    """
    Get runs of the same experiment from historical db
    """
    error = False
    error_message = ""
    result = []

    def assign_current(job_dictionary, job_data_list, exp_history):
        for job_data in job_data_list:
            if job_data._finish == 0:
                job_current_info = job_dictionary.get(job_data.job_name, None)
                if job_current_info and job_current_info.finish_ts > 0:
                    job_data._finish = job_current_info.finish_ts
                    exp_history.update_job_finish_time_if_zero(job_data.job_name, job_data._finish)


    try:
        # TODO: TEST TEST TEST TEST
        # Current data
        joblist_loader = JobListLoaderDirector(JobListLoaderBuilder(expid)).build_loaded_joblist_loader()
        experiment_history = ExperimentHistoryDirector(ExperimentHistoryBuilder(expid)).build_reader_experiment_history()
        # time_0 = time.time()
        experiment_runs = experiment_history.manager.get_experiment_runs_dcs() # job_data_structure.get_experiment_runs()
        sim_jobs = experiment_history.manager.get_job_data_dcs_COMPLETED_by_section("SIM")
        post_jobs = experiment_history.manager.get_job_data_dcs_COMPLETED_by_section("POST")
        run_id_job_name_to_job_data_dc_COMPLETED = {}
        for job_dc in experiment_history.manager.get_job_data_dcs_all():
            if job_dc.status_code == common_utils.Status.COMPLETED:
                run_id_job_name_to_job_data_dc_COMPLETED[(job_dc.run_id, job_dc.job_name)] = job_dc
        run_id_wrapper_code_to_job_dcs = {}
        for key, job_dc in list(run_id_job_name_to_job_data_dc_COMPLETED.items()):
            if job_dc.wrapper_code:
                run_id, _ = key
                run_id_wrapper_code_to_job_dcs.setdefault((run_id, job_dc.wrapper_code), []).append(job_dc)

        run_dict_SIM = {}
        for job_data_dc in sim_jobs:
            run_dict_SIM.setdefault(job_data_dc.run_id, []).append(job_data_dc)
        run_dict_POST = {}
        for job_data_dc in post_jobs:
            run_dict_POST.setdefault(job_data_dc.run_id, []).append(job_data_dc)
        max_run_id = 0
        # print("Time spent in data retrieval and pre-process: {}".format(time.time() - time_0))
        if experiment_runs:
            for experiment_run in experiment_runs:
                max_run_id = max(experiment_run.run_id, max_run_id)
                valid_SIM_in_run = run_dict_SIM.get(experiment_run.run_id, [])
                valid_POST_in_run = run_dict_POST.get(experiment_run.run_id, [])
                # The content of the if block try to correct lack of finish time information in the Historical database
                # It may not be necessary in the future.
                if max_run_id == experiment_run.run_id:
                   assign_current(joblist_loader.job_dictionary, valid_SIM_in_run, experiment_history)
                   assign_current(joblist_loader.job_dictionary, valid_POST_in_run, experiment_history)
                result.append({"run_id": experiment_run.run_id,
                                "created": experiment_run.created,
                                "finish": common_utils.timestamp_to_datetime_format(experiment_run.finish),
                                "chunk_unit": experiment_run.chunk_unit,
                                "chunk_size": experiment_run.chunk_size,
                                "submitted": experiment_run.submitted,
                                "queuing": experiment_run.queuing,
                                "running": experiment_run.running,
                                "completed": experiment_run.completed,
                                "failed": experiment_run.failed,
                                "total": experiment_run.total,
                                "suspended": experiment_run.suspended,
                                "SYPD": experiment_run.getSYPD(valid_SIM_in_run),
                                "ASYPD": experiment_run.getASYPD(valid_SIM_in_run, valid_POST_in_run, run_id_wrapper_code_to_job_dcs)})
            result.sort(key=lambda x: x["run_id"], reverse=True)
        else:
            error = True
            error_message = "No data"
    except Exception as exp:
        error = True
        error_message = str(exp)
        logger.info( traceback.format_exc() )
        logger.info("Error: " + error_message)
        pass
        # for full debug, uncomment this
        #raise exp
    return {"error": error, "error_message": error_message, "runs": result}


def read_esarchive(result):
    # t0 = time.time()
    # Using as_times.db as reference
    current_latency = 10000
    current_bandwidth = 10000
    avg_latency = 1000
    avg_bandwidth = 1000
    if os.path.exists('/esarchive/scratch/pbretonn/monitor-esarchive/plot/io-benchmark/stats-io.txt'):
        output = subprocess.check_output(['tail', '-n', '49', '/esarchive/scratch/pbretonn/monitor-esarchive/plot/io-benchmark/stats-io.txt'])

        if len(output) > 0:
            lines = output.split('\n')[:-1]  # Get rid of last line
            last_line = lines[-1].split()
            try:
                current_bandwidth = float(last_line[1])
            except IndexError:
                # Default to 90.0
                current_bandwidth = 90.0
            try:
                current_latency = float(last_line[2])
            except IndexError:
                current_latency = 2.0
            try:
                last_day = [line.split() for line in lines[:-1]]
                avg_bandwidth = sum(float(last[1])
                                    for last in last_day if len(last) > 1) / len(last_day)
                avg_latency = sum(float(last[2])
                                  for last in last_day if len(last) > 2) / len(last_day)
            except IndexError:
                avg_bandwidth = 90.0
                avg_latency = 2.0

        result.append(True)
    else:
        result.append(False)
    result.append(avg_bandwidth)
    result.append(avg_latency)
    result.append(current_bandwidth)
    result.append(current_latency)


def test_esarchive_status():
    logger.warning("WARNING: This background task have been REMOVED")


def enforceLocal(log):
    try:
        try:
            locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')
        except Exception:
            try:
                locale.setlocale(locale.LC_ALL, 'C.utf8')
            except Exception:
                try:
                    locale.setlocale(locale.LC_ALL, 'en_GB')
                except Exception:
                    locale.setlocale(locale.LC_ALL, 'es_ES')
    except Exception:
        log.info("Locale C.utf8 is not found, using '{0}' as fallback".format("C"))
        locale.setlocale(locale.LC_ALL, 'C')
