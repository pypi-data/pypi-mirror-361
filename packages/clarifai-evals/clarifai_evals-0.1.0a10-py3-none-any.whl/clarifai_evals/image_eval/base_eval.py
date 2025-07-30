from typing import Dict
from clarifai_evals.common_base_evaluator import CommonBaseEvaluator


class BaseImageEvaluator(CommonBaseEvaluator):
  """This is the base class for all image evaluators. It contains the basic structure of the evaluator and the evaluate method."""

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
      **kwargs,
  ):
    """
    This method evaluates the model based on the given inputs
    Args:
        **kwargs: The input arguments like prediction_batch, ground_truth_batch, query_batch, context_batch, sub_template, mode, etc.
    Returns:
        dict: The evaluation results
    """
    return NotImplementedError("Override this method in the child class")
