from typing import Dict, List

from clarifai_evals.common_base_evaluator import CommonBaseEvaluator
from clarifai_evals.constant import DEFAULT_TEXT_GEN_JUDGE_LLM_URL


class BaseTextEvaluator(CommonBaseEvaluator):
  """This is the base class for all text evaluators. It contains the basic structure of the evaluator and the evaluate method."""

  def __init__(
      self,
      description: str,
      task_type: str,
      all_metrics: Dict = {},
      quick_metrics: Dict = {},
      batch_size: int = 32,
  ):
    """Initializes the evaluator object
        Args:
            description (str): The description of the evaluator, eg: Text Classification Evaluator
            task_type (str): The type of task the evaluator is designed for, eg: text-classification
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
      ground_truth_batch: List = None,
      query_batch: List = None,
      context_batch: List = None,
      sub_template: str = "all",
      mode: str = "detailed",
  ):
    """This method evaluates the model based on the given inputs
        Args:
            prediction_batch (List): A list of lists containing the predictions
            ground_truth_batch (List): A list of lists containing the ground truth labels
            query_batch (List): A list of queries
            context_batch (List): A list of contexts
            mode (str): The mode of evaluation, eg: detailed, quick
        Returns:
            dict: The evaluation results
        """
    return NotImplementedError("Override this method in the child class")


class BaseLLMJudgeTextEvaluator:
  """This is the base class for all LLM Judge text evaluators. It contains the basic structure of the evaluator and the evaluate method."""

  def __init__(
      self,
      clarifai_pat: str,
      description: str,
      task_type: str,
      clarifai_model_url: str = DEFAULT_TEXT_GEN_JUDGE_LLM_URL,
      has_explanation: bool = False,
      aggregation_type: str = "mean",
      graph_type: str = None,
      corrective_action: str = None,
      examples: List = [],
      library: str = None,
      unit: str = None,
      judge_prompt: str = None,
      batch_size: int = 32,
  ):
    """Initializes the evaluator object
        Args:
            clarifai_pat (str): The Clarifai Personal Access Token
            clarifai_model_url (str): The Clarifai Model URL
            description (str): The description of the evaluator, eg: Text Summarization Evaluator
            task_type (str): The type of task the evaluator is designed for - ['classification', 'generation']
            has_explanation (bool): Whether the evaluator provides an explanation
            aggregation_type (str): The aggregation type for the evaluator - ['mean']
            graph_type (str): The type of graph for the evaluator - ['histogram', 'confusion matrix', 'precision-recall curve', None]
            corrective_action (str): The corrective action for the evaluator, if any
            examples (List): A list of examples
            library (str): The library used for the evaluator - ['clarifai', 'uptrain', 'sklearn']
            unit (str): The unit for the evaluator - ['percentage', 'tenths']
            judge_prompt (str): The judge prompt for the evaluator
            batch_size (int): The batch size for the evaluator
        """
    self.description = description
    self.task_type = task_type
    self.has_explanation = has_explanation
    self.aggregation_type = aggregation_type
    self.graph_type = graph_type
    self.corrective_action = corrective_action
    self.examples = examples
    self.library = library
    self.unit = unit
    clarifai_model_url = ("https://clarifai.com/openai/chat-completion/models/GPT-4"
                          if clarifai_model_url is None else clarifai_model_url)
    self.judge_llm = clarifai_model_url.split("/")[-1]
    if self.judge_llm not in ["GPT-4", "llama2-70b-chat", "claude-v2"]:
      raise ValueError("Invalid LLM Judge. Please choose from GPT-4, llama2-70b-chat, claude-v2")
    self.judge_prompt = judge_prompt
    self.clarifai_pat = clarifai_pat
    self.clarifai_model_url = clarifai_model_url
    self.batch_size = batch_size

  def evaluate(self, *args):
    return NotImplementedError("Override this method in the child class")

  def get_info(self):
    return {
        "description": self.description,
        "task_type": self.task_type,
        "has_explanation": self.has_explanation,
        "aggregation_type": self.aggregation_type,
        "graph_type": self.graph_type,
        "corrective_action": self.corrective_action,
        "examples": self.examples,
        "library": self.library,
        "unit": self.unit,
        "judge_prompt": self.judge_prompt,
        "clarifai_model_url": self.clarifai_model_url,
    }
