from typing import Dict, List, Tuple

from uptrain import EvalLLM, Evals

from clarifai_evals.constant import DEFAULT_TEXT_GEN_JUDGE_LLM_URL, DataTypes, VisualizationTypes
from clarifai_evals.text_eval.text_generation_eval.base_text_gen_eval import \
    BaseTextGenerationEvaluator


##TODO: RETRY EVAL IF SCORE RESPONSE IS NONE
class TextGenCompletenessEvaluator(BaseTextGenerationEvaluator):
  """Checks whether the response has answered all the aspects of the question specified"""

  def __init__(
      self,
      clarifai_pat: str,
      clarifai_model_url: str = DEFAULT_TEXT_GEN_JUDGE_LLM_URL,
  ):
    """Initializes the evaluator object"""
    super().__init__(
        clarifai_pat=clarifai_pat,
        description=
        "Checks whether the response has answered all the aspects of the question specified. This check is important to ensure that the model is not generating incomplete responses.",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action="1. Clearly state what aspects need to be covered in the prompt \n\
          2. Prompt the llm to break down the question into sequential parts and answer them all",
        examples=None,
        library="uptrain",
        unit=DataTypes.float_type,
        clarifai_model_url=clarifai_model_url,
    )

  def evaluate(
      self,
      query_batch: List[str],
      predictions_batch: List[str],
      ground_truth_batch: List[str] = None,
      context_batch: List[str] = None,
  ) -> Tuple[List, float, List]:
    """
        This method evaluates the completeness of the predicted text
        Args:
            query_batch (List[str]): A list of queries
            predictions_batch (List[str]): A list of predictions
        Returns:
            List: Per sample score
            float: The average score
            List: The explanations for each sample
        """
    data = self.batch_to_uptrain_inputs(query_batch, predictions_batch)
    eval_llm = EvalLLM(self.settings)
    results = eval_llm.evaluate(data=data, checks=[Evals.RESPONSE_COMPLETENESS])
    metric_scores = []
    explanations = []
    for result in results:
      metric_scores.append(
          round(result["score_response_completeness"], 4)
          if result["score_response_completeness"] is not None else 0)
      expln = result["explanation_response_completeness"]
      expln = (expln["Reasoning"] if isinstance(expln, dict) and "Reasoning" in expln else expln)
      explanations.append(expln)
    return metric_scores, round(sum(metric_scores) / len(metric_scores), 4), explanations

  def get_graph_data(self, ground_truth_batch: List[List], predictions_dict: Dict) -> None:
    return None


class TextGenConcisenessEvaluator(BaseTextGenerationEvaluator):
  """Grades how concise the generated response is or if it has any additional irrelevant information for the question asked."""

  def __init__(
      self,
      clarifai_pat: str,
      clarifai_model_url: str = DEFAULT_TEXT_GEN_JUDGE_LLM_URL,
  ):
    super().__init__(
        clarifai_pat=clarifai_pat,
        description=
        "Grades how concise the generated response is or if it has any additional irrelevant information for the question asked.",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=
        "1. In the prompt, use constraints for response length (such as 1 sentence) \n\
          2. Mention length preference in prompt (such as ‘respond briefly’)",
        examples=None,
        library="uptrain",
        unit=DataTypes.float_type,
        clarifai_model_url=clarifai_model_url,
    )

  def evaluate(
      self,
      query_batch: List[str],
      predictions_batch: List[str],
      ground_truth_batch: List[str] = None,
      context_batch: List[str] = None,
  ) -> Tuple[List, float, List]:
    """
        This method evaluates the conciseness of the generated text
        Args:
            query_batch (List[str]): A list of queries
            predictions_batch (List[str]): A list of predictions
        Returns:
            List: Per sample score
            float: The average score
            List: The explanations for each sample
        """
    data = self.batch_to_uptrain_inputs(query_batch, predictions_batch)
    eval_llm = EvalLLM(self.settings)
    results = eval_llm.evaluate(data=data, checks=[Evals.RESPONSE_CONCISENESS])
    metric_scores = []
    explanations = []
    for result in results:
      metric_scores.append(
          round(result["score_response_conciseness"], 4)
          if result["score_response_conciseness"] is not None else 0)
      expln = result["explanation_response_conciseness"]
      expln = (expln["Reasoning"] if isinstance(expln, dict) and "Reasoning" in expln else expln)
      explanations.append(expln)
    return metric_scores, round(sum(metric_scores) / len(metric_scores), 4), explanations

  def get_graph_data(self, ground_truth_batch: List[List], predictions_dict: Dict) -> Dict:
    return None


