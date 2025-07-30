from typing import Any, Dict, List, Union

import numpy as np
from numpy.typing import NDArray

from clarifai_evals.constant import DataTypes, VisualizationTypes
from clarifai_evals.result_data import MetricResult


class BaseImageSegmentationEvaluator:
  """This is the base evaluator class for image segmentation tasks."""

  def __init__(
      self,
      description:
      str = "Evaluates the segmentation model with metrics using ground truth and predictions mask data",
      has_explanation: bool = False,
      aggregation_type: str = None,
      graph_type: str = VisualizationTypes.confusion_matrix,
      examples: List = None,
      library: str = None,
      unit: str = DataTypes.float_type,
  ):
    """Initialisess the evaluator object
        Args:
            description (str): The description of the evaluator
            has_explanation (bool): A flag to indicate if the evaluator has an explanation
            aggregation_type (str): The type of aggregation for the evaluator - ['mean']
            graph_type (str): The type of graph for the evaluator - ['histogram', 'confusion matrix', 'precision-recall curve', None]
            examples (List): The examples for the evaluator
            library (str): The library used for the evaluator - ['numpy']
            unit (str): The unit of the evaluator - ['percentage', 'float']
        """
    self.description = description
    self.has_explanation = has_explanation
    self.aggregation_type = aggregation_type
    self.graph_type = graph_type
    self.examples = examples
    self.library = library
    self.unit = unit

  def evaluate(self, ground_truth_batch: NDArray[NDArray[np.bool_]],
               prediction_batch: NDArray[NDArray[np.bool_]]) -> Union[np.float64, Dict]:
    return NotImplementedError("Override this method in the child class")

  def get_graph_data(self) -> Any:
    return NotImplementedError("Override this method in the child class")

  def get_info(self) -> Dict:
    """Returns the information about the evaluator"""
    return {
        "description": self.description,
        "has_explanation": self.has_explanation,
        "aggregation_type": self.aggregation_type,
        "graph_type": self.graph_type,
        "examples": self.examples,
        "library": self.library,
        "unit": self.unit,
    }


class IoUEvaluator(BaseImageSegmentationEvaluator):
  """This is the evaluator class for computing IoU (Intersection over Union) for image segmentation tasks."""

  def __init__(self):
    """Initialises the evaluator object"""
    super().__init__(
        description="IoU score for image segmentation tasks",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.confusion_matrix,
        examples=None,
        library="numpy",
        unit=DataTypes.float_type,
    )

  def evaluate(self, ground_truth: NDArray[NDArray[np.bool_]],
               predictions: NDArray[NDArray[np.bool_]]) -> np.float64:
    """Evaluates the IoU for the given ground truth and predictions.
        Args:
            ground_truth (np.ndarray): A list of ground truth batch masks per class per input
            predictions (np.ndarray): A list of predicted batch masks per class per input
        Returns:
            List: A list of IoU scores for each sample
            float: The mean IoU score.
        """

    if (predictions.sum() + ground_truth.sum() -
        np.logical_and(predictions, ground_truth).sum()) != 0:
      iou = np.logical_and(predictions, ground_truth).sum() / \
          (predictions.sum() + ground_truth.sum() - np.logical_and(predictions, ground_truth).sum())
    else:
      iou = 0.0
    return iou

  def get_graph_data(self):
    return None


class DiceCoefficientEvaluator(BaseImageSegmentationEvaluator):
  """This is the evaluator class for computing Dice Coefficient for image segmentation tasks."""

  def __init__(self):
    """Initialises the evaluator object for DiceCoefficientEvaluator"""
    super().__init__(
        description="Dice Co-efficient for image segmentation tasks",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.confusion_matrix,
        examples=None,
        library="numpy",
        unit=DataTypes.float_type,
    )

  def evaluate(self, ground_truth: NDArray[NDArray[np.bool_]],
               predictions: NDArray[NDArray[np.bool_]]) -> np.float64:
    """Evaluates the Dice Coefficient for the given ground truth and predictions.
        Args:
            ground_truth (np.ndarray): A list of ground truth batch masks per class per input.
            predictions (np.ndarray): A list of predicted batch masks per class per input.
        Returns:
            dice_coefficient (float): The Dice Coefficient score.

        """
    if ground_truth.sum() == 0 and predictions.sum() == 0:
      dice_coefficient = 1.0
    elif (predictions.sum() + ground_truth.sum()) != 0:
      dice_coefficient = 2 * np.logical_and(predictions, ground_truth).sum() / (
          predictions.sum() + ground_truth.sum())

    else:
      dice_coefficient = 0.0

    return dice_coefficient

  def get_graph_data(self):
    return None


class AccuracyEvaluator(BaseImageSegmentationEvaluator):
  """This is the evaluator class for computing Accuracy for image segmentation tasks."""

  def __init__(self):
    """Initialises the evaluator object for AccuracyEvaluator"""
    super().__init__(
        description="Accuracy for image segmentation tasks",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.confusion_matrix,
        examples=None,
        library="numpy",
        unit=DataTypes.float_type,
    )

  def evaluate(self, ground_truth: NDArray[NDArray[np.bool_]],
               predictions: NDArray[NDArray[np.bool_]]) -> np.float64:
    """Evaluates the Accuracy for the given ground truth and predictions.
        Args:
            ground_truth (np.ndarray): A list of ground truth batch masks per class per input.
            predictions (np.ndarray): A list of predicted batch masks per class per input.
        Returns:
            accuracy (float): The accuracy score.
        """
    accuracy = np.sum(ground_truth == predictions) / np.prod(ground_truth.shape)
    return accuracy

  def get_graph_data(self):
    return None


