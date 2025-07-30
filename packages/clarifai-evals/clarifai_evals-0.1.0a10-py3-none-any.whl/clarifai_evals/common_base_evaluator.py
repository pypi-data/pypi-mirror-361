import math
from collections import defaultdict
from typing import Callable, Dict, List, Union

from joblib import Parallel, delayed

from clarifai_evals.result_data import MetricResult, ResultData, ResultResponse


class CommonBaseEvaluator:
  """This is the base class for all evaluators. It contains the basic structure of the evaluator and the evaluate method."""

  def __init__(
      self,
      description: str,
      task_type: str,
      all_metrics: Dict = {},
      quick_metrics: Dict = {},
      batch_size: int = 32,
  ):
    """
    Initializes the evaluator object
    Args:
        description (str): The description of the evaluator, eg: Image Classification Evaluator
        task_type (str): The type of task the evaluator is designed for, eg: image-classification
        all_metrics (Dict): A dictionary containing all the metrics available for the evaluator
        quick_metrics (Dict): A dictionary containing the on-the-fly metrics available for the evaluator
        batch_size (int): The batch size for the evaluator
    """
    self.description = description
    self.task_type = task_type
    self.all_metrics = all_metrics
    self.quick_metrics = quick_metrics
    self.batch_size = batch_size

  def evaluate(
      self,
      prediction_batch: List,
      **kwargs,
  ) -> ResultResponse:
    """
    This method evaluates the model based on the given inputs
    Args:
        prediction_batch (List): The list of predictions
        **kwargs: The input arguments like ground_truth_batch, query_batch, context_batch, sub_template, mode, etc.
    Returns:
        dict: The evaluation results
    """
    return NotImplementedError("Override this method in the child class")

  def _parallel_evaluate(self, callback_fn: Callable, prediction_batch: List,
                         static_argsdict: Dict, **batch_args) -> List[ResultData]:
    """This method evaluates the model based on the given inputs
        Args:
            callback_fn (Callable): The callback function to evaluate the model on a batch
            prediction_batch (List): The list of predictions
            static_argsdict (Dict): The static arguments which are common to all batches like mode, sub_template, etc.
            **batch_args: The batch arguments like prediction_batch, ground_truth_batch, query_batch, context_batch, etc.
        Returns:
            List[List[ResultResponse]]: The evaluation results
    """
    num_batches = math.ceil(len(prediction_batch) / self.batch_size)
    distributed_results = self._distribute_evals(
        num_batches=num_batches,
        callback_fn=callback_fn,
        prediction_batch=prediction_batch,
        static_argsdict=static_argsdict,
        **batch_args,
    )
    return self._gather_evals(distributed_results)

  def _distribute_evals(self, num_batches: int, callback_fn: Callable, prediction_batch: List,
                        static_argsdict: Dict, **batch_args) -> List[List[ResultData]]:
    """This method distributes the evaluations across multiple batches
    Args:
        num_batches (int): The number of batches
        callback_fn (Callable): The callback function to evaluate the model on a batch
        prediction_batch (List): The list of predictions
        static_argsdict (Dict): The static arguments which are common to all batches like mode, sub_template, etc.
        **batch_args: The batch arguments like prediction_batch, ground_truth_batch, query_batch, context_batch, etc.
    Returns:
        List[List[ResultResponse]]: The evaluation results
    """

    list_ResultData = Parallel(n_jobs=num_batches)(delayed(self._callback_batcheval)(
        batch_no,
        callback_fn,
        prediction_batch,
        static_argsdict,
        **batch_args,
    ) for batch_no in range(num_batches))
    return list_ResultData

  def _callback_batcheval(self, batch_no, callback_fn: Callable, prediction_batch: List,
                          static_argsdict: Dict, **batch_args) -> List[ResultData]:
    """This method evaluates the model based on the given inputs
    Args:
        batch_no (int): The current batch number
        callback_fn (Callable): The callback function to evaluate the model on a batch
        prediction_batch (List): The list of predictions
        static_argsdict (Dict): The static arguments which are common to all batches like mode, sub_template, etc.
        **batch_args: The batch arguments like prediction_batch, ground_truth_batch, query_batch, context_batch, etc.
    Returns:
        List[ResultData]: The evaluation results
    """
    current_batch_agrs = {}
    batch_size = self.batch_size
    for key in batch_args:
      current_batch_agrs[key] = batch_args[key][
          batch_no * batch_size:batch_no * batch_size + batch_size] if batch_args[key] else None
    current_prediction_batch = prediction_batch[batch_no * batch_size:
                                                batch_no * batch_size + batch_size]

    return callback_fn(current_prediction_batch, static_argsdict, **current_batch_agrs)

  def _gather_evals(
      self, batch_results: List[Union[List[ResultData], ResultResponse]]) -> List[ResultData]:
    """This method is used to gather the evaluations from multiple batches
          Args:
              batch_results (List[List[ResultData]]): The evaluation results from multiple batches
          Returns:
              List[ResultData]: The aggregated evaluation results
      """
    if not batch_results:
      return []

    if batch_results and isinstance(batch_results[0], ResultResponse):
      return self._group_and_merge_evals(batch_results)

    grouped_by_template = defaultdict(list)

    for batch in batch_results:
      for result_data in batch:
        grouped_by_template[result_data.sub_template].append(result_data)

    merged_results = self._merge_metrics(grouped_by_template)
    return merged_results

  def _group_and_merge_evals(self, batch_results: List[ResultResponse]) -> ResultResponse:
    gathered_result = ResultResponse(gt_results=[], judge_results=[], provided_predictions=[])
    """This method is used to gather the evaluations
    Args:
        batch_results (List[List[ResultResponse]]): The evaluation results
    Returns:
        ResultResponse: The gathered evaluation results
    """
    if not batch_results:
      return []

    grouped_by_gt_template = defaultdict(list)
    grouped_by_judge_template = defaultdict(list)

    for batch in batch_results:
      for result_data in batch.gt_results:
        grouped_by_gt_template[result_data.sub_template].append(result_data)
      for result_data in batch.judge_results:
        grouped_by_judge_template[result_data.sub_template].append(result_data)

    merged_gt_results = self._merge_metrics(grouped_by_gt_template)
    merged_judge_results = self._merge_metrics(grouped_by_judge_template)

    gathered_result.gt_results = merged_gt_results
    gathered_result.judge_results = merged_judge_results

    return gathered_result

  def _merge_metrics(self, grouped_by_template: Dict) -> List[ResultData]:
    """
    This method is used to merge the metrics
    Args:
        grouped_by_template (Dict): The metrics grouped by template
    Returns:
        List[ResultData]: The merged metrics
    """
    merged_results = []
    for sub_template, result_data_list in grouped_by_template.items():
      merged_metrics = defaultdict(list)

      for result_data in result_data_list:
        for metric in result_data.metrics_results:
          merged_metrics[metric.metric_name].append(metric)

      combined_metrics = []
      for metric_name, metric_list in merged_metrics.items():
        combined_metric = MetricResult(
            metric_name=metric_name,
            summary_score=(sum(m.summary_score for m in metric_list if m.summary_score is not None)
                           / max(len([m for m in metric_list if m.summary_score is not None]), 1))
            if metric_list else None,
            perclass_scores={
                k: (scores := [
                    m.perclass_scores[k] for m in metric_list
                    if m.perclass_scores and k in m.perclass_scores.keys()
                ]) and sum(scores) / len(scores)
                for m in metric_list if m.perclass_scores for k, v in m.perclass_scores.items()
            },
            persample_scores=([
                score for m in metric_list
                if isinstance(m.persample_scores, list) for score in m.persample_scores
            ] if all(
                isinstance(m.persample_scores, list) for m in metric_list
                if m.persample_scores) else {
                    k: (scores := [
                        m.persample_scores[k] for m in metric_list
                        if isinstance(m.persample_scores, dict) and k in m.persample_scores
                    ]) and sum(scores) / len(scores)
                    for k in {
                        key
                        for m in metric_list
                        if isinstance(m.persample_scores, dict) for key in m.persample_scores
                    }
                }),
            perobject_scores=[
                score for m in metric_list
                if m.perobject_scores is not None for score in m.perobject_scores
            ],
            persample_explanations=[
                exp for m in metric_list
                if m.persample_explanations is not None for exp in m.persample_explanations
            ],
            graph_data=None,
            metric_info={
                k: v
                for m in metric_list if m.metric_info for k, v in m.metric_info.items()
            },
        )
        combined_metrics.append(combined_metric)

      combined_considered_gt = {
          k: v
          for rd in result_data_list if rd.considered_gt for k, v in rd.considered_gt.items()
      } if isinstance(result_data_list[0].considered_gt, dict) else [
          item for rd in result_data_list if rd.considered_gt for item in rd.considered_gt
      ]

      merged_result_data = ResultData(
          metrics_results=combined_metrics,
          sub_template=sub_template,
          considered_gt=combined_considered_gt,
      )
      merged_results.append(merged_result_data)
    return merged_results
