from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List

import numpy as np
from clarifai_grpc.grpc.api import resources_pb2
from google.protobuf.json_format import MessageToDict

from clarifai_evals.constant import TaskTypes
from clarifai_evals.image_eval.base_eval import BaseImageEvaluator
from clarifai_evals.image_eval.image_segmentation_eval.eval_with_gt.evaluate import (
    AccuracyEvaluator, DiceCoefficientEvaluator, F1ScoreEvaluator, IoUEvaluator,
    PrecisionEvaluator, RecallEvaluator, WeightedIoUEvaluator)
from clarifai_evals.image_eval.image_segmentation_eval.utils import (combine_masks,
                                                                     process_segmentation_proto)
from clarifai_evals.result_data import (MetricResult, ResultData, ResultResponse,
                                        transform_result_to_proto)


class ImageSegmentationEvaluator(BaseImageEvaluator):
  """This class is used to trigger evaluations for image segmentation tasks"""

  def __init__(
      self,
      batch_size: int = 32,
  ):
    all_metrics = {
        "with_gt": {
            "iou": IoUEvaluator,
            "dice": DiceCoefficientEvaluator,
            "weighted_iou": WeightedIoUEvaluator,
            "accuracy": AccuracyEvaluator,
            "precision": PrecisionEvaluator,
            "recall": RecallEvaluator,
            "f1": F1ScoreEvaluator,
        },
    }
    super().__init__(
        description="Image Segmentation Evaluator",
        task_type=TaskTypes.image_segmentation,
        all_metrics=all_metrics,
        batch_size=batch_size,
    )

  def evaluate(self, ground_truth_batch: List[resources_pb2.Annotation],
               prediction_batch: List[resources_pb2.Output],
               input_list: List[resources_pb2.Input]) -> ResultResponse:
    """This method evaluates the Image segmentation models based on the given inputs
            Args:
                ground_truth_batch (List[resources_pb2.Data]): A list of Data containing the ground truth masks
                prediction_batch (List[resources_pb2.Data]): A list of Data containing the predicted masks
                input_list (List[resources_pb2.Input]): A list of Input containing the image details
            Returns:
                ResultResponse: The evaluation results
            """
    _ground_truth_batch, _prediction_batch, _input_list = self._transform_inputs(
        ground_truth_batch, prediction_batch, input_list)
    gathered_results = self._parallel_evaluate(
        callback_fn=self._evaluate_batch,
        prediction_batch=_prediction_batch,
        static_argsdict={'input_list': _input_list,
                         'ground_truth_batch': _ground_truth_batch},
    )
    order_id = [input_id.id for input_id in input_list]
    for metric in gathered_results[0].metrics_results:
      if metric.persample_scores:  # Checks if not empty
        metric.persample_scores = [metric.persample_scores[k] for k in order_id]

    ground_truth_batch = [annotation.data for annotation in ground_truth_batch]
    prediction_batch = [outputs.data for outputs in prediction_batch]

    response = ResultResponse(
        provided_predictions=prediction_batch,
        provided_gts=ground_truth_batch,
        gt_results=gathered_results)
    return transform_result_to_proto(response, self.task_type)

  def _evaluate_batch(self, prediction_batch: List, static_argsdict, **batch_args) -> ResultData:
    """This method evaluates the model based on the given inputs
            Args:
                prediction_batch (List): A list of Data containing the predictions with confidence scores or one-hot encoding
                static_argsdict (Dict): A dictionary containing the static arguments
                batch_args (Dict): A dictionary containing the batch arguments
            Returns:
                ResultData: The evaluation results
    """
    input_list = static_argsdict.get('input_list', None)
    ground_truth_batch = static_argsdict.get('ground_truth_batch', None)

    # Part : 1 Process the ground truth and prediction masks
    ground_truth_mask, prediction_mask = process_segmentation_proto(input_list, ground_truth_batch,
                                                                    prediction_batch)

    # Process the ground truth and prediction masks in parallel
    args_list = []
    for image_id, gt_list in ground_truth_mask.items():
      pred_list = prediction_mask.get(image_id, [])
      args_list.append((image_id, gt_list, pred_list))

    results = {}
    with ProcessPoolExecutor(max_workers=10) as executor:
      futures = {executor.submit(_evaluate, args): args[0] for args in args_list}
      for future in as_completed(futures):
        image_id, result = future.result()
        results[image_id] = result

    # Part : 2 Aggregate the results
    weighted_iou = WeightedIoUEvaluator().evaluate(iou_per_class=results)
    aggregate_metrics(results, 'iou')
    dice = aggregate_metrics(results, 'dicecoefficient')
    accuracy = aggregate_metrics(results, 'accuracy')
    precision = aggregate_metrics(results, 'precision')
    recall = aggregate_metrics(results, 'recall')

    f1_score = MetricResult(
        metric_name="f1",
        summary_score=(F1ScoreEvaluator().evaluate(precision.summary_score, recall.summary_score)),
        perclass_scores=(F1ScoreEvaluator().evaluate(precision.perclass_scores,
                                                     recall.perclass_scores)),
        persample_scores=(F1ScoreEvaluator().evaluate(precision.persample_scores,
                                                      recall.persample_scores)))

    result_data = ResultData(
        metrics_results=[dice, weighted_iou, accuracy, precision, recall, f1_score],
        sub_template="with_gt",
        considered_gt=ground_truth_mask,
    )

    return [result_data]

  def _transform_inputs(self, ground_truth_batch: List[resources_pb2.Annotation],
                        prediction_batch: List[resources_pb2.Output],
                        input_list: List[resources_pb2.Input]) -> List:
    """This method transforms the inputs to the required format
        Args:
            ground_truth_batch (List[resources_pb2.Annotation]): A list of Data containing the ground truth masks
            prediction_batch (List[resources_pb2.Output]): A list of Data containing the predicted masks
            input_list (List[resources_pb2.Input]): A list of Input containing the image details

        Returns:
            List: The transformed inputs
    """

    return ([MessageToDict(ground_truth_batch[i]) for i in range(len(ground_truth_batch))],
            [MessageToDict(prediction_batch[i]) for i in range(len(prediction_batch))],
            [MessageToDict(input_list[i]) for i in range(len(input_list))])


