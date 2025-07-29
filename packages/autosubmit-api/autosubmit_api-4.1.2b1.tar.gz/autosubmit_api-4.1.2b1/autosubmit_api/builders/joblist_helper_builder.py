#!/usr/bin/env python
from typing import Optional
from autosubmit_api.components.experiment.pkl_organizer import PklOrganizer
from autosubmit_api.config.basicConfig import APIBasicConfig
from autosubmit_api.builders.configuration_facade_builder import AutosubmitConfigurationFacadeBuilder, ConfigurationFacadeDirector
from autosubmit_api.builders.basic_builder import BasicBuilder
from autosubmit_api.components.jobs.joblist_helper import JobListHelper
from abc import ABCMeta, abstractmethod


class Builder(BasicBuilder, metaclass=ABCMeta):
  def __init__(self, expid: str):
    super(Builder, self).__init__(expid)

  @abstractmethod
  def generate_autosubmit_configuration_facade(self):
    pass

  @abstractmethod
  def generate_pkl_organizer(self):
    pass

  @abstractmethod
  def make_joblist_helper(self) -> JobListHelper:
    pass

class JobListHelperBuilder(Builder):
  def __init__(self, expid: str):
    super(JobListHelperBuilder, self).__init__(expid)

  def _validate_autosubmit_configuration_facade(self):
    if not self.configuration_facade:
      raise Exception("AutosubmitConfigurationFacade is missing.")

  def _validate_pkl_organizer(self):
    if not self.pkl_organizer:
      raise Exception("PklOrganizer is missing.")

  def generate_autosubmit_configuration_facade(self):
    self._validate_basic_config()
    self.configuration_facade = ConfigurationFacadeDirector(AutosubmitConfigurationFacadeBuilder(self.expid)).build_autosubmit_configuration_facade(self.basic_config)

  def generate_pkl_organizer(self):
    self._validate_autosubmit_configuration_facade()
    self.pkl_organizer = PklOrganizer(self.expid)

  def make_joblist_helper(self) -> JobListHelper:
    self._validate_basic_config()
    self._validate_autosubmit_configuration_facade()
    self._validate_pkl_organizer()
    return JobListHelper(self.expid, self.configuration_facade, self.pkl_organizer, self.basic_config)

class JobListHelperDirector:
  def __init__(self, builder: Builder):
    self.builder = builder

  def _set_basic_config(self, basic_config=None):
    if basic_config:
      self.builder.set_basic_config(basic_config)
    else:
      self.builder.generate_basic_config()

  def build_job_list_helper(self, basic_config: Optional[APIBasicConfig] = None) -> JobListHelper:
    self._set_basic_config(basic_config)
    self.builder.generate_autosubmit_configuration_facade()
    self.builder.generate_pkl_organizer()
    return self.builder.make_joblist_helper()
