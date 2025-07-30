from random import randint
from typing import List, Tuple

import fiftyone as fo
from clarifai_grpc.grpc.api import resources_pb2

from clarifai_evals.constant import TaskTypes
from clarifai_evals.image_eval.base_eval import BaseImageEvaluator
from clarifai_evals.image_eval.image_detection_eval.eval_with_gt.evaluate import (
    AccuracyDetectionGTEvaluator, FNDetectionGTEvaluator, FODetectionGTEvaluator,
    FPDetectionGTEvaluator, FScoreDetectionGTEvaluator, IOUDetectionGTEvaluator,
    MAPDetectionGTEvaluator, PrecisionDetectionGTEvaluator, RecallDetectionGTEvaluator,
    SupportDetectionGTEvaluator, TPDetectionGTEvaluator)
from clarifai_evals.image_eval.image_utils import get_image_dimensions
from clarifai_evals.result_data import (MetricResult, ResultData, ResultResponse,
                                        transform_result_to_proto)


class ImageDetectionEvaluator(BaseImageEvaluator):
  """This class is used to evaluate object detection models"""

  def __init__(
      self,
      available_labels: List[resources_pb2.Concept],
      batch_size: int = 32,
      clarifai_pat: str = None,
  ):
    all_metrics = {
        "with_gt": {
            "accuracy": AccuracyDetectionGTEvaluator,
            "precision": PrecisionDetectionGTEvaluator,
            "recall": RecallDetectionGTEvaluator,
            "fscore": FScoreDetectionGTEvaluator,
            "support": SupportDetectionGTEvaluator,
            "true_positives": TPDetectionGTEvaluator,
            "false_negatives": FNDetectionGTEvaluator,
            "false_positives": FPDetectionGTEvaluator,
            "iou": IOUDetectionGTEvaluator,
            "map": MAPDetectionGTEvaluator,
        },
    }
    # quick_metrics = {}
    super().__init__(
        description="Object Detection Evaluator",
        task_type=TaskTypes.image_object_detection,
        all_metrics=all_metrics,
        batch_size=batch_size,
    )
    self.available_labels = [concept.id for concept in available_labels]
    self.available_labels.sort()
    self.clarifai_pat = clarifai_pat

  def evaluate(
      self,
      prediction_batch: List[resources_pb2.Data],
      input_batch: List[resources_pb2.Data],
      ground_truth_batch: List[resources_pb2.Data],
  ) -> ResultResponse:
    """This function is used to evaluate the predicted detections
        Args:
          image_dimensions: List of tuples containing the dimensions of each image in the batch (w,h)
          prediction_batch (List[resources_pb2.Data]): List of Data object containing the detection bboxes for each image in the batch
          ground_truth_batch (List[resources_pb2.Data]): List of Data object containing the ground truth bboxes for each image in the batch
        Returns:
          ResultResponse: The response of the evaluation
        """
    self._verify_inputs(input_batch, prediction_batch, ground_truth_batch)
    (
        image_dimensions,
        _prediction_batch,
        _ground_truth_batch,
    ) = self._transform_inputs(input_batch, prediction_batch, ground_truth_batch)
    gathered_result = self._parallel_evaluate(
        callback_fn=self._evaluate_batch,
        prediction_batch=_prediction_batch,
        static_argsdict={},
        image_dimensions=image_dimensions,
        ground_truth_batch=_ground_truth_batch,
    )
    response = ResultResponse(
        provided_predictions=prediction_batch,
        provided_gts=ground_truth_batch,
        gt_results=gathered_result,
    )
    return transform_result_to_proto(response, self.task_type)

  def _evaluate_batch(self, prediction_batch: List[List], static_argsdict,
                      **batch_args) -> List[ResultData]:
    """This function is used to evaluate the batch of predictions
        Args:
            prediction_batch: List of lists containing the detections for each image in the batch (x1,y1,x2,y2,label,confidence)
            static_argsdict: The static arguments which are common to all batches like mode, sub_template, inputs_list etc.
            **batch_args: The batch arguments like image_dimensions, prediction_batch, ground_truth_batch, etc.
        Returns:
            List[ResultData]: The results of the evaluation
        """
    image_dimensions = batch_args["image_dimensions"]
    ground_truth_batch = batch_args.get("ground_truth_batch", None)
    fo_dataset = self._create_dataset(image_dimensions, prediction_batch, ground_truth_batch)
    result = self._evaluate_with_gt(ground_truth_batch, prediction_batch, fo_dataset)
    return [result]

  def _evaluate_with_gt(self, ground_truth_batch: List, prediction_batch: List,
                        dataset: fo.Dataset) -> ResultData:
    """This function is used to evaluate the predictions against the ground truth
        Args:
            prediction_batch: List of lists containing the detections for each image in the batch (x1,y1,x2,y2,label,confidence)
            ground_truth_batch: List of lists containing the ground truth bboxes for each image in the batch (x1,y1,x2,y2,label)
            dataset: FiftyOne dataset containing the predictions and ground truth
        Returns:
            ResultData: The results of the evaluation
        """
    eval_obj = FODetectionGTEvaluator()
    results = eval_obj.evaluate(dataset)
    metric_names = list(self.all_metrics["with_gt"].keys())
    output = []
    for metric in metric_names:
      output.append(self._evaluate_gt_metric(dataset, results, metric))
    result_data = ResultData(
        metrics_results=output,
        sub_template="with_gt",
        considered_gt=ground_truth_batch,
    )
    return result_data

  def _evaluate_gt_metric(self, dataset, results, metric) -> MetricResult:
    """This function is used to evaluate the specified ground truth metric
        Args:
            dataset: FiftyOne dataset containing the predictions and ground truth
            results: The results of the evaluation
            metric: The metric to evaluate
        Returns:
            MetricResult: The results of the evaluation of the metric
        """
    obj = self.all_metrics["with_gt"][metric]()
    summary_score, perclass_scores, persample_scores, perobj_scores = obj.evaluate(
        dataset, results)
    graph_data = obj.get_graph_data(results)
    metric_result = MetricResult(
        metric_name=metric,
        summary_score=summary_score,
        perclass_scores=perclass_scores,
        persample_scores=persample_scores,
        perobject_scores=perobj_scores,
        graph_data=graph_data,
        metric_info=obj.get_info(),
    )
    return metric_result

  def _verify_inputs(
      self,
      input_batch: List[Tuple[int, int]],
      prediction_batch: List[resources_pb2.Data],
      ground_truth_batch: List[resources_pb2.Data],
  ):
    """This function is used to verify the inputs
        Args:
            input_batch: List of data objects containing the image or video data given as inputs to the model
            prediction_batch: List of lists containing the detections for each image in the batch (x1,y1,x2,y2,label,confidence)
            ground_truth_batch: List of lists containing the ground truth bboxes for each image in the batch (x1,y1,x2,y2,label)
        """
    if len(prediction_batch) != len(ground_truth_batch):
      raise ValueError("prediction_batch and ground_truth_batch must have the same length")
    if len(input_batch) != len(prediction_batch):
      raise ValueError("input_batch and prediction_batch must have the same length")
    if (not all(isinstance(detections, resources_pb2.Data) for detections in prediction_batch) or
        not all(isinstance(detections, resources_pb2.Data) for detections in ground_truth_batch) or
        not all(isinstance(detections, resources_pb2.Data) for detections in input_batch)):
      raise ValueError(
          "prediction_batch, ground_truth_batch and input_batch must be a list of Data objects")

  def _transform_inputs(
      self,
      input_batch: List[resources_pb2.Data],
      prediction_batch: List[resources_pb2.Data],
      ground_truth_batch: List[resources_pb2.Data],
  ):
    """This function is used to transform the inputs
        Args:
            prediction_batch: List of lists containing the detections for each image in the batch (x1,y1,x2,y2,label,confidence)
            ground_truth_batch: List of lists containing the ground truth bboxes for each image in the batch (x1,y1,x2,y2,label)
        Returns:
            List of lists: The transformed inputs
        """

    def convert_bbox(regions):
      bbox_list = []
      for region in regions:
        region_info = region.region_info.bounding_box
        x1 = region_info.top_row
        y1 = region_info.left_col
        x2 = region_info.bottom_row
        y2 = region_info.right_col
        cpt = region.data.concepts[0]
        label = cpt.name
        if label not in self.available_labels:
          raise ValueError("Label is not present in the list of provided labels")
        conf = cpt.value
        if conf:
          bbox_list.append([x1, y1, x2, y2, label, conf])
        else:
          bbox_list.append([x1, y1, x2, y2, label])
      return bbox_list

    # regions = prediction_response.outputs[0].data.regions
    transformed_prediction_batch = [
        convert_bbox(detections.regions) for detections in prediction_batch
    ]
    transformed_ground_truth_batch = [
        convert_bbox(detections.regions) for detections in ground_truth_batch
    ]

    image_dimensions = get_image_dimensions(input_batch, self.clarifai_pat)
    if len(image_dimensions) != len(prediction_batch):
      raise ValueError("image_dimensions and prediction_batch must have the same length")

    return (
        image_dimensions,
        transformed_prediction_batch,
        transformed_ground_truth_batch,
    )

  def _create_dataset(
      self,
      image_dimensions: List[Tuple[int, int]],
      prediction_batch: List[List],
      ground_truth_batch: List[List],
  ) -> fo.Dataset:
    """This function is used to create a FiftyOne dataset from the inputs
        Args:
            image_dimensions: List of tuples containing the dimensions of each image in the batch (w,h)
            prediction_batch: List of lists containing the detections for each image in the batch (x1,y1,x2,y2,label,confidence)
            ground_truth_batch: List of lists containing the ground truth bboxes for each image in the batch (x1,y1,x2,y2,label)
        Returns:
            FiftyOne Dataset: The dataset containing the predictions and ground truth
        """

    def convert_bbox(bbox):
      x1 = bbox[0] * image_dimensions[i][0]
      y1 = bbox[1] * image_dimensions[i][1]
      x2 = bbox[2] * image_dimensions[i][0]
      y2 = bbox[3] * image_dimensions[i][1]
      bw = x2 - x1
      bh = y2 - y1
      label = bbox[4]
      conf = bbox[5] if len(bbox) == 6 else None
      return [x1, y1, bw, bh], label, conf

    rndm = randint(10000000, 99999999)
    dataset = fo.Dataset(name=f"my-detection-dataset-{rndm}", persistent=False)

    for i in range(len(prediction_batch)):
      fo_sample = fo.Sample(filepath="./tmp")
      p_detections = []
      for bbox in prediction_batch[i]:
        newbbox, label, conf = convert_bbox(bbox)
        p_detections.append(fo.Detection(label=label, bounding_box=newbbox, confidence=conf))
      fo_sample["predictions"] = fo.Detections(detections=p_detections)
      gt_detections = []
      for bbox in ground_truth_batch[i]:
        newbbox, label, _ = convert_bbox(bbox)
        gt_detections.append(fo.Detection(label=label, bounding_box=newbbox))
      fo_sample["ground_truth"] = fo.Detections(detections=gt_detections)
      dataset.add_sample(fo_sample)
    return dataset

  def get_metrics_info(self, gt_present: bool = True) -> dict:
    """This function is used to get the information about the metrics
        Args:
            gt_present: Whether ground truth is present
        Returns:
            dict: The information about the metrics
        """
    if gt_present:
      return {
          metric: self.all_metrics["with_gt"][metric]().get_info()
          for metric in self.all_metrics["with_gt"].keys()
      }
    else:
      return None
