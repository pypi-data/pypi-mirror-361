#!/bin/env/python

class StatsSummary(object):

  def __init__(self):    
    # Counters
    self.submitted_count = 0 
    self.run_count = 0
    self.completed_count = 0
    self.failed_count = 0
    # Consumption
    self.expected_consumption = 0.0
    self.real_consumption = 0.0
    self.failed_real_consumption = 0.0
    # CPU Consumption
    self.expected_cpu_consumption: float = 0.0
    self.cpu_consumption = 0.0
    self.failed_cpu_consumption = 0.0
    self.total_queue_time = 0.0
    self.cpu_consumption_percentage = 0.0
  
  def calculate_consumption_percentage(self):
    if self.expected_cpu_consumption > 0.0:
      self.cpu_consumption_percentage = round((self.cpu_consumption / self.expected_cpu_consumption) * 100, 2)
  
  def get_as_dictionary(self):
    return {
      "cpuConsumptionPercentage": self.cpu_consumption_percentage,
      "totalQueueTime": round(self.total_queue_time, 2),
      "submittedCount": self.submitted_count,
      "runCount": self.run_count,
      "completedCount": self.completed_count,
      "failedCount": self.failed_count,
      "expectedConsumption": round(self.expected_consumption, 4),
      "realConsumption": round(self.real_consumption, 4),
      "failedRealConsumption": round(self.failed_real_consumption, 4),
      "expectedCpuConsumption": round(self.expected_cpu_consumption, 4),
      "cpuConsumption": round(self.cpu_consumption, 4),
      "failedCpuConsumption": round(self.failed_cpu_consumption, 4)
    }

  def get_as_list(self):
    return [
      "Summary: ",
      "{}  :  {}".format("CPU Consumption Percentage", str(self.cpu_consumption_percentage) + "%"),
      "{}  :  {:,} hrs.".format("Total Queue Time", round(self.total_queue_time, 2)),
      "{}  :  {:,}".format("Submitted Count", self.submitted_count),
      "{}  :  {:,}".format("Run Count", self.run_count),
      "{}  :  {:,}".format("Completed Count", self.completed_count),
      "{}  :  {:,}".format("Failed Count", self.failed_count),
      "{}  :  {:,} hrs.".format("Expected Consumption", round(self.expected_consumption, 4)),
      "{}  :  {:,} hrs.".format("Real Consumption", round(self.real_consumption, 4)),
      "{}  :  {:,} hrs.".format("Failed Real Consumption", round(self.failed_real_consumption, 4)),
      "{}  :  {:,} hrs.".format("Expected CPU Consumption", round(self.expected_cpu_consumption, 4)),
      "{}  :  {:,} hrs.".format("CPU Consumption", round(self.cpu_consumption, 4)),
      "{}  :  {:,} hrs.".format("Failed CPU Consumption", round(self.failed_cpu_consumption, 4))
    ]
  









  