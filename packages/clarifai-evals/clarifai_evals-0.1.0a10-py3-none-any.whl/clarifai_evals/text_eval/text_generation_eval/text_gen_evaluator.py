from typing import Dict, List, Tuple

from clarifai_grpc.grpc.api import resources_pb2
from joblib import Parallel, delayed

from clarifai_evals.constant import DEFAULT_BATCH_SIZE, DEFAULT_TEXT_GEN_JUDGE_LLM_URL, TaskTypes
from clarifai_evals.result_data import (MetricResult, ResultData, ResultResponse,
                                        transform_result_to_proto)
from clarifai_evals.text_eval.base_eval import BaseTextEvaluator
from clarifai_evals.text_eval.text_generation_eval.context_aware_eval.evaluate import (
    TextGenContextRelevanceEvaluator, TextGenContextUtilizationEvaluator,
    TextGenFactualAccuracyEvaluator, TextGenResponseConsistencyEvaluator)
from clarifai_evals.text_eval.text_generation_eval.eval_with_gt.evaluate import (
    TextGenExactMatchEvaluator, TextGenMatchEvaluator, TextGenRougeEvaluator)
from clarifai_evals.text_eval.text_generation_eval.response_quality_eval.evaluate import (
    TextGenCompletenessEvaluator, TextGenConcisenessEvaluator, TextGenRelevanceEvaluator,
    TextGenValidityEvaluator)


