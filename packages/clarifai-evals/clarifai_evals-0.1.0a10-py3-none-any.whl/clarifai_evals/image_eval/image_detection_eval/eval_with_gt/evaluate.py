from typing import Any, Dict, List, Tuple

import fiftyone as fo

from clarifai_evals.constant import DataTypes, VisualizationTypes


class FODetectionGTEvaluator:
  """This class evaluates the accuracy of the text label ground truth"""

  def __init__(self):
    pass

  def evaluate(self, fo_dataset: fo.Dataset) -> fo.DetectionResults:
    """
      This method evaluates the accuracy of the text label ground truth
      Args:
          fo_dataset: FiftyOne dataset containing the predictions and ground truth
      Returns:
          fo_result: The result of the evaluation of dataset
     """
    result = fo_dataset.evaluate_detections(
        pred_field="predictions",
        gt_field="ground_truth",
        eval_key="eval_coco",
        compute_mAP=True,
    )
    return result


class BaseDetectionGTEvaluator:

  def __init__(
      self,
      description="It evaluates the detections of the model by comparing them with the ground truth using FiftyOne library",
      has_explanation=False,
      aggregation_type=None,
      graph_type=VisualizationTypes.undefined,
      corrective_action=None,
      examples=None,
      library=None,
      unit=DataTypes.float_type,
  ):
    self.description = description
    self.has_explanation = has_explanation
    self.aggregation_type = aggregation_type
    self.graph_type = graph_type
    self.corrective_action = corrective_action
    self.examples = examples
    self.library = library
    self.unit = unit

  def evaluate(self, fo_dataset: fo.Dataset,
               fo_result: fo.DetectionResults) -> Tuple[float, Dict, List, List]:
    return NotImplementedError("Override this method in the child class")

  def get_graph_data(self, fo_result: fo.DetectionResults) -> Any:
    return NotImplementedError("Override this method in the child class")

  def get_info(self):
    return {
        "description": self.description,
        "has_explanation": self.has_explanation,
        "aggregation_type": self.aggregation_type,
        "graph_type": self.graph_type,
        "corrective_action": self.corrective_action,
        "examples": self.examples,
        "library": self.library,
        "unit": self.unit,
    }


class AccuracyDetectionGTEvaluator(BaseDetectionGTEvaluator):

  def __init__(self):
    super().__init__(
        description="Accuracy score for object detections",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.confusion_matrix,
        corrective_action=None,
        examples=None,
        library="fiftyone",
        unit=DataTypes.float_type,
    )

  def evaluate(self, fo_dataset: fo.Dataset,
               fo_result: fo.DetectionResults) -> Tuple[float, Dict, List, List]:
    """This method evaluates the accuracy of the detections
    Args:
        fo_dataset (fo.Dataset): FiftyOne dataset containing the predictions and ground truth
        fo_result (fo.DetectionResults): The results of the evaluation
    Returns:
        float: The average accuracy
        Dict: The per class accuracy
        List: The per sample accuracy
        List[List]: The per object accuracy
    """
    return round(fo_result.metrics()['accuracy'], 4), None, None, None

  def get_graph_data(self, fo_result):
    """This method returns the confusion matrix for the evaluation
    Args:
        fo_result: The results of the evaluation
    Returns:
        Dict: The confusion matrix
    """
    return fo_result.confusion_matrix()


