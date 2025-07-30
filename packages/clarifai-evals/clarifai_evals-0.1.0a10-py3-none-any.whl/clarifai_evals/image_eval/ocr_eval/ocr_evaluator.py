from itertools import chain
from typing import Dict, List, Tuple

from clarifai_grpc.grpc.api import resources_pb2
from joblib import Parallel, delayed

from clarifai_evals.constant import TaskTypes
from clarifai_evals.image_eval.base_eval import BaseImageEvaluator
from clarifai_evals.image_eval.ocr_eval.eval_with_gt.evaluate import (
    ComputeCharacterErrorRates, ComputeClassicalMetrics, ComputeSemanticSimilarity,
    ComputeWordErrorRates)
from clarifai_evals.result_data import (MetricResult, ResultData, ResultResponse,
                                        transform_result_to_proto)


class OCREvaluator(BaseImageEvaluator):
  """This class is used to evaluate OCR models"""

  def __init__(
      self,
      clarifai_pat: str,
      clarifai_model_url:
      str = "https://clarifai.com/hapxpu3a2wn7/sentence-transformers-embedding/models/sentence-transformers-embedding",
      batch_size: int = 32,
  ):
    all_metrics = {
        "with_gt": {
            "word_error_rate": ComputeWordErrorRates,
            "character_error_rate": ComputeCharacterErrorRates,
            "semantic_similarity": ComputeSemanticSimilarity,
            "classical_metrics": ComputeClassicalMetrics,
        }
    }
    super().__init__(
        description="Text Classification Evaluator",
        task_type=TaskTypes.image_ocr,
        all_metrics=all_metrics,
        batch_size=batch_size,
    )
    self.clarifai_pat = clarifai_pat
    self.clarifai_model_url = clarifai_model_url

  def evaluate(self,
               prediction_batch: List[resources_pb2.Data],
               ground_truth_batch: List[resources_pb2.Data] = None) -> ResultResponse:
    """This method evaluates the model based on the given inputs
        Args:
            prediction_batch (List[resources_pb2.Data]): A list of Data containing the predictions with confidence scores or one-hot encoding
            ground_truth_batch (List[resources_pb2.Data]): A list of Data containing the ground truth labels if available
        Returns:
            ResultResponse: The evaluation results
        """
    self._verify_inputs(prediction_batch, ground_truth_batch)
    _prediction_batch, _ground_truth_batch = self._transform_inputs(prediction_batch,
                                                                    ground_truth_batch)
    gathered_result = self._parallel_evaluate(
        callback_fn=self._evaluate_batch,
        prediction_batch=_prediction_batch,
        static_argsdict={},
        ground_truth_batch=_ground_truth_batch)
    final_result = ResultResponse(
        provided_predictions=prediction_batch,
        provided_gts=ground_truth_batch,
        gt_results=gathered_result)
    return transform_result_to_proto(final_result, self.task_type)

  def _evaluate_batch(self, prediction_batch: List, static_argsdict: Dict,
                      **batch_args) -> List[ResultData]:
    """
    This method evaluates the model based on the given inputs
    Args:
        prediction_batch (List): The list of predictions
        static_argsdict (Dict): The static arguments which are common to all batches like mode, sub_template, etc.
        **batch_args: The batch arguments like prediction_batch, ground_truth_batch, query_batch, context_batch, etc.
    Returns:
        List[ResultData]: The evaluation results
    """
    ground_truth_batch = batch_args.get("ground_truth_batch", None)
    result = self._evaluate_with_gt(ground_truth_batch, prediction_batch)
    return [result]

  def _evaluate_with_gt(self, ground_truth_batch: List[str],
                        predictions_batch: List[str]) -> ResultData:
    """This method evaluates the model based on the given inputs when ground truth is available
        Args:
            ground_truth_batch (List[str]): A list of ground truth texts
            predictions_dict (List[str]): A list of predicted texts
        Returns:
            ResultData: The evaluation results
        """
    metrics_batch = []
    metrics = self.all_metrics["with_gt"]
    metrics_batch = Parallel(n_jobs=len(metrics.keys()))(delayed(self._evaluate_gt_metric)(
        ground_truth_batch,
        predictions_batch,
        metric,
    ) for metric in metrics.keys())
    flatten_metrics_batch = list(chain.from_iterable(metrics_batch))
    return ResultData(
        metrics_results=flatten_metrics_batch,
        sub_template="with_gt",
    )

  def _evaluate_gt_metric(
      self,
      predictions_batch: List[str],
      ground_truth_batch: List[str],
      metric: str,
      graph: bool = False,
  ) -> List[MetricResult]:
    """This method evaluates a single metric based on the given inputs when ground truth is available
        Args:
            ground_truth_batch (List[str]): A list of ground truth texts
            predictions_dict (List[str]): A list of predicted texts
            metric (str): The metric to evaluate
        Returns:
            Tuple[str, MetricResult]: The metric name and the evaluation results
        """
    metric_obj = self.all_metrics["with_gt"][metric](
        pat=self.clarifai_pat, embedding_model=self.clarifai_model_url)
    summary_scores, persample_scores = metric_obj.evaluate(
        predictions=predictions_batch, ground_truth=ground_truth_batch)
    graph_data = None
    if graph:
      graph_data = metric_obj.get_graph_data(ground_truth_batch, predictions_batch)
    metric_result_list = []
    for metric in summary_scores.keys():
      metric_result_list.append(
          MetricResult(
              metric_name=metric,
              summary_score=summary_scores[metric],
              persample_scores=persample_scores[metric],
              graph_data=graph_data,
              metric_info=metric_obj.get_info()))
    return metric_result_list

  def _verify_inputs(self, prediction_batch: List[resources_pb2.Data],
                     ground_truth_batch: List[resources_pb2.Data]) -> None:
    """This method verifies the inputs before evaluation
        Args:
            prediction_batch (List[resources_pb2.Data]): A list of Data containing the predictions with confidence scores
            ground_truth_batch (List[resources_pb2.Data]): A list of Data containing the ground truth labels if available
        """
    if len(prediction_batch) == 0:
      raise ValueError("prediction_batch cannot be empty")
    if ground_truth_batch is not None:
      if len(prediction_batch) != len(ground_truth_batch):
        raise ValueError("prediction_batch and ground_truth_batch must have the same length")

  def _transform_inputs(
      self,
      prediction_batch: List[resources_pb2.Data],
      ground_truth_batch: List[resources_pb2.Data] = None) -> Tuple[List[List], List[List]]:
    """This method transforms the inputs to the required format
        Args:
            prediction_batch (List[resources_pb2.Data]): A list of Data containing the predictions with confidence scores
            ground_truth_batch (List[resources_pb2.Data]): A list of Data containing the ground truth labels if available
        Returns:
            Tuple[List[List], List[List], List[str], List[str]]: The transformed inputs
        """

    def extract_text(detection):
      all_text = []
      if detection.regions is None or len(detection.regions) == 0 and detection.text:
        return detection.text.raw.lower()
      for region in detection.regions:
        all_text.append(region.data.text.raw.lower())
      return " ".join(all_text)

    try:
      transformed_prediction_batch = [extract_text(detection) for detection in prediction_batch]
    except Exception:
      transformed_prediction_batch = [detection.text.raw.lower() for detection in prediction_batch]

    try:
      transformed_ground_truth_batch = [
          extract_text(detection) for detection in ground_truth_batch
      ] if ground_truth_batch is not None else None
    except Exception:
      transformed_ground_truth_batch = [
          detection.text.raw.lower() for detection in ground_truth_batch
      ] if ground_truth_batch is not None else None

    return transformed_prediction_batch, transformed_ground_truth_batch

  def get_metrics_info(self, gt_present: bool = True) -> Dict:
    """This method returns the information about the metrics
        Args:
            gt_present (bool): Whether ground truth is present or not
        Returns:
            Dict: The information about the metrics
        """
    if gt_present:
      return {
          metric: self.all_metrics["with_gt"][metric]().get_info()
          for metric in self.all_metrics["with_gt"].keys()
      }
    else:
      return None
