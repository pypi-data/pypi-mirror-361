from typing import Dict, List, Tuple

import numpy as np
from sklearn.metrics import (average_precision_score, f1_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score)
from clarifai_evals.constant import DataTypes, VisualizationTypes


class BaseTextLabelGTEvaluator:
  """This is the base class for all text label ground truth evaluators. It contains the basic structure of the evaluator and the evaluate method."""

  def __init__(
      self,
      description: str,
      has_explanation: bool = False,
      aggregation_type: str = "mean",
      graph_type: str = VisualizationTypes.undefined,
      corrective_action: str = "None",
      examples: List = [],
      library: str = None,
      unit: str = DataTypes.undefined,
  ):
    """Initializes the evaluator object
        Args:
            description (str): The description of the evaluator
            has_explanation (bool): Whether the evaluator has an explanation
            aggregation_type (str): The type of aggregation for the evaluator - ['mean']
            graph_type (str): The type of graph for the evaluator - ['histogram', 'confusion matrix', 'precision-recall curve', None]
            corrective_action (str): The corrective action for the evaluator
            examples (List): The examples for the evaluator
            library (str): The library used for the evaluator - ['clarifai', 'uptrain', 'sklearn']
            unit (str): The unit of the evaluator - ['percentage', 'float']
        """
    self.description = description
    self.has_explanation = has_explanation
    self.aggregation_type = aggregation_type
    self.graph_type = graph_type
    self.corrective_action = corrective_action
    self.examples = examples
    self.library = library
    self.unit = unit

  def evaluate(self, ground_truth_batch: List[List], prediction_dict: Dict):
    return NotImplementedError("Override this method in the child class")

  def get_graph_data(self, ground_truth_batch: List[List], prediction_dict: Dict):
    return NotImplementedError("Override this method in the child class")

  def get_info(self) -> Dict:
    """Returns the information about the evaluator"""
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


class TextLabelAccuracyGTEvaluator(BaseTextLabelGTEvaluator):
  """This class evaluates the accuracy of the text label ground truth"""

  def __init__(self):
    """Initializes the evaluator object"""
    super().__init__(
        description=
        "The set of labels predicted for a sample must exactly match the corresponding set of labels in y_true",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.confusion_matrix,
        corrective_action=None,
        examples=None,
        library="sklearn",
        unit=DataTypes.float_type,
    )

  def evaluate(self, ground_truth_batch: List[List], predictions_dict) -> Tuple[List, float, List]:
    """This method evaluates the accuracy of the text label ground truth
        Args:
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
            predictions_dict (Dict): A dictionary containing the predictions in the form of onehot encoding, confidence scores & vector encoding
        Returns:
            List: The per class accuracy
            float: The average accuracy
        """
    per_sample_accuracy = np.array(
        ground_truth_batch == predictions_dict["onehot_encoding"], dtype=int)
    perclass_accuracy = np.sum(per_sample_accuracy, axis=0) / len(ground_truth_batch)
    avg_accuracy = sum(perclass_accuracy) / len(perclass_accuracy)
    per_sample_accuracy = np.sum(per_sample_accuracy, axis=1) / len(per_sample_accuracy[0])
    return perclass_accuracy, avg_accuracy, per_sample_accuracy.tolist()

  def get_graph_data(self, ground_truth_batch: List[List], predictions_dict: Dict) -> Dict:
    """This method returns the graph data for the evaluator
        Args:
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
            predictions_dict (Dict): A dictionary containing the predictions
        Returns:
            dict: The graph data
        """
    # cm_basic = confusion_matrix(ground_truth_batch, predictions_dict['vector_encoding'])
    # for each class:
    # [[tn, fp],
    #  [fn, tp]]
    # cm_multilabel = multilabel_confusion_matrix(ground_truth_batch, predictions_dict["onehot_encoding"])
    # return cm_multilabel
    return None


class TextLabelF1ScoreGTEvaluator(BaseTextLabelGTEvaluator):
  """This class evaluates the F1 score of the text label ground truth"""

  def __init__(self):
    """Initializes the evaluator object"""
    super().__init__(
        description=
        "The F1 score can be interpreted as a harmonic mean of the precision and recall, \
                where an F1 score reaches its best value at 1 and worst score at 0. \
                The relative contribution of precision and recall to the F1 score are equal. ",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        examples=None,
        library="sklearn",
        unit=DataTypes.float_type,
    )

  def evaluate(self, ground_truth_batch: List[List],
               predictions_dict: Dict) -> Tuple[List, float, List]:
    """This method evaluates the F1 score of the text label ground truth
        Args:
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
            predictions_dict (Dict): A dictionary containing the predictions in the form of onehot encoding, confidence scores & vector encoding
        Returns:
            List: The per class F1 score
            float: The average F1 score
        """
    perclass_f1 = f1_score(ground_truth_batch, predictions_dict["onehot_encoding"], average=None)
    f1_avg = sum(perclass_f1) / len(perclass_f1)
    return perclass_f1, f1_avg, None

  def get_graph_data(self, ground_truth_batch: List[List], predictions_dict: Dict) -> None:
    return None