class PrecisionDetectionGTEvaluator(BaseDetectionGTEvaluator):

  def __init__(self):
    super().__init__(
        description="Precision score for object detections",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.pr_curve,
        corrective_action=None,
        examples=None,
        library="fiftyone",
        unit=DataTypes.float_type,
    )

  def evaluate(self, fo_dataset: fo.Dataset,
               fo_result: fo.DetectionResults) -> Tuple[float, Dict, List, List]:
    """This method evaluates the precision for the detections
    Args:
        fo_dataset (fo.Dataset): FiftyOne dataset containing the predictions and ground truth
        fo_result (fo.DetectionResults): The results of the evaluation
    Returns:
        float: The average precision
        Dict: The per class precision
        List: The per sample precision
        List[List]: The per object precision
    """
    report = fo_result.report()
    perclass_scores = {}
    for cls, scores in report.items():
      if cls in ['micro avg', 'macro avg', 'weighted avg', 'accuracy']:
        continue
      perclass_scores[cls] = round(scores['precision'], 4)

    return round(fo_result.metrics()['precision'], 4), perclass_scores, None, None

  def get_graph_data(self, fo_result):
    """This method returns the precision recall curve for the evaluation
    Args:
        fo_result: The results of the evaluation
    Returns:
        Dict: The precision recall curve
    """
    return fo_result.plot_pr_curves()


class RecallDetectionGTEvaluator(BaseDetectionGTEvaluator):

  def __init__(self):
    super().__init__(
        description="Recall score for object detections",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        examples=None,
        library="fiftyone",
        unit=DataTypes.float_type,
    )

  def evaluate(self, fo_dataset: fo.Dataset,
               fo_result: fo.DetectionResults) -> Tuple[float, Dict, List, List]:
    """This method evaluates the recall for the detections
    Args:
        fo_dataset (fo.Dataset): FiftyOne dataset containing the predictions and ground truth
        fo_result (fo.DetectionResults): The results of the evaluation
    Returns:
        float: The average recall
        Dict: The per class recall
        List: The per sample recall
        List[List]: The per object recall
    """
    report = fo_result.report()
    perclass_scores = {}
    for cls, scores in report.items():
      if cls in ['micro avg', 'macro avg', 'weighted avg', 'accuracy']:
        continue
      perclass_scores[cls] = round(scores['recall'], 4)

    return round(fo_result.metrics()['recall'], 4), perclass_scores, None, None

  def get_graph_data(self, fo_result):
    """This method returns the precision recall curve for the evaluation"""
    return None


class FScoreDetectionGTEvaluator(BaseDetectionGTEvaluator):

  def __init__(self):
    super().__init__(
        description="F1 score for object detections",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        examples=None,
        library="fiftyone",
        unit=DataTypes.float_type,
    )

  def evaluate(self, fo_dataset: fo.Dataset,
               fo_result: fo.DetectionResults) -> Tuple[float, Dict, List, List]:
    """This method evaluates the F1 score for the detections
    Args:
        fo_dataset (fo.Dataset): FiftyOne dataset containing the predictions and ground truth
        fo_result (fo.DetectionResults): The results of the evaluation
    Returns:
        float: The average F1 score
        Dict: The per class F1 score
        List: The per sample F1 score
        List[List]: The per object F1 score
    """
    report = fo_result.report()
    perclass_scores = {}
    for cls, scores in report.items():
      if cls in ['micro avg', 'macro avg', 'weighted avg', 'accuracy']:
        continue
      perclass_scores[cls] = round(scores['f1-score'], 4)

    return round(fo_result.metrics()['fscore'], 4), perclass_scores, None, None

  def get_graph_data(self, fo_result):
    return None


class SupportDetectionGTEvaluator(BaseDetectionGTEvaluator):

  def __init__(self):
    super().__init__(
        description="Support score for object detections",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        examples=None,
        library="fiftyone",
        unit=DataTypes.float_type,
    )

  def evaluate(self, fo_dataset: fo.Dataset,
               fo_result: fo.DetectionResults) -> Tuple[float, Dict, List, List]:
    """This method gives the support of the detections
    Args:
        fo_dataset (fo.Dataset): FiftyOne dataset containing the predictions and ground truth
        fo_result (fo.DetectionResults): The results of the evaluation
    Returns:
        float: The average support
        Dict: The per class support
        List: The per sample support
        List[List]: The per object support
    """
    report = fo_result.report()
    perclass_scores = {}
    for cls, scores in report.items():
      if cls in ['micro avg', 'macro avg', 'weighted avg', 'accuracy']:
        continue
      perclass_scores[cls] = scores['support']

    return fo_result.metrics()['support'], perclass_scores, None, None

  def get_graph_data(self, fo_result):
    return None


