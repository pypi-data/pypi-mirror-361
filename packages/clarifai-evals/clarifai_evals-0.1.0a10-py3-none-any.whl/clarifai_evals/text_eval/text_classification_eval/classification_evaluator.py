from collections import OrderedDict
from typing import Dict, List, Tuple

import numpy as np
from clarifai_grpc.grpc.api import resources_pb2
from joblib import Parallel, delayed

from clarifai_evals.constant import TaskTypes
from clarifai_evals.result_data import (MetricResult, ResultData, ResultResponse,
                                        transform_result_to_proto)
from clarifai_evals.text_eval.base_eval import BaseTextEvaluator
from clarifai_evals.text_eval.text_classification_eval.eval_with_gt.evaluate import (
    TextLabelAccuracyGTEvaluator, TextLabelF1ScoreGTEvaluator, TextLabelPrecisionGTEvaluator,
    TextLabelRecallGTEvaluator, TextLabelROCAUCGTEvaluator)
from clarifai_evals.text_eval.text_classification_eval.eval_with_llm_as_judge.evaluate import \
    LLMJudgeTextClassificationEvaluator
from clarifai_evals.text_eval.utils import get_correctness, get_prediction_encodings


class TextClassificationEvaluator(BaseTextEvaluator):
  """This class is used to evaluate text classification models"""

  def __init__(
      self,
      available_labels: List[resources_pb2.Concept],
      batch_size: int = 32,
      clarifai_pat: str = None,
      clarifai_model_url: str = None,
  ):
    all_metrics = {
        "with_gt": {
            "accuracy": TextLabelAccuracyGTEvaluator,
            "precision": TextLabelPrecisionGTEvaluator,
            "recall": TextLabelRecallGTEvaluator,
            "f1": TextLabelF1ScoreGTEvaluator,
            "roc_auc": TextLabelROCAUCGTEvaluator,
        },
        "without_gt": {
            "llm-as-judge": LLMJudgeTextClassificationEvaluator
        },
    }
    quick_metrics = {
        "with_gt": {
            "accuracy": TextLabelAccuracyGTEvaluator,
            "precision": TextLabelPrecisionGTEvaluator,
            "recall": TextLabelRecallGTEvaluator,
        },
        "without_gt": {
            "llm-as-judge": LLMJudgeTextClassificationEvaluator
        },
    }
    super().__init__(
        description="Text Classification Evaluator",
        task_type=TaskTypes.text_classification,
        all_metrics=all_metrics,
        quick_metrics=quick_metrics,
        batch_size=batch_size,
    )
    self.available_labels = [concept.id for concept in available_labels]
    self.available_labels.sort()
    self.clarifai_pat = clarifai_pat
    self.clarifai_model_url = clarifai_model_url

  def evaluate(
      self,
      prediction_batch: List[resources_pb2.Data],
      ground_truth_batch: List[resources_pb2.Data] = None,
      query_batch: List[resources_pb2.Data] = None,
      context_batch: List[resources_pb2.Data] = None,
      mode: str = "detailed",
  ) -> ResultResponse:
    """This method evaluates the model based on the given inputs
        Args:
            prediction_batch (List[resources_pb2.Data]): A list of Data containing the predictions with confidence scores or one-hot encoding
            ground_truth_batch (List[resources_pb2.Data]): A list of Data containing the ground truth labels if available
            query_batch (List[resources_pb2.Data]): A list of queries if ground truth is not available
            context_batch (List[resources_pb2.Data]): A list of contexts if available
            mode (str): The mode of evaluation, eg: detailed, quick
        Returns:
            ResultResponse: The evaluation results
        """
    self._verify_inputs(prediction_batch, ground_truth_batch, query_batch, context_batch)
    _prediction_batch, _ground_truth_batch, _query_batch, context_batch = self._transform_inputs(
        prediction_batch, ground_truth_batch, query_batch, context_batch)
    static_argsdict = {"mode": mode}
    gathered_result = self._parallel_evaluate(
        callback_fn=self.evaluate_batch,
        prediction_batch=_prediction_batch,
        static_argsdict=static_argsdict,
        ground_truth_batch=_ground_truth_batch,
        query_batch=_query_batch,
        context_batch=context_batch)
    gathered_result = self._re_aggregate_scores(gathered_result, _prediction_batch,
                                                _ground_truth_batch)
    if ground_truth_batch is not None:
      final_result = ResultResponse(
          provided_predictions=prediction_batch,
          provided_gts=ground_truth_batch,
          provided_inputs=query_batch,
          gt_results=gathered_result)
    else:
      final_result = ResultResponse(
          provided_predictions=prediction_batch,
          provided_gts=None,
          provided_inputs=query_batch,
          judge_results=gathered_result)
    return transform_result_to_proto(final_result, self.task_type)

  def evaluate_batch(self, prediction_batch: List, static_argsdict,
                     **batch_args) -> List[ResultData]:
    """This method evaluates the model based on the given inputs
        Args:
            prediction_batch (List): The list of predictions
            static_argsdict (Dict): The static arguments which are common to all batches like mode, sub_template, etc.
            **batch_args: The batch arguments like prediction_batch, ground_truth_batch, query_batch, context_batch, etc.
        Returns:
            List[ResultData]: The evaluation results
        """
    mode = static_argsdict.get("mode", "detailed")
    ground_truth_batch = batch_args.get("ground_truth_batch", None)
    query_batch = batch_args.get("query_batch", None)
    context_batch = batch_args.get("context_batch", None)
    predictions_dict = get_prediction_encodings(prediction_batch, self.available_labels)
    if ground_truth_batch is not None:
      _ground_truth_batch = np.array(ground_truth_batch)
      return self._evaluate_with_gt(_ground_truth_batch, predictions_dict, mode)
    return self._evaluate_without_gt(predictions_dict, query_batch, context_batch, mode)

  def _evaluate_with_gt(
      self,
      ground_truth_batch: List[List],
      predictions_dict: Dict,
      mode: str = "detailed",
  ) -> List[ResultData]:
    """This method evaluates the model based on the given inputs when ground truth is available
        Args:
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
            predictions_dict (Dict): A dictionary of the predictions in the form of one-hot encoding, confidence scores and vector encoding
            mode (str): The mode of evaluation, eg: detailed, quick
            Returns:
            List[ResultData]: The evaluation results
        """
    correctness = get_correctness(ground_truth_batch, predictions_dict["onehot_encoding"])
    metrics_batch = []
    if mode == "quick":
      metrics = self.quick_metrics["with_gt"]
    else:
      metrics = self.all_metrics["with_gt"]
    # Execute in parallel
    metrics_batch = Parallel(n_jobs=len(metrics.keys()))(delayed(self._evaluate_gt_metric)(
        ground_truth_batch,
        predictions_dict,
        metric,
        mode == "detailed",
    ) for metric in metrics.keys())
    results_batch = ResultData(
        considered_gt=None,
        correctness=correctness,
        metrics_results=metrics_batch,
        sub_template="with_gt",
    )
    return [results_batch]

  def _evaluate_without_gt(
      self,
      prediction_dict: Dict,
      query_batch: List,
      context_batch: List[str] = None,
      mode="detailed",
  ) -> List[ResultData]:
    """This method evaluates the model based on the given inputs when ground truth is not available
        Args:
            prediction_dict (Dict): A dictionary containing the predictions in the form of one-hot encoding, confidence scores and vector encoding
            query_batch (List): A list of queries
            context_batch (List): A list of contexts if available
            mode (str): The mode of evaluation, eg: detailed, quick
        Returns:
            List[ResultData]: The evaluation results
        """
    if mode == "quick":
      metrics = self.quick_metrics["without_gt"]
    else:
      metrics = self.all_metrics["without_gt"]
    result_obj = self._evaluate_nongt_metric(
        prediction_dict,
        query_batch,
        list(metrics.keys())[0],
        context_batch,
        mode == "detailed",
    )
    return [result_obj]

  def _evaluate_gt_metric(
      self,
      ground_truth_batch: List[List],
      predictions_dict: Dict,
      metric: str,
      graph: bool = False,
  ) -> MetricResult:
    """This method evaluates a single metric based on the given inputs when ground truth is available
        Args:
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
            predictions_dict (Dict): A dictionary containing the predictions in the form of one-hot encoding, confidence scores and vector encoding
            metric (str): The metric to evaluate
        Returns:
            MetricResult: The metric evaluation results
        """
    metric_obj = self.all_metrics["with_gt"][metric]()
    perclass_scores, summary_score, persample_scores = metric_obj.evaluate(
        ground_truth_batch, predictions_dict)
    perclass_scores = OrderedDict({
        label: score
        for label, score in zip(self.available_labels, perclass_scores)
    }) if perclass_scores is not None else None
    graph_data = None
    if graph:
      graph_data = metric_obj.get_graph_data(ground_truth_batch, predictions_dict)
    return MetricResult(
        metric_name=metric,
        summary_score=summary_score,
        perclass_scores=perclass_scores,
        persample_scores=persample_scores,
        graph_data=graph_data,
        metric_info=metric_obj.get_info(),
    )

  def _evaluate_nongt_metric(
      self,
      prediction_dict: Dict,
      query_batch: List[str],
      metric: str,
      context_batch: List[str] = None,
      graph: bool = False,
  ) -> ResultData:
    """This method evaluates a single metric based on the given inputs when ground truth is not available
        Args:
            prediction_dict (Dict): A dictionary containing the predictions in the form of one-hot encoding, confidence scores and vector encoding
            query_batch (List): A list of queries
            context_batch (List): A list of contexts if available
            metric (str): The metric to evaluate
        Returns:
            ResultData: The metric name and the evaluation results
        """
    obj = self.all_metrics["without_gt"][metric](
        clarifai_pat=self.clarifai_pat, clarifai_model_url=self.clarifai_model_url)
    judge_preds, per_sample_score, perclass_scores, summary_score = obj.evaluate(
        prediction_dict, self.available_labels, query_batch, context_batch)
    perclass_scores = OrderedDict(
        {label: score
         for label, score in zip(self.available_labels, perclass_scores)})
    graph_data = None
    if graph:
      graph_data = obj.get_graph_data(judge_preds, prediction_dict)
    metric_obj = MetricResult(
        metric_name="accuracy",
        summary_score=summary_score,
        persample_scores=per_sample_score,
        perclass_scores=perclass_scores,
        graph_data=graph_data,
        metric_info=obj.get_info(),
    )
    return ResultData(
        considered_gt=judge_preds,
        correctness=None,
        metrics_results=[metric_obj],
        sub_template="without_gt",
    )

  def _verify_inputs(
      self,
      prediction_batch: List[resources_pb2.Data],
      ground_truth_batch: List[resources_pb2.Data],
      query_batch: List[resources_pb2.Data],
      context_batch: List[resources_pb2.Data],
  ) -> None:
    """This method verifies the inputs before evaluation
        Args:
            prediction_batch (List[resources_pb2.Data]): A list of Data containing the predictions with confidence scores
            ground_truth_batch (List[resources_pb2.Data]): A list of Data containing the ground truth labels if available
            query_batch (List[resources_pb2.Data]): A list of queries if ground truth is not available
            context_batch (List[resources_pb2.Data]): A list of contexts if available
        """
    if ground_truth_batch is not None:
      if len(prediction_batch) != len(ground_truth_batch):
        raise ValueError("prediction_batch and ground_truth_batch must have the same length")
      if query_batch and len(ground_truth_batch) != len(query_batch):
        raise ValueError("ground_truth_batch and query_batch must have the same length")
    else:
      if len(prediction_batch) != len(query_batch):
        raise ValueError("prediction_batch and query_batch must have the same length")
    if context_batch is not None:
      if len(prediction_batch) != len(context_batch):
        raise ValueError("prediction_batch and context_batch must have the same length")

  def _transform_inputs(
      self,
      prediction_batch: List[resources_pb2.Data],
      ground_truth_batch: List[resources_pb2.Data] = None,
      query_batch: List[resources_pb2.Data] = None,
      context_batch: List[resources_pb2.Data] = None,
  ) -> Tuple[List[List], List[List], List[str], List[str]]:
    """This method transforms the inputs to the required format
        Args:
            prediction_batch (List[resources_pb2.Data]): A list of Data containing the predictions with confidence scores
            ground_truth_batch (List[resources_pb2.Data]): A list of Data containing the ground truth labels if available
            query_batch (List[resources_pb2.Data]): A list of queries if ground truth is not available
            context_batch (List[resources_pb2.Data]): A list of contexts if available
        Returns:
            Tuple[List[List], List[List], List[str], List[str]]: The transformed inputs
        """
    pred_batch = []
    label_idx_map = {label: idx for idx, label in enumerate(self.available_labels)}
    for pred in prediction_batch:
      pred_scores = [0] * len(self.available_labels)
      for concept in pred.concepts:
        pred_scores[label_idx_map[concept.id]] = round(concept.value, 3)
      pred_batch.append(pred_scores)

    gt_batch = None
    if ground_truth_batch:
      gt_batch = []
      for gt in ground_truth_batch:
        gt_labels = [0] * len(self.available_labels)
        for concept in gt.concepts:
          gt_labels[label_idx_map[concept.id]] = round(concept.value, 3)
        gt_batch.append(gt_labels)

    qry_batch = None
    if query_batch:
      qry_batch = [query.text.raw for query in query_batch]

    cntxt_batch = None
    if context_batch:
      cntxt_batch = [context.text.raw for context in context_batch]

    return pred_batch, gt_batch, qry_batch, cntxt_batch

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

  def _re_aggregate_scores(self, results: List[ResultData], prediction_batch: List[List],
                           ground_truth_batch: List[List]) -> ResultData:
    """This method is used to re-aggregate the scores if needed
        Args:
            results (List[ResultData]): The evaluation results
            prediction_batch (List[List]): A list of lists containing the predictions
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
        Returns:
            ResultData: The re-aggregated evaluation results
    """
    predictions_dict = get_prediction_encodings(prediction_batch, self.available_labels)
    done = False
    for result_idx, result in enumerate(results):
      if result.sub_template == "with_gt":
        for metric_idx, metric in enumerate(result.metrics_results):
          if metric.metric_name == "roc_auc":
            results[result_idx].metrics_results[metric_idx] = self._evaluate_gt_metric(
                ground_truth_batch, predictions_dict, "roc_auc", False)
            done = True
            break
      if done:
        break
    return results