class PrecisionEvaluator(BaseImageSegmentationEvaluator):
  """This is the evaluator class for computing Precision for image segmentation tasks."""

  def __init__(self):
    """Initialises the evaluator object for PrecisionEvaluator"""
    super().__init__(
        description="Precision for image segmentation tasks",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.confusion_matrix,
        examples=None,
        library="numpy",
        unit=DataTypes.float_type,
    )

  def evaluate(self, ground_truth: NDArray[NDArray[np.bool_]],
               predictions: NDArray[NDArray[np.bool_]]) -> np.float64:
    """Evaluates the Precision for the given ground truth and predictions.
        Args:
            ground_truth (np.ndarray): A list of ground truth batch masks per class per input.
            predictions (np.ndarray): A list of predicted batch masks per class per input.
        Returns:
            precision (float): The precision score.
        """
    total_predicted_positives = np.sum(predictions)
    precision = np.sum(np.logical_and(predictions, ground_truth)
                      ) / total_predicted_positives if total_predicted_positives > 0 else 0.0
    return np.nan_to_num(precision, nan=0.0)

  def get_graph_data(self):
    return None


class RecallEvaluator(BaseImageSegmentationEvaluator):
  """This is the evaluator class for computing Recall for image segmentation tasks."""

  def __init__(self):
    """Initialises the evaluator object for RecallEvaluator"""
    super().__init__(
        description="Recall for image segmentation tasks",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.confusion_matrix,
        examples=None,
        library="numpy",
        unit=DataTypes.float_type,
    )

  def evaluate(self, ground_truth: NDArray[NDArray[np.bool_]],
               predictions: NDArray[NDArray[np.bool_]]) -> np.float64:
    """Evaluates the Recall for the given ground truth and predictions.
        Args:
            ground_truth (np.ndarray): A list of ground truth batch masks per class per input.
            predictions (np.ndarray): A list of predicted batch masks per class per input.
        Returns:
            recall (float): The recall
        """
    recall = np.sum(np.logical_and(predictions, ground_truth)) / np.sum(ground_truth)
    return recall

  def get_graph_data(self):
    return None


class F1ScoreEvaluator(BaseImageSegmentationEvaluator):
  """This is the evaluator class for computing F1 Score for image segmentation tasks."""

  def __init__(self):
    """Initialises the evaluator object for F1ScoreEvaluator"""
    super().__init__(
        description="F1 score for image segmentation tasks",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.confusion_matrix,
        examples=None,
        library="numpy",
        unit=DataTypes.float_type,
    )

  def evaluate(self, precision_dict: Dict[str, np.float64],
               recall_dict: Dict[str, np.float64]) -> Dict[str, Dict[str, np.float64]]:
    """Calculates the F1 Score using precision and recall of the ground truth and predictions.
        Args:
            precision_dict (Dict): A dictionary containing the precision values for each class
            recall_dict (Dict): A dictionary containing the recall values for each class
        Returns:
            f1_scores (Dict): A dictionary containing mean F1 scores for each category.
        """
    # Single value precision and recall
    f1_scores = {}

    # Check if precision and recall are dict.
    if (isinstance(precision_dict, dict)) and (isinstance(recall_dict, dict)):
      for category in recall_dict:
        precision = precision_dict.get(category, 0.0)
        recall = recall_dict.get(category, 0.0)

        # Checking for edge case
        if precision + recall == 0:
          f1_scores[category] = 0.0
        else:
          f1_scores[category] = 2 * (precision * recall) / (precision + recall)
    else:
      return (2 * (precision_dict * recall_dict)) / (precision_dict + recall_dict)

    return f1_scores

  def get_graph_data(self):
    return None


class WeightedIoUEvaluator(BaseImageSegmentationEvaluator):
  """This is the evaluator class for computing Weighted IoU for image segmentation tasks."""

  def __init__(self):
    """Initialises the evaluator object for WeightedIoUEvaluator"""
    super().__init__(
        description="Weighted IoU for image segmentation tasks",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.confusion_matrix,
        examples=None,
        library="numpy",
        unit=DataTypes.float_type,
    )

  def evaluate(
      self, iou_per_class: Dict[str, Dict[str, Dict[str, np.float64]]]) -> Dict[str, np.float64]:
    """Evaluates the Weighted IoU per class by the weightage of presence indicator.
        Args:
            iou_per_class (Dict): A Dict of IoU scores for each class for each image
        Returns:
            List: A list of Weighted IoU scores for each sample
        """
    iou_sums = {}  # IoUs sum per class
    class_counts = {}  # Count of images where each class is present (Weightage)

    # Iterate over images and classes
    for image_id, image_data in iou_per_class.items():
      iou_dict = image_data['iou']
      for cls, iou in iou_dict.items():
        # Presence indicator: class is present if it appears in the iou_dict
        if cls in iou_dict:
          # Initialize if not already present
          if cls not in iou_sums:
            iou_sums[cls] = 0.0
            class_counts[cls] = 0
          # Update accumulators
          iou_sums[cls] += iou
          class_counts[cls] += 1

    # Calculate weighted average IoU per class
    weighted_avg_iou = {}
    for cls in iou_sums:
      if class_counts[cls] > 0:
        weighted_avg_iou[cls] = iou_sums[cls] / class_counts[cls]
      else:
        weighted_avg_iou[cls] = 0.0

    return MetricResult(metric_name='WeightedIoU', perclass_scores=weighted_avg_iou)

  def get_graph_data(self):
    return None