class TextLabelPrecisionGTEvaluator(BaseTextLabelGTEvaluator):
  """This class evaluates the precision of the text label ground truth"""

  def __init__(self):
    super().__init__(
        description=
        "The precision is the ratio tp / (tp + fp) where tp is the number of true positives and fp the number of false positives. \
                The precision is intuitively the ability of the classifier not to label as positive a sample that is negative. \
                The best value is 1 and the worst value is 0.",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.pr_curve,
        corrective_action=None,
        examples=None,
        library="sklearn",
        unit=DataTypes.float_type,
    )

  def evaluate(self, ground_truth_batch: List[List],
               predictions_dict: Dict) -> Tuple[List, float, List]:
    """This method evaluates the precision of the text label ground truth
        Args:
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
            predictions_dict (Dict): A dictionary containing the predictions in the form of onehot encoding, confidence scores & vector encoding
        Returns:
            List: The per class precision
            float: The average precision
        """
    perclass_precision = precision_score(
        ground_truth_batch, predictions_dict["onehot_encoding"], average=None)
    precision_avg = sum(perclass_precision) / len(perclass_precision)
    return perclass_precision, precision_avg, None

  def get_graph_data(self, ground_truth_batch: List[List], predictions_dict: Dict) -> Dict:
    """This method returns the graph data for the evaluator
        Args:
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
            predictions_dict (Dict): A dictionary containing the predictions in the form of onehot encoding, confidence scores & vector encoding
        Returns:
            dict: The graph data
        """
    # For each class
    precision, recall, threshold, average_precision = {}, {}, {}, {}
    pred_scores = predictions_dict["confidence_scores"]
    for i in range(len(ground_truth_batch[0])):
      precision[i], recall[i], threshold[i] = precision_recall_curve(ground_truth_batch[:, i],
                                                                     pred_scores[:, i])
      average_precision[i] = average_precision_score(ground_truth_batch[:, i], pred_scores[:, i])

    # A "micro-average": quantifying score on all classes jointly
    (
        precision["micro"],
        recall["micro"],
        threshold["micro"],
    ) = precision_recall_curve(ground_truth_batch.ravel(), pred_scores.ravel())
    average_precision["micro"] = average_precision_score(
        ground_truth_batch, pred_scores, average="micro")
    response = {
        "precision": precision,
        "recall": recall,
        "threshold": threshold,
        "average_precision": average_precision,
    }
    return response


class TextLabelRecallGTEvaluator(BaseTextLabelGTEvaluator):
  """This class evaluates the recall of the text label ground truth"""

  def __init__(self):
    super().__init__(
        description=
        "The recall is the ratio tp / (tp + fn) where tp is the number of true positives and fn the number of false negatives. \
                The recall is intuitively the ability of the classifier to find all the positive samples. \
                The best value is 1 and the worst value is 0.",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.pr_curve,
        corrective_action=None,
        examples=None,
        library="sklearn",
        unit=DataTypes.float_type,
    )

  def evaluate(self, ground_truth_batch: List[List],
               predictions_dict: Dict) -> Tuple[List, float, List]:
    """This method evaluates the recall of the text label ground truth
        Args:
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
            predictions_dict (Dict): A dictionary containing the predictions in the form of onehot encoding, confidence scores & vector encoding
        Returns:
            List: The per class recall
            float: The average recall
        """
    perclass_recall = recall_score(
        ground_truth_batch, predictions_dict["onehot_encoding"], average=None)
    recall_avg = sum(perclass_recall) / len(perclass_recall)
    return perclass_recall, recall_avg, None

  def get_graph_data(self, ground_truth_batch: List[List], predictions_dict: Dict) -> None:
    return None


class TextLabelROCAUCGTEvaluator(BaseTextLabelGTEvaluator):
  """ "This class evaluates the Area Under the Receiver Operating Characteristic Curve (ROC AUC) of the text label ground truth"""

  def __init__(self):
    super().__init__(
        description=
        "Compute Area Under the Receiver Operating Characteristic Curve (ROC AUC) from prediction scores",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.roc_auc_curve,
        corrective_action=None,
        examples=None,
        library="sklearn",
        unit=DataTypes.float_type,
    )

  def evaluate(self, ground_truth_batch: List[List],
               predictions_dict: Dict) -> Tuple[List, float, List]:
    """This method evaluates the ROC AUC of the text label ground truth
        Args:
            ground_truth_batch (List[List]): A list of lists containing the ground truth labels
            predictions_dict (Dict): A dictionary containing the predictions in the form of onehot encoding, confidence scores & vector encoding
            Returns:
            List: The per class ROC AUC
            float: The average ROC AUC
        """
    try:
      perclass_roc_auc = roc_auc_score(
          ground_truth_batch, predictions_dict["confidence_scores"], average=None)
    except ValueError as e:
      print(e)
      return None, None, None
    roc_auc_avg = sum(perclass_roc_auc) / len(perclass_roc_auc)
    return perclass_roc_auc, roc_auc_avg, None

  def get_graph_data(self, ground_truth_batch: List[List], predictions_dict: Dict) -> Dict:
    return None

    ### Keeping this code for reference when integrating with the Clarifai-web
    # """This method returns the graph data for the evaluator
    #     Args:
    #         ground_truth_batch (List[List]): A list of lists containing the ground truth labels
    #         predictions_dict (Dict): A dictionary containing the predictions in the form of onehot encoding, confidence scores & vector encoding
    #         Returns:
    #         dict: The graph data
    #     """
    # # For each class
    # fpr, tpr, threshold, roc_auc = {}, {}, {}, {}
    # pred_scores = predictions_dict["confidence_scores"]
    # for i in range(len(ground_truth_batch[0])):
    #   fpr[i], tpr[i], threshold[i] = roc_curve(ground_truth_batch[:, i], pred_scores[:, i])
    #   roc_auc[i] = auc(fpr[i], tpr[i])

    # # A "micro-average": quantifying score on all classes jointly
    # fpr["micro"], tpr["micro"], threshold["micro"] = roc_curve(ground_truth_batch.ravel(),
    #                                                            pred_scores.ravel())
    # roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
    # response = {"fpr": fpr, "tpr": tpr, "roc_auc": roc_auc, "threshold": threshold}
    # return response
