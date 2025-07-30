from dataclasses import dataclass
from typing import Dict, List


@dataclass
class MetricResult:
  """This class is used to store the results of a metric"""

  metric_name: str
  summary_score: float
  perclass_scores: List = None
  graph_data: Dict = None


@dataclass
class ResultData:
  """This class is used to store the results of the evaluation"""

  considered_gt: List
  correctness: List
  metrics_results: List[MetricResult]


@dataclass
class ResultResponse:
  """This class is used to store the response of the evaluation"""

  provided_predictions: List
  gt_results: ResultData = None
  judge_results: ResultData = None

  def __post_init__(self):
    if self.gt_results is None and self.judge_results is None:
      raise ValueError("At least one of gt_results or judge_results should be provided")