class MAPDetectionGTEvaluator(BaseDetectionGTEvaluator):

  def __init__(self):
    super().__init__(
        description="Mean average precision for object detections",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        examples=None,
        library="fiftyone",
        unit=DataTypes.float_type,
    )

  def evaluate(self, fo_dataset: fo.Dataset,
               fo_result: fo.DetectionResults) -> Tuple[float, Dict, List, List]:
    """This method evaluates the mean average precision for the detections
    Args:
        fo_dataset (fo.Dataset): FiftyOne dataset containing the predictions and ground truth
        fo_result (fo.DetectionResults): The results of the evaluation
    Returns:
        float: The average mean average precision
        Dict: The per class mean average precision
        List: The per sample mean average precision
        List[List]: The per object mean average precision
    """
    return round(fo_result.mAP(), 4), None, None, None

  def get_graph_data(self, fo_result):
    return None


class IOUDetectionGTEvaluator(BaseDetectionGTEvaluator):

  def __init__(self):
    super().__init__(
        description="Intersection over Union for object detections",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        examples=None,
        library="fiftyone",
        unit=DataTypes.float_type,
    )

  def evaluate(self, fo_dataset: fo.Dataset,
               fo_result: fo.DetectionResults) -> Tuple[float, Dict, List, List]:
    """This method evaluates the intersection over union for the detections
    Args:
        fo_dataset (fo.Dataset): FiftyOne dataset containing the predictions and ground truth
        fo_result (fo.DetectionResults): The results of the evaluation
    Returns:
        float: The average intersection over union
        Dict: The per class intersection over union
        List: The per sample intersection over union
        List[List]: The per object intersection over union
    """
    persample_scores = []
    perobject_scores = []
    perclass_scores = {m: [] for m in fo_result.classes}
    for sample in list(fo_dataset.iter_samples()):
      sample_obj_scores = []
      tp_ious = []
      for bbox in sample["predictions"].detections:
        try:
          sample_obj_scores.append(round(bbox.eval_coco_iou, 4))
        except AttributeError:
          sample_obj_scores.append(0)
        if bbox.eval_coco == 'tp':
          try:
            tp_ious.append(round(bbox.eval_coco_iou, 4))
            perclass_scores[bbox.label].append(round(bbox.eval_coco_iou, 4))
          except AttributeError:
            tp_ious.append(0)
            perclass_scores[bbox.label].append(0)
      perobject_scores.append(sample_obj_scores)
      persample_scores.append(round(sum(tp_ious) / len(tp_ious) if tp_ious else 0, 4))
    perclass_scores = {
        c: round(sum(scores) / len(scores), 4) if len(scores) > 0 else 0
        for c, scores in perclass_scores.items()
    }

    return round(sum(persample_scores) / len(persample_scores),
                 4), perclass_scores, persample_scores, perobject_scores

  def get_graph_data(self, fo_result):
    return None


class TPDetectionGTEvaluator(BaseDetectionGTEvaluator):

  def __init__(self):
    super().__init__(
        description="True positive detections for object detections",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        examples=None,
        library="fiftyone",
        unit=DataTypes.float_type,
    )

  def evaluate(self, fo_dataset: fo.Dataset,
               fo_result: fo.DetectionResults) -> Tuple[float, Dict, List, List]:
    """This method gives the true positive detections
    Args:
        fo_dataset (fo.Dataset): FiftyOne dataset containing the predictions and ground truth
        fo_result (fo.DetectionResults): The results of the evaluation
    Returns:
        float: The average true positive detections
        Dict: The per class true positive detections
        List: The per sample true positive detections
        List[List]: The per object true positive detections
    """
    persample_scores = []
    perobject_scores = []
    perclass_scores = {m: [] for m in fo_result.classes}
    for sample in list(fo_dataset.iter_samples()):
      sample_obj_scores = []
      for bbox in sample["predictions"].detections:
        if bbox.eval_coco == 'tp':
          sample_obj_scores.append(1)
          perclass_scores[bbox.label].append(1)
        else:
          sample_obj_scores.append(0)
          perclass_scores[bbox.label].append(0)
      perobject_scores.append(sample_obj_scores)
      persample_scores.append(round(sample.eval_coco_tp / len(sample_obj_scores), 4))

    perclass_scores = {
        m: round(sum(scores) / len(scores), 4)
        for m, scores in perclass_scores.items()
    }

    return round(sum(persample_scores) / len(persample_scores),
                 4), perclass_scores, persample_scores, perobject_scores

  def get_graph_data(self, fo_result):
    return None


