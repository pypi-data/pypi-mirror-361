from dataclasses import dataclass
from typing import Dict, List, Union

from clarifai_grpc.grpc.api import resources_pb2

from clarifai_evals.constant import DataTypes, TaskTypes, VisualizationTypes


@dataclass
class MetricResult:
  """This class is used to store the results of a metric"""

  metric_name: str
  summary_score: float = None
  perclass_scores: Dict = None
  persample_scores: List = None
  perobject_scores: List = None
  persample_explanations: List = None
  graph_data: Dict = None
  metric_info: Dict = None


@dataclass
class ResultData:
  """This class is used to store the results of the evaluation"""

  metrics_results: List[MetricResult]
  sub_template: str
  correctness: List = None
  considered_gt: Union[List, Dict] = None


@dataclass
class ResultResponse:
  """This class is used to store the response of the evaluation"""

  provided_predictions: Union[resources_pb2.Data]
  provided_inputs: Union[resources_pb2.Data] = None
  provided_gts: [resources_pb2.Data] = None
  gt_results: List[ResultData] = None
  judge_results: List[ResultData] = None

  def __post_init__(self):
    if self.gt_results is None and self.judge_results is None:
      raise ValueError("At least one of gt_results or judge_results should be provided")


def transform_result_to_proto(result: ResultResponse, task_type: TaskTypes):
  """Transforms the result to proto format
  Args:
      result (ResultResponse): The result of the evaluation
      task_type (TaskType): The task type of the evaluation
  """

  results_list = []
  if result.gt_results:
    results_list.extend(result.gt_results)
  if result.judge_results:
    results_list.extend(result.judge_results)

  template_proto_list, summary_results_proto_list, input_results_proto_list = [], [], []

  for metric_grp_result in results_list:
    template_proto = resources_pb2.WorkflowVersionEvaluationTemplate(
        id=metric_grp_result.sub_template,
        description="",
        task_types=[
            resources_pb2.WorkflowVersionEvaluationTemplate.TaskType.Value(task_type.value)
        ],
        workflow_version_evaluation_metrics=[
            resources_pb2.WorkflowVersionEvaluationMetric(
                id=metric_result.metric_name,
                description=metric_result.metric_info.get("description", ""),
                summary="",
                data_type=metric_result.metric_info.get("unit", DataTypes.undefined).value,
                visualisation_type=resources_pb2.WorkflowVersionEvaluationMetric.VisualisationType.
                Value(
                    metric_result.metric_info.get("graph_type",
                                                  VisualizationTypes.undefined).value),
            ) for metric_result in metric_grp_result.metrics_results
        ])

    summary_results_proto = resources_pb2.WorkflowEvaluationResult(
        summary=resources_pb2.WorkflowEvaluationResultSummary(evaluation_metric_values=[
            resources_pb2.EvaluationMetricValue(
                evaluation_metric_id=mv.metric_name,
                explanation="",
                metric_value=resources_pb2.MetricValue(float_value=mv.summary_score),
                per_concept_values={
                    k: resources_pb2.MetricValue(float_value=v)
                    for k, v in mv.perclass_scores.items()
                } if mv.perclass_scores else None) for mv in metric_grp_result.metrics_results
        ]))

    template_proto_list.append(template_proto)
    summary_results_proto_list.append(summary_results_proto)

  for inp_idx in range(len(result.provided_predictions)):
    inp = resources_pb2.Input(
        id=str(inp_idx),
        data=result.provided_inputs[inp_idx]) if result.provided_inputs is not None and len(
            result.provided_inputs) > inp_idx else None
    gts = [result.provided_gts[inp_idx]
          ] if result.provided_gts is not None and len(result.provided_gts) > inp_idx else None

    input_evaluation_metric_values = []
    for grp_result in results_list:  #for each ResultData inside ResultResponse (gt_results or judge_results)
      for metric_res in grp_result.metrics_results:  #for each MetricResult inside ResultData
        if metric_res.persample_scores is not None and len(metric_res.persample_scores) > inp_idx:
          metric_value = resources_pb2.MetricValue(
              float_value=metric_res.persample_scores[inp_idx])
        else:
          metric_value = None

        if metric_res.persample_explanations is not None and len(
            metric_res.persample_explanations) > inp_idx:
          explanation = metric_res.persample_explanations[inp_idx]
        else:
          explanation = ""

        if metric_res.perobject_scores is not None and len(metric_res.perobject_scores) > inp_idx:
          per_region_values = {
              str(j):
              resources_pb2.MetricValue(float_value=metric_res.perobject_scores[inp_idx][j])
              for j in range(len(metric_res.perobject_scores[inp_idx]))
          }
        else:
          per_region_values = None

        if metric_value is None and per_region_values is None and explanation == "":
          continue
        metric_value_object = resources_pb2.InputEvaluationMetricValue(
            evaluation_metric_id=metric_res.metric_name,
            metric_value=metric_value,
            explanation=str(explanation),
            per_region_values=per_region_values)
        input_evaluation_metric_values.append(metric_value_object)

    inp_eval_res = resources_pb2.WorkflowEvaluationInputResult(
        input_evaluation_metric_values=input_evaluation_metric_values)
    main_proto = resources_pb2.WorkflowVersionEvaluationData(
        id=str(inp_idx),
        input=inp,
        ground_truths=gts,
        predictions=[result.provided_predictions[inp_idx]],
        workflow_evaluation_sample_result=inp_eval_res)
    input_results_proto_list.append(main_proto)

  return_dict = {
      "WorkflowVersionEvaluationTemplate": template_proto_list,
      "WorkflowEvaluationResult": summary_results_proto_list,
      "WorkflowVersionEvaluationData": input_results_proto_list
  }

  return return_dict
