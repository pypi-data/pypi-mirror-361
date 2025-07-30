from typing import Dict, List, Tuple

from clarifai_grpc.grpc.api import resources_pb2
from uptrain import Settings

from clarifai_evals.constant import DEFAULT_TEXT_GEN_JUDGE_LLM_URL, TaskTypes, VisualizationTypes
from clarifai_evals.text_eval.base_eval import BaseLLMJudgeTextEvaluator


class BaseTextGenerationEvaluator(BaseLLMJudgeTextEvaluator):
  """This is the base class for all text generation ground truth evaluators. It contains the basic structure of the evaluator and the evaluate method."""

  def __init__(
      self,
      clarifai_pat: str,
      description: str,
      has_explanation: bool = False,
      aggregation_type: str = "mean",
      graph_type: str = VisualizationTypes.undefined,
      corrective_action: str = None,
      examples: List = [],
      library: str = None,
      unit: str = None,
      clarifai_model_url: str = DEFAULT_TEXT_GEN_JUDGE_LLM_URL,
      task_type: str = TaskTypes.text_generation,
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
    self.clarifai_model_url = clarifai_model_url
    self.description = description
    self.has_explanation = has_explanation
    self.aggregation_type = aggregation_type
    self.graph_type = graph_type
    self.corrective_action = corrective_action
    self.examples = examples
    self.library = library
    self.unit = unit
    self.task_type = task_type
    model = clarifai_model_url.split("/")[-1]
    user = clarifai_model_url.split("/")[-4]
    app = clarifai_model_url.split("/")[-3]
    uptrain_model = "clarifai/" + user + "." + app + "." + model
    self.settings = Settings(
        model=uptrain_model,
        clarifai_api_key=clarifai_pat,
        custom_llm_provider="clarifai",
    )
    self.corrective_action = corrective_action if corrective_action else None
    if self.corrective_action is None:
      self.corrective_action = "1. Include explicit instructions in the prompt about what information is required and how it should be presented. \
                                    2. Request answers in a structured format that makes it easier for the model to generate precise responses. \
                                    3. Apply post-processing techniques to refine the model's output, ensuring it matches the expected response more closely. \
                                    4. Include examples of correct responses in the prompt to set a standard for the model."

  def evaluate(
      self,
      query_batch: List[resources_pb2.Data],
      predictions_batch: List[resources_pb2.Data],
      ground_truth_batch: List[resources_pb2.Data] = None,
      context_batch: List[resources_pb2.Data] = None,
  ) -> Tuple:
    return NotImplementedError("Override this method in the child class")

  def get_graph_data(self, ground_truth_batch: List[List], prediction_dict: Dict):
    return NotImplementedError("Override this method in the child class")

  def get_info(self) -> Dict:
    """Returns the information about the evaluator"""
    return {
        "judge_model": self.clarifai_model_url,
        "description": self.description,
        "has_explanation": self.has_explanation,
        "aggregation_type": self.aggregation_type,
        "graph_type": self.graph_type,
        "corrective_action": self.corrective_action,
        "examples": self.examples,
        "library": self.library,
        "unit": self.unit,
        "task_type": self.task_type,
    }

  def batch_to_uptrain_inputs(
      self,
      query_batch: List[str],
      predictions_batch: List[str] = None,
      ground_truth_batch: List[str] = None,
      context_batch: List[str] = None,
  ) -> List[Dict]:
    """Converts the batch to uptrain inputs"""
    data = []
    for i in range(len(query_batch)):
      data = [{
          "question": query_batch[i],
          "response": predictions_batch[i] if predictions_batch else None,
          "ground_truth": ground_truth_batch[i] if ground_truth_batch else None,
          "context": context_batch[i] if context_batch else None,
      } for i in range(len(query_batch))]
    return data