class FPDetectionGTEvaluator(BaseDetectionGTEvaluator):

  def __init__(self):
    super().__init__(
        description="False positive detections for object detections",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        examples=None,
        library="fiftyone",
        unit=DataTypes.float_type,
    )

  def evaluate(self, fo_dataset: fo.Dataset,
               fo_result: fo.DetectionResults) -> Tuple[float, Dict, List, List]:
    """This method gives the false positive detections
    Args:
        fo_dataset (fo.Dataset): FiftyOne dataset containing the predictions and ground truth
        fo_result (fo.DetectionResults): The results of the evaluation
    Returns:
        float: The average false positive detections
        Dict: The per class false positive detections
        List: The per sample false positive detections
        List[List]: The per object false positive detections
    """
    persample_scores = []
    perobject_scores = []
    perclass_scores = {m: [] for m in fo_result.classes}
    for sample in list(fo_dataset.iter_samples()):
      sample_obj_scores = []
      for bbox in sample["predictions"].detections:
        if bbox.eval_coco == 'fp':
          sample_obj_scores.append(1)
          perclass_scores[bbox.label].append(1)
        else:
          sample_obj_scores.append(0)
          perclass_scores[bbox.label].append(0)
      perobject_scores.append(sample_obj_scores)
      persample_scores.append(round(sample.eval_coco_fp / len(sample_obj_scores), 4))
    perclass_scores = {
        m: round(sum(scores) / len(scores), 4)
        for m, scores in perclass_scores.items()
    }

    return round(sum(persample_scores) / len(persample_scores),
                 4), perclass_scores, persample_scores, perobject_scores

  def get_graph_data(self, fo_result):
    return None


class FNDetectionGTEvaluator(BaseDetectionGTEvaluator):

  def __init__(self):
    super().__init__(
        description="False negative detections for object detections",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        examples=None,
        library="fiftyone",
        unit=DataTypes.float_type,
    )

  def evaluate(self, fo_dataset: fo.Dataset,
               fo_result: fo.DetectionResults) -> Tuple[float, Dict, List, List]:
    """This method gives the false negative detections
    Args:
        fo_dataset (fo.Dataset): FiftyOne dataset containing the predictions and ground truth
        fo_result (fo.DetectionResults): The results of the evaluation
    Returns:
        float: The average false negative detections
        Dict: The per class false negative detections
        List: The per sample false negative detections
        List[List]: The per object false negative detections
    """
    persample_scores = []
    perobject_scores = []
    perclass_scores = {m: [] for m in fo_result.classes}
    for sample in list(fo_dataset.iter_samples()):
      sample_obj_scores = []
      for bbox in sample["predictions"].detections:
        if bbox.eval_coco == 'fn':
          sample_obj_scores.append(1)
          perclass_scores[bbox.label].append(1)
        else:
          sample_obj_scores.append(0)
          perclass_scores[bbox.label].append(0)
      perobject_scores.append(sample_obj_scores)
      persample_scores.append(round(sample.eval_coco_fn / len(sample_obj_scores), 4))
    perclass_scores = {
        m: round(sum(scores) / len(scores), 4)
        for m, scores in perclass_scores.items()
    }

    return round(sum(persample_scores) / len(persample_scores),
                 4), perclass_scores, persample_scores, perobject_scores

  def get_graph_data(self, fo_result):
    return None