class TextGenerationEvaluator(BaseTextEvaluator):
  """This class is used to evaluate text classification models"""

  def __init__(
      self,
      clarifai_pat: str,
      clarifai_model_url: str = DEFAULT_TEXT_GEN_JUDGE_LLM_URL,
      batch_size: int = DEFAULT_BATCH_SIZE,
  ):
    all_metrics = {
        "with_gt": {
            "response_match": TextGenMatchEvaluator,
            "rouge": TextGenRougeEvaluator,
            "exact_match": TextGenExactMatchEvaluator,
        },
        "quality_eval": {
            "completeness": TextGenCompletenessEvaluator,
            "relevance": TextGenRelevanceEvaluator,
            "conciseness": TextGenConcisenessEvaluator,
            "validity": TextGenValidityEvaluator,
        },
        "context_eval": {
            "context_relevance": TextGenContextRelevanceEvaluator,
            "context_utilization": TextGenContextUtilizationEvaluator,
            "factual_accuracy": TextGenFactualAccuracyEvaluator,
            "response_consistency": TextGenResponseConsistencyEvaluator,
        },
    }
    quick_metrics = {
        "quality_eval": {
            "completeness": TextGenCompletenessEvaluator,
            "relevance": TextGenRelevanceEvaluator,
            "conciseness": TextGenConcisenessEvaluator,
            "validity": TextGenValidityEvaluator,
        }
    }
    super().__init__(
        description="Text Generation Evaluator",
        task_type=TaskTypes.text_generation,
        all_metrics=all_metrics,
        quick_metrics=quick_metrics,
        batch_size=batch_size,
    )
    self.clarifai_pat = clarifai_pat
    self.clarifai_model_url = clarifai_model_url

  def evaluate(
      self,
      prediction_batch: List[resources_pb2.Data],
      query_batch: List[resources_pb2.Data],
      ground_truth_batch: List[resources_pb2.Data] = None,
      context_batch: List[resources_pb2.Data] = None,
      sub_template="all",
      mode: str = "detailed",
  ) -> Dict:
    """This method evaluates the model based on the given inputs
        Args:
            prediction_batch (List[resources_pb2.Data]): A list of lists containing the predictions with confidence scores or one-hot encoding
            ground_truth_batch (List[resources_pb2.Data]): A list of lists containing the ground truth labels if available
            query_batch (resources_pb2.Data): A list of queries if ground truth is not available
            context_batch (resources_pb2.Data): A list of contexts if available
            sub_template (str): The sub_template to evaluate
            mode (str): The mode of evaluation, eg: detailed, quick
        Returns:
            ResultResponse: The evaluation results
        """
    # accept one-hot ground_truth_batch
    self._verify_inputs(
        prediction_batch,
        query_batch,
        ground_truth_batch,
        context_batch,
        sub_template,
        mode,
    )
    _prediction_batch, _query_batch, _ground_truth_batch, context_batch = self._transform_inputs(
        prediction_batch, query_batch, ground_truth_batch, context_batch)

    static_argsdict = {"sub_template": sub_template, "mode": mode}
    final_result = self._parallel_evaluate(
        callback_fn=self._evaluate_batch,
        prediction_batch=_prediction_batch,
        static_argsdict=static_argsdict,
        query_batch=_query_batch,
        ground_truth_batch=_ground_truth_batch,
        context_batch=context_batch)
    final_result.provided_gts = ground_truth_batch
    final_result.provided_inputs = query_batch
    final_result.provided_predictions = prediction_batch

    return transform_result_to_proto(final_result, self.task_type)

  def _evaluate_batch(self, prediction_batch: List, static_argsdict,
                      **batch_args) -> List[ResultResponse]:
    """This method evaluates the model based on the given batch
        Args:
            prediction_batch (List): The list of predictions
            static_argsdict (Dict): A dictionary containing the static arguments like sub_template and mode
            batch_args (Dict): A dictionary containing the batch arguments like prediction_batch, ground_truth_batch, query_batch, context_batch
        Returns:
            List[ResultResponse]: The evaluation results
        """
    results_batch = ResultResponse(gt_results=[], judge_results=[], provided_predictions=[])
    mode = static_argsdict.get('mode', 'detailed')
    sub_template = static_argsdict.get('sub_template', 'all')
    ground_truth_batch = batch_args.get('ground_truth_batch', None)
    context_batch = batch_args.get('context_batch', None)
    query_batch = batch_args.get('query_batch', None)

    if mode == "detailed":
      if sub_template in ["all", "with_gt"] and ground_truth_batch is not None:
        results_batch.gt_results.append(
            self._evaluate_with_gt(ground_truth_batch, query_batch, prediction_batch, mode))
      if sub_template in ["all", "quality_eval"]:
        results_batch.judge_results.append(
            self._evaluate_quality(prediction_batch, query_batch, context_batch, mode))
      if sub_template in ["all", "context_eval"] and context_batch is not None:
        results_batch.judge_results.append(
            self._evaluate_context(prediction_batch, query_batch, context_batch, mode))
    elif mode == "quick":
      if sub_template in ["all", "quality_eval"]:
        results_batch.judge_results.append(
            self._evaluate_quality(prediction_batch, query_batch, context_batch, mode))

    return results_batch

  def _evaluate_with_gt(
      self,
      prediction_batch: List[str],
      query_batch: List[str],
      ground_truth_batch: List[str] = None,
      context_batch: List[str] = None,
      mode: str = "detailed",
  ) -> ResultData:
    """This method evaluates the model based on the given inputs when ground truth is available
        Args:
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
            predictions_dict (Dict): A dictionary of the predictions in the form of one-hot encoding, confidence scores and vector encoding
            query_batch (List): A list of queries
            context_batch (List): A list of contexts if available
            mode (str): The mode of evaluation, eg: detailed, quick
        Returns:
            ResultData: The evaluation results
        """
    metrics_batch = []
    if mode == "quick":
      metrics = self.quick_metrics["with_gt"]
    else:
      metrics = self.all_metrics["with_gt"]
    # Execute in parallel
    with Parallel(n_jobs=len(metrics.keys())) as parallel:
      metrics_batch = parallel(
          delayed(self._evaluate_gt_metric)(
              metric,
              prediction_batch,
              query_batch,
              ground_truth_batch,
              context_batch,
              mode == "detailed",
          ) for metric in metrics.keys())
    flat_metrics_batch = []
    for sublist in metrics_batch:
      if isinstance(sublist, list):
        flat_metrics_batch.extend(sublist)
      else:
        flat_metrics_batch.append(sublist)
    results_batch = ResultData(
        metrics_results=flat_metrics_batch,
        sub_template="with_gt",
    )
    return results_batch

  def _evaluate_quality(
      self,
      prediction_batch: List[str],
      query_batch: List[str],
      context_batch: List[str] = None,
      mode="detailed",
  ) -> ResultData:
    """This method evaluates the model based on the given inputs when ground truth is not available
        Args:
            prediction_dict (Dict): A dictionary containing the predictions in the form of one-hot encoding, confidence scores and vector encoding
            query_batch (List): A list of queries
            context_batch (List): A list of contexts if available
            mode (str): The mode of evaluation, eg: detailed, quick
        Returns:
            ResultData: The evaluation results
        """
    mgrp = "quality_eval"
    if mode == "quick":
      metrics = self.quick_metrics[mgrp]
    else:
      metrics = self.all_metrics[mgrp]

    metrics_batch = []
    # Execute in parallel
    with Parallel(n_jobs=len(metrics.keys())) as parallel:
      metrics_batch = parallel(
          delayed(self._evaluate_nongt_metric)(
              mgrp,
              metric,
              prediction_batch,
              query_batch,
              context_batch,
              mode == "detailed",
          ) for metric in metrics.keys())
    results_batch = ResultData(metrics_results=metrics_batch, sub_template=mgrp)
    return results_batch

  def _evaluate_context(
      self,
      prediction_batch: List[str],
      query_batch: List[str],
      context_batch: List[str] = None,
      mode="detailed",
  ) -> ResultData:
    """This method evaluates the model based on the given inputs when ground truth is not available
        Args:
            prediction_dict (Dict): A dictionary containing the predictions in the form of one-hot encoding, confidence scores and vector encoding
            query_batch (List): A list of queries
            context_batch (List): A list of contexts if available
            mode (str): The mode of evaluation, eg: detailed, quick
        Returns:
            ResultData: The evaluation results
        """
    mgrp = "context_eval"
    if mode == "quick":
      metrics = self.quick_metrics[mgrp]
    else:
      metrics = self.all_metrics[mgrp]

    metrics_batch = []
    # Execute in parallel
    with Parallel(n_jobs=len(metrics.keys())) as parallel:
      metrics_batch = parallel(
          delayed(self._evaluate_nongt_metric)(
              mgrp,
              metric,
              prediction_batch,
              query_batch,
              context_batch,
              mode == "detailed",
          ) for metric in metrics.keys())
    results_batch = ResultData(metrics_results=metrics_batch, sub_template=mgrp)
    return results_batch

  def _evaluate_gt_metric(
      self,
      metric: str,
      prediction_batch: List[str],
      query_batch: List[str],
      ground_truth_batch: List[str],
      context_batch: List[str],
      graph: bool = False,
  ) -> MetricResult:
    """This method evaluates a single metric based on the given inputs when ground truth is available
        Args:
            metric (str): The metric to evaluate
            prediction_batch List[str]: A list of strings containing the predictions
            query_batch (List[str]): A list of queries
            ground_truth_batch (List[str]): A list of ground truth labels
            context_batch (List[str]): A list of contexts if available
            graph (bool): Whether to generate graph data or not
        Returns:
            MetricResult: The metric evaluation results
    """
    obj = self.all_metrics["with_gt"][metric](
        clarifai_pat=self.clarifai_pat, clarifai_model_url=self.clarifai_model_url)
    metric_scores, summary_scores, explanations = obj.evaluate(
        query_batch=query_batch,
        predictions_batch=prediction_batch,
        ground_truth_batch=ground_truth_batch,
        context_batch=context_batch)
    metric_results = None
    if graph:
      graph_data = obj.get_graph_data(metric_scores, ground_truth_batch, prediction_batch)
    if isinstance(metric_scores, dict):
      metric_results = []
      for key in metric_scores.keys():
        mrobj = MetricResult(
            metric_name=key,
            summary_score=summary_scores[key],
            persample_scores=metric_scores[key],
            persample_explanations=explanations[key] if explanations[key] else None,
            graph_data=graph_data[key] if graph_data else None,
            metric_info=obj.get_info(),
        )
        metric_results.append(mrobj)
    else:
      metric_results = MetricResult(
          metric_name=metric,
          summary_score=summary_scores,
          persample_scores=metric_scores,
          persample_explanations=explanations,
          graph_data=graph_data,
          metric_info=obj.get_info(),
      )
    return metric_results

  def _evaluate_nongt_metric(
      self,
      metric_grp: str,
      metric: str,
      prediction_batch: List[str],
      query_batch: List[str],
      context_batch: List[str] = None,
      graph: bool = False,
  ) -> ResultData:
    """This method evaluates a single metric based on the given inputs when ground truth is not available
        Args:
            metric_grp (str): The metric group to which the metric belongs
            metric (str): The metric to evaluate
            prediction_batch List[str]: A list of strings containing the predictions
            query_batch (List[str]): A list of queries
            context_batch (List[str]): A list of contexts if available
            graph (bool): Whether to generate graph data or not
        Returns:
            MetricResult: The metric evaluation results
    """
    obj = self.all_metrics[metric_grp][metric](
        clarifai_pat=self.clarifai_pat, clarifai_model_url=self.clarifai_model_url)
    metric_scores, summary_score, explanations = obj.evaluate(
        query_batch=query_batch, predictions_batch=prediction_batch, context_batch=context_batch)
    graph_data = None
    if graph:
      graph_data = obj.get_graph_data(metric_scores, prediction_batch)

    return MetricResult(
        metric_name=metric,
        summary_score=summary_score,
        persample_scores=metric_scores,
        persample_explanations=explanations,
        graph_data=graph_data,
        metric_info=obj.get_info(),
    )

  def _verify_inputs(
      self,
      prediction_batch: List[List],
      query_batch: List[str],
      ground_truth_batch: List[List],
      context_batch: List[str],
      sub_template: str,
      mode: str,
  ) -> None:
    """This method verifies the inputs before evaluation
        Args:
            prediction_batch (List[List]): A list of lists containing the predictions
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
            query_batch (List): A list of queries
            context_batch (List): A list of contexts
    """
    if sub_template not in list(self.all_metrics.keys()) + ["all"]:
      raise ValueError("Invalid sub_template. Must be one of: " +
                       str(list(self.all_metrics.keys()) + ["all"]))
    if mode not in ["detailed", "quick"]:
      raise ValueError("Invalid mode. Must be one of: detailed, quick")
    if mode == "quick" and sub_template not in ["all"] + list(self.quick_metrics.keys()):
      raise ValueError("Quick mode does not support the given sub_template")

    if len(prediction_batch) != len(query_batch):
      raise ValueError("prediction_batch and query_batch must have the same length")

    if ground_truth_batch is not None:
      if len(prediction_batch) != len(ground_truth_batch):
        raise ValueError("prediction_batch and ground_truth_batch must have the same length")

    if context_batch is not None:
      if len(prediction_batch) != len(context_batch):
        raise ValueError("prediction_batch and context_batch must have the same length")

  def get_metrics_info(self, gt_present: bool, mode: str = "detailed") -> Dict:
    """This method returns the information about the metrics
        Args:
            gt_present (bool): Whether ground truth is present or not
            mode (str): The mode of evaluation, eg: detailed, quick
        Returns:
            Dict: The information about the metrics
        """
    if mode == "detailed":
      metrics = self.all_metrics
    else:
      metrics = self.quick_metrics
    if gt_present:
      metrics = metrics["with_gt"]
    else:
      metrics = metrics["without_gt"]
    return {metric: metrics[metric]().get_info() for metric in metrics.keys()}

  def _transform_inputs(self,
                        prediction_batch: List[resources_pb2.Data],
                        query_batch: List[resources_pb2.Data],
                        ground_truth_batch: List[resources_pb2.Data] = None,
                        context_batch: List[resources_pb2.Data] = None
                       ) -> Tuple[List[str], List[str], List[str], List[str]]:
    """This method transforms the inputs to the required format
        Args:
            prediction_batch (List[resources_pb2.Data]): A list of lists containing the predictions with confidence scores or one-hot encoding
            ground_truth_batch (List[resources_pb2.Data]): A list of lists containing the ground truth labels if available
            query_batch (resources_pb2.Data): A list of queries if ground truth is not available
            context_batch (resources_pb2.Data): A list of contexts if available
        Returns:
            Tuple[List[str], List[str], List[str], List[str]]: The transformed inputs
    """
    preds_batch = [pred.text.raw for pred in prediction_batch]
    qry_batch = [query.text.raw for query in query_batch]
    gt_batch = None
    if ground_truth_batch is not None:
      gt_batch = [gt.text.raw for gt in ground_truth_batch]
    ctx_batch = None
    if context_batch is not None:
      ctx_batch = [ctx.text.raw for ctx in context_batch]
    return preds_batch, qry_batch, gt_batch, ctx_batch
