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

from abc import ABC, abstractmethod
from configparser import ConfigParser as PyConfigParser
from typing import Union

from autosubmitconfigparser.config.configcommon import (
    AutosubmitConfig as Autosubmit4Config,
)
from bscearth.utils.config_parser import ConfigParser, ConfigParserFactory


class IConfigStrategy(ABC):
    """
    Public interface for Autosubmit config files

    :param expid: experiment identifier
    :type expid: str
    """

    @abstractmethod
    def jobs_parser(self):
        """"""

    @abstractmethod
    def experiment_file(self):
        """
        Returns experiment's config file name
        """

    @abstractmethod
    def platforms_parser(self) -> PyConfigParser:
        """
        Returns experiment's platforms parser object

        :return: platforms config parser object
        """

    @abstractmethod
    def platforms_file(self):
        """
        Returns experiment's platforms config file name

        :return: platforms config file's name
        :rtype: str
        """

    @abstractmethod
    def project_file(self):
        """
        Returns project's config file name
        """

    @abstractmethod
    def jobs_file(self):
        """
        Returns project's jobs file name
        """

    @abstractmethod
    def get_full_config_as_dict(self):
        """
        Returns full configuration as json object
        """

    @abstractmethod
    def get_project_dir(self):
        """
        Returns experiment's project directory

        :return: experiment's project directory
        :rtype: str
        """

    @abstractmethod
    def get_queue(self, section):
        """
        Get queue for the given job type
        :param section: job type
        :type section: str
        :return: queue
        :rtype: str
        """

    @abstractmethod
    def get_job_platform(self, section: str) -> str:
        """
        Gets wallclock for the given job type
        :param section: job type
        :return: wallclock time
        """

    @abstractmethod
    def get_platform_queue(self, platform):
        """"""

    @abstractmethod
    def get_platform_serial_queue(self, platform):
        """"""

    @abstractmethod
    def get_platform_project(self, platform):
        """"""

    @abstractmethod
    def get_platform_wallclock(self, platform):
        """"""

    @abstractmethod
    def get_platform_conf_footprint(self, platform):
        """"""

    def get_wallclock(self, section):
        """
        Gets wallclock for the given job type
        :param section: job type
        :type section: str
        :return: wallclock time
        :rtype: str
        """

    def get_synchronize(self, section):
        """
        Gets wallclock for the given job type
        :param section: job type
        :type section: str
        :return: wallclock time
        :rtype: str
        """

    def get_processors(self, section: str) -> str:
        """
        Gets processors needed for the given job type
        :param section: job type
        :return: wallclock time
        """

    def get_threads(self, section):
        """
        Gets threads needed for the given job type
        :param section: job type
        :type section: str
        :return: threads needed
        :rtype: str
        """

    def get_tasks(self, section):
        """
        Gets tasks needed for the given job type
        :param section: job type
        :type section: str
        :return: tasks (processes) per host
        :rtype: str
        """

    def get_scratch_free_space(self, section):
        """
        Gets scratch free space needed for the given job type
        :param section: job type
        :type section: str
        :return: percentage of scratch free space needed
        :rtype: int
        """

    def get_memory(self, section):
        """
        Gets memory needed for the given job type
        :param section: job type
        :type section: str
        :return: memory needed
        :rtype: str
        """

    def get_memory_per_task(self, section):
        """
        Gets memory per task needed for the given job type
        :param section: job type
        :type section: str
        :return: memory per task needed
        :rtype: str
        """

    def get_migrate_user_to(self, section):
        """
        Returns the user to change to from platform config file.

        :return: migrate user to
        :rtype: str
        """
        # return self._platforms_parser.get_option(section, 'USER_TO', '').lower()

    def get_current_user(self, section):
        """
        Returns the user to be changed from platform config file.

        :return: migrate user to
        :rtype: str
        """

    def get_current_project(self, section):
        """
        Returns the project to be changed from platform config file.

        :return: migrate user to
        :rtype: str
        """

    def set_new_user(self, section, new_user):
        """
        Sets new user for given platform
        :param new_user:
        :param section: platform name
        :type: str
        """

    def get_migrate_project_to(self, section):
        """
        Returns the project to change to from platform config file.

        :return: migrate project to
        :rtype: str
        """

    def set_new_project(self, section, new_project):
        """
        Sets new project for given platform
        :param new_project:
        :param section: platform name
        :type: str
        """

    def get_custom_directives(self, section):
        """
        Gets custom directives needed for the given job type
        :param section: job type
        :type section: str
        :return: custom directives needed
        :rtype: str
        """

    def check_conf_files(self):
        """
        Checks configuration files (autosubmit, experiment jobs and platforms), looking for invalid values, missing
        required options. Prints results in log

        :return: True if everything is correct, False if it finds any error
        :rtype: bool
        """

    def check_autosubmit_conf(self):
        """
        Checks experiment's autosubmit configuration file.

        :return: True if everything is correct, False if it founds any error
        :rtype: bool
        """

    def check_platforms_conf(self):
        """
        Checks experiment's queues configuration file.

        :return: True if everything is correct, False if it founds any error
        :rtype: bool
        """

    def check_jobs_conf(self):
        """
        Checks experiment's jobs configuration file.

        :return: True if everything is correct, False if it founds any error
        :rtype: bool
        """

    def check_expdef_conf(self):
        """
        Checks experiment's experiment configuration file.

        :return: True if everything is correct, False if it founds any error
        :rtype: bool
        """

    def check_proj(self):
        """
        Checks project config file

        :return: True if everything is correct, False if it founds any error
        :rtype: bool
        """

    def check_wrapper_conf(self):
        """"""

    def reload(self):
        """
        Creates parser objects for configuration files
        """

    def load_parameters(self):
        """
        Load parameters from experiment and autosubmit config files. If experiment's type is not none,
        also load parameters from model's config file

        :return: a dictionary containing tuples [parameter_name, parameter_value]
        :rtype: dict
        """

    def load_project_parameters(self):
        """
        Loads parameters from model config file

        :return: dictionary containing tuples [parameter_name, parameter_value]
        :rtype: dict
        """

    def set_expid(self, exp_id):
        """
        Set experiment identifier in autosubmit and experiment config files

        :param exp_id: experiment identifier to store
        :type exp_id: str
        """

    def get_project_type(self):
        """
        Returns project type from experiment config file

        :return: project type
        :rtype: str
        """

    def get_file_project_conf(self):
        """
        Returns path to project config file from experiment config file

        :return: path to project config file
        :rtype: str
        """

    def get_file_jobs_conf(self):
        """
        Returns path to project config file from experiment config file

        :return: path to project config file
        :rtype: str
        """

    def get_git_project_origin(self):
        """
        Returns git origin from experiment config file

        :return: git origin
        :rtype: str
        """

    def get_git_project_branch(self):
        """
        Returns git branch  from experiment's config file

        :return: git branch
        :rtype: str
        """

    def get_git_project_commit(self):
        """
        Returns git commit from experiment's config file

        :return: git commit
        :rtype: str
        """

    def get_submodules_list(self):
        """
        Returns submodules list from experiment's config file
        Default is --recursive
        :return: submodules to load
        :rtype: list
        """

    def get_project_destination(self):
        """
        Returns git commit from experiment's config file

        :return: git commit
        :rtype: str
        """

    def set_git_project_commit(self, as_conf: Autosubmit4Config):
        """
        Function to register in the configuration the commit SHA of the git project version.
        :param as_conf: Configuration class for exteriment
        """

    def get_svn_project_url(self):
        """
        Gets subversion project url

        :return: subversion project url
        :rtype: str
        """

    def get_svn_project_revision(self):
        """
        Get revision for subversion project

        :return: revision for subversion project
        :rtype: str
        """

    def get_local_project_path(self):
        """
        Gets path to origin for local project

        :return: path to local project
        :rtype: str
        """

    def get_date_list(self):
        """
        Returns startdates list from experiment's config file

        :return: experiment's startdates
        :rtype: list
        """

    def get_num_chunks(self):
        """
        Returns number of chunks to run for each member

        :return: number of chunks
        :rtype: int
        """

    def get_chunk_ini(self, default=1):
        """
        Returns the first chunk from where the experiment will start

        :param default:
        :return: initial chunk
        :rtype: int
        """

    def get_chunk_size_unit(self) -> str:
        """
        Unit for the chunk length

        :return: Unit for the chunk length  Options: {hour, day, month, year}
        :rtype: str
        """

    def get_chunk_size(self, default: int = 1) -> int:
        """
        Chunk Size as defined in the expdef file.

        :return: Chunksize, 1 as default.
        :rtype: int
        """

    def get_member_list(self, run_only=False):
        """
        Returns members list from experiment's config file

        :return: experiment's members
        :rtype: list
        """

    def get_rerun(self):
        """
        Returns startdates list from experiment's config file

        :return: rerurn value
        :rtype: list
        """

    def get_chunk_list(self):
        """
        Returns chunk list from experiment's config file

        :return: experiment's chunks
        :rtype: list
        """

    def get_platform(self):
        """
        Returns main platforms from experiment's config file

        :return: main platforms
        :rtype: str
        """

    def set_platform(self, hpc):
        """
        Sets main platforms in experiment's config file

        :param hpc: main platforms
        :type: str
        """

    def set_version(self, autosubmit_version):
        """
        Sets autosubmit's version in autosubmit's config file

        :param autosubmit_version: autosubmit's version
        :type autosubmit_version: str
        """

    def get_version(self):
        """
        Returns version number of the current experiment from autosubmit's config file

        :return: version
        :rtype: str
        """

    def get_total_jobs(self):
        """
        Returns max number of running jobs  from autosubmit's config file

        :return: max number of running jobs
        :rtype: int
        """

    def get_max_wallclock(self):
        """
        Returns max wallclock

        :rtype: str
        """

    def get_max_processors(self):
        """
        Returns max processors from autosubmit's config file

        :rtype: str
        """

    def get_max_waiting_jobs(self):
        """
        Returns max number of waiting jobs from autosubmit's config file

        :return: main platforms
        :rtype: int
        """

    def get_default_job_type(self):
        """
        Returns the default job type from experiment's config file

        :return: default type such as bash, python, r..
        :rtype: str
        """

    def get_safetysleeptime(self):
        """
        Returns safety sleep time from autosubmit's config file

        :return: safety sleep time
        :rtype: int
        """

    def set_safetysleeptime(self, sleep_time):
        """
        Sets autosubmit's version in autosubmit's config file

        :param sleep_time: value to set
        :type sleep_time: int
        """

    def get_retrials(self):
        """
        Returns max number of retrials for job from autosubmit's config file

        :return: safety sleep time
        :rtype: int
        """

    def get_notifications(self):
        """
        Returns if the user has enabled the notifications from autosubmit's config file

        :return: if notifications
        :rtype: string
        """

    def get_remote_dependencies(self):
        """
        Returns if the user has enabled the remote dependencies from autosubmit's config file

        :return: if remote dependencies
        :rtype: bool
        """

    def get_wrapper_type(self):
        """
        Returns what kind of wrapper (VERTICAL, MIXED-VERTICAL, HORIZONTAL, HYBRID, NONE) the user has configured in the autosubmit's config

        :return: wrapper type (or none)
        :rtype: string
        """

    def get_wrapper_jobs(self):
        """
        Returns the jobs that should be wrapped, configured in the autosubmit's config

        :return: expression (or none)
        :rtype: string
        """

    def get_max_wrapped_jobs(self):
        """
        Returns the maximum number of jobs that can be wrapped together as configured in autosubmit's config file

        :return: maximum number of jobs (or total jobs)
        :rtype: string
        """
        # return int(self._conf_parser.get_option('wrapper', 'MAXWRAPPEDJOBS', self.get_total_jobs()))

    def get_wrapper_check_time(self):
        """
        Returns time to check the status of jobs in the wrapper

        :return: wrapper check time
        :rtype: int
        """

    def get_wrapper_machinefiles(self):
        """
        Returns the strategy for creating the machinefiles in wrapper jobs

        :return: machinefiles function to use
        :rtype: string
        """

    def get_wrapper_queue(self):
        """
        Returns the wrapper queue if not defined, will be the one of the first job wrapped

        :return: expression (or none)
        :rtype: string
        """

    def get_jobs_sections(self):
        """
        Returns the list of sections defined in the jobs config file

        :return: sections
        :rtype: list
        """

    def get_copy_remote_logs(self):
        """
        Returns if the user has enabled the logs local copy from autosubmit's config file

        :return: if logs local copy
        :rtype: bool
        """

    def get_mails_to(self):
        """
        Returns the address where notifications will be sent from autosubmit's config file

        :return: mail address
        :rtype: [str]
        """

    def get_communications_library(self):
        """
        Returns the communications library from autosubmit's config file. Paramiko by default.

        :return: communications library
        :rtype: str
        """

    def get_storage_type(self):
        """
        Returns the communications library from autosubmit's config file. Paramiko by default.

        :return: communications library
        :rtype: str
        """

    def get_workflow_commit(self) -> Union[str, None]:
        """
        Returns the commit of the workflow

        :return: commit
        """

    @staticmethod
    def is_valid_mail_address(mail_address: str) -> bool:
        """"""

    def is_valid_communications_library(self):
        """"""

    def is_valid_storage_type(self):
        """"""

    def is_valid_jobs_in_wrapper(self):
        """"""

    def is_valid_git_repository(self):
        """"""

    @staticmethod
    def get_parser(parser_factory: ConfigParserFactory, file_path: str) -> ConfigParser:
        """"""