def _evaluate(args: List) -> Dict:
  """Processes the ground truth and prediction masks and computes the metrics for single input(image)
    Args:
        args (List): A list containing the image ID, ground truth masks and prediction masks per input."""

  image_id, gt_list, pred_list = args
  result = {}

  # Collect ground truth masks per class
  gt_masks_per_class = {}
  for gt_dict in gt_list:
    for class_label, masks in gt_dict.items():
      if class_label not in gt_masks_per_class:
        gt_masks_per_class[class_label] = []
      gt_masks_per_class[class_label].extend(masks)

  # Combine ground truth masks per class
  for class_label in gt_masks_per_class:
    gt_masks_per_class[class_label] = combine_masks(gt_masks_per_class[class_label])

  # Collect prediction masks per class
  pred_masks_per_class = {}
  for pred_dict in pred_list:
    for class_label, masks in pred_dict.items():
      if class_label not in pred_masks_per_class:
        pred_masks_per_class[class_label] = []
      pred_masks_per_class[class_label].extend(masks)

  # Combine prediction masks per class
  for class_label in pred_masks_per_class:
    pred_masks_per_class[class_label] = combine_masks(pred_masks_per_class[class_label])

  # Initialize metrics for the current image ID
  result['iou'] = {}
  result['dicecoefficient'] = {}
  result['accuracy'] = {}
  result['precision'] = {}
  result['recall'] = {}

  # Calculate metrics for each class
  for class_label, gt_mask in gt_masks_per_class.items():
    pred_mask = pred_masks_per_class.get(class_label, np.zeros_like(gt_mask))

    if pred_mask.any():
      iou = IoUEvaluator().evaluate(ground_truth=gt_mask, predictions=pred_mask)
      result['iou'][class_label] = iou

      dice_coefficient = DiceCoefficientEvaluator().evaluate(
          ground_truth=gt_mask, predictions=pred_mask)
      result['dicecoefficient'][class_label] = dice_coefficient

      accuracy = AccuracyEvaluator().evaluate(ground_truth=gt_mask, predictions=pred_mask)
      result['accuracy'][class_label] = accuracy

      precision = PrecisionEvaluator().evaluate(ground_truth=gt_mask, predictions=pred_mask)
      result['precision'][class_label] = precision

      recall = RecallEvaluator().evaluate(ground_truth=gt_mask, predictions=pred_mask)
      result['recall'][class_label] = recall

    else:
      # Else, No predictions for this class
      result['iou'][class_label] = 0.0
      result['dicecoefficient'][class_label] = 0.0
      result['accuracy'][class_label] = 0.0
      result['precision'][class_label] = 0.0
      result['recall'][class_label] = 0.0

  return image_id, result


def aggregate_metrics(results: Dict, metric: str) -> MetricResult:
  """Aggregate the metrics for the given metric type
            Args:
                results (Dict): The results dictionary.
                metric (str): The metric to aggregate.
            Returns:
                MetricResult: The aggregated
        """
  # Initialize dictionaries
  metric_per_class = defaultdict(list)
  metric_per_image = defaultdict(list)
  all_metrics = []

  for image_id, class_dict in results.items():
    for class_label, metric_value in class_dict[metric].items():
      # Handle tuple or single value
      if isinstance(metric_value, tuple):
        metric_val = metric_value[0]
      else:
        metric_val = metric_value
      #per-class Metrics
      metric_per_class[class_label].append(metric_val)
      #per-image Metricss
      metric_per_image[image_id].append(metric_val)
      # all Metrics
      all_metrics.append(metric_val)

  # Compute mean metric per class
  mean_metric_per_class = {}
  for class_label, metric_list_class in metric_per_class.items():
    mean_metric_class = np.mean(metric_list_class)
    mean_metric_per_class[class_label] = mean_metric_class

  # Compute mean metric per image
  mean_metric_per_image = {}
  for image_id, metric_list_image in metric_per_image.items():
    mean_metric_image = np.mean(metric_list_image)
    mean_metric_per_image[image_id] = mean_metric_image

  # Compute overall mean IoU
  overall_mean_metric = np.mean(all_metrics)

  return MetricResult(
      metric_name=metric,
      summary_score=overall_mean_metric,
      perclass_scores=mean_metric_per_class,
      persample_scores=mean_metric_per_image,
  )
