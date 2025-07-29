#!/usr/bin/env python
from typing import Optional
from autosubmit_api.config.basicConfig import APIBasicConfig
from autosubmit_api.builders.basic_builder import BasicBuilder
from autosubmit_api.components.jobs.joblist_loader import JobListLoader
from autosubmit_api.builders.joblist_helper_builder import JobListHelperBuilder, JobListHelperDirector

class JobListLoaderBuilder(BasicBuilder):
  def __init__(self, expid):
    super(JobListLoaderBuilder, self).__init__(expid)

  def generate_joblist_helper(self):
    self._validate_basic_config()
    self.joblist_helper = JobListHelperDirector(JobListHelperBuilder(self.expid)).build_job_list_helper(self.basic_config)

  def _validate_joblist_helper(self):
    if not self.joblist_helper:
      raise Exception("JobListHelper is missing.")

  def make_joblist_loader(self) -> JobListLoader:
    self._validate_basic_config()
    self._validate_joblist_helper()
    return JobListLoader(self.expid, self.joblist_helper)

class JobListLoaderDirector:
  def __init__(self, builder: JobListLoaderBuilder):
    self.builder = builder

  def _set_basic_config(self, basic_config=None):
    if basic_config:
      self.builder.set_basic_config(basic_config)
    else:
      self.builder.generate_basic_config()

  def build_loaded_joblist_loader(self, basic_config: Optional[APIBasicConfig]=None) -> JobListLoader:
    self._set_basic_config(basic_config)
    self.builder.generate_joblist_helper()
    joblist_loader = self.builder.make_joblist_loader()
    joblist_loader.load_jobs()
    return joblist_loader