class TextGenRelevanceEvaluator(BaseTextGenerationEvaluator):
  """Measures how relevant the generated response was to the question specified."""

  def __init__(
      self,
      clarifai_pat: str,
      clarifai_model_url: str = DEFAULT_TEXT_GEN_JUDGE_LLM_URL,
  ):
    super().__init__(
        clarifai_pat=clarifai_pat,
        description="Measures how relevant the generated response was to the question specified.",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=
        "1. Set constraints on the length or scope of the response to maintain focus. \n\
          2. Clearly define what the model should focus on in its response",
        examples=None,
        library="uptrain",
        unit=DataTypes.float_type,
        clarifai_model_url=clarifai_model_url,
    )

  def evaluate(
      self,
      query_batch: List[str],
      predictions_batch: List[str],
      ground_truth_batch: List[str] = None,
      context_batch: List[str] = None,
  ) -> Tuple[List, float, List]:
    """
        This method evaluates the relevance of the generated text with the ground truth text
        Args:
            query_batch (List[str]): A list of queries
            predictions_batch (List[str]): A list of predictions
        Returns:
            List: Per sample score
            float: The average score
            List: The explanations for each sample
        """
    data = self.batch_to_uptrain_inputs(query_batch, predictions_batch)
    eval_llm = EvalLLM(self.settings)
    results = eval_llm.evaluate(data=data, checks=[Evals.RESPONSE_RELEVANCE])
    metric_scores = []
    explanations = []
    for result in results:
      metric_scores.append(
          round(result["score_response_relevance"], 4)
          if result["score_response_relevance"] is not None else 0)
      expln = result["explanation_response_relevance"]
      expln = (expln["Reasoning"] if isinstance(expln, dict) and "Reasoning" in expln else expln)
      explanations.append(expln)
    return metric_scores, round(sum(metric_scores) / len(metric_scores), 4), explanations

  def get_graph_data(self, ground_truth_batch: List[List], predictions_dict: Dict) -> None:
    return None


class TextGenValidityEvaluator(BaseTextGenerationEvaluator):
  """Checks if the response generated is valid or not. A response is considered to be valid if it contains any information."""

  def __init__(
      self,
      clarifai_pat: str,
      clarifai_model_url: str = DEFAULT_TEXT_GEN_JUDGE_LLM_URL,
  ):
    super().__init__(
        clarifai_pat=clarifai_pat,
        description=
        "Checks if the response generated is valid or not. A response is considered to be valid if it contains any information.",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action="1. Prompt the llm to provide explanation to questions asked \n\
          2. Provide some context / background information in the prompt \n\
          3. Prompt to answer the reasoning in bullet points",
        examples=None,
        library="uptrain",
        unit=DataTypes.float_type,
        clarifai_model_url=clarifai_model_url,
    )

  def evaluate(
      self,
      query_batch: List[str],
      predictions_batch: List[str],
      ground_truth_batch: List[str] = None,
      context_batch: List[str] = None,
  ) -> Tuple[List, float, List]:
    """
        This method evaluates the validity of the predicted text
        Args:
            query_batch (List[str]): A list of queries
            predictions_batch (List[str]): A list of predictions
            ground_truth_batch (List[str]): A list of ground truth labels
        Returns:
            List: Per sample score
            float: The average score
            List: The explanations for each sample
        """
    data = self.batch_to_uptrain_inputs(query_batch, predictions_batch, ground_truth_batch)
    eval_llm = EvalLLM(self.settings)
    results = eval_llm.evaluate(data=data, checks=[Evals.VALID_RESPONSE])
    metric_scores = []
    explanations = []
    for result in results:
      metric_scores.append(
          round(result["score_valid_response"], 4)
          if result["score_valid_response"] is not None else 0)
      expln = result["explanation_valid_response"]
      expln = (expln["Reasoning"] if isinstance(expln, dict) and "Reasoning" in expln else expln)
      explanations.append(expln)
    return metric_scores, round(sum(metric_scores) / len(metric_scores), 4), explanations

  def get_graph_data(self, ground_truth_batch: List[List], predictions_dict: Dict) -> None:
    return None
