from typing import Any, Dict, List, Tuple

import jiwer
from clarifai.client.input import Inputs
from clarifai.client.model import Model
from sklearn.metrics.pairwise import cosine_similarity

from clarifai_evals.constant import DataTypes, VisualizationTypes


class BaseOCRGTEvaluator:
  '''Base class for OCR Ground Truth Evaluators'''

  def __init__(
      self,
      description="It evaluates the OCR detections of the model by comparing them with the ground truth OCR texts.",
      has_explanation=False,
      aggregation_type=None,
      graph_type=None,
      corrective_action=None,
      examples=None,
      library=None,
      unit=None,
      pat=None,
      embedding_model="https://clarifai.com/hapxpu3a2wn7/sentence-transformers-embedding/models/sentence-transformers-embedding",
  ):
    """
    Args:
        description (str): The description of the evaluator
        has_explanation (bool): Whether the evaluator has an explanation
        aggregation_type (str): The type of aggregation for the evaluator - ['mean']
        graph_type (str): The type of graph for the evaluator - ['bar', 'histogram', 'confusion matrix', 'precision-recall curve', None]
        corrective_action (str): The corrective action for the evaluator
        examples (List): The examples for the evaluator
        library (str): The library used for the evaluator - ['clarifai', 'uptrain', 'sklearn', 'jiwer']
        unit (str): The unit of the evaluator - ['percentage', 'float']
        pat (str): Clarifai PAT for the evaluator
        embedding_model (str): The embedding model for the evaluator
    """
    self.description = description
    self.has_explanation = has_explanation
    self.aggregation_type = aggregation_type
    self.graph_type = graph_type
    self.corrective_action = corrective_action
    self.examples = examples
    self.library = library
    self.unit = unit
    self.embedding_model = Model(url=embedding_model, pat=pat)
    self.pat = pat

  def evaluate(self, predictions: List, ground_truth: List) -> Tuple[Dict, Dict]:
    return NotImplementedError("Override this method in the child class")

  def get_graph_data(self, result: List) -> Any:
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


class ComputeWordErrorRates(BaseOCRGTEvaluator):

  def __init__(self, pat: str = None, embedding_model: str = None):
    super().__init__(
        description=
        "It computes Word Error Rate in the OCR detections of the model by comparing them with the ground truth OCR texts.",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        pat=pat,
        embedding_model=embedding_model,
        examples=None,
        library="jiwer",
        unit=DataTypes.float_type,
    )

  def evaluate(self, predictions: List, ground_truth: List) -> Tuple[float, List]:
    persample = {
        "match_error_rate": [],
        "word_information_lost": [],
        "word_information_preserved": [],
        "word_error_rate": [],
    }
    total = len(predictions)
    for i in range(total):
      output = jiwer.process_words(ground_truth[i], predictions[i])
      persample["match_error_rate"].append(round(output.mer, 4))
      persample["word_information_lost"].append(round(output.wil, 4))
      persample["word_information_preserved"].append(round(output.wip, 4))
      persample["word_error_rate"].append(round(output.wer, 4))
    summary = {
        "match_error_rate":
            round(sum(persample["match_error_rate"]) / total, 4),
        "word_information_lost":
            round(sum(persample["word_information_lost"]) / total, 4),
        "word_information_preserved":
            round(sum(persample["word_information_preserved"]) / total, 4),
        "word_error_rate":
            round(sum(persample["word_error_rate"]) / total, 4),
    }

    return summary, persample

  def get_graph_data(self, result: List) -> Any:
    return None


class ComputeCharacterErrorRates(BaseOCRGTEvaluator):

  def __init__(self, pat: str = None, embedding_model: str = None):
    super().__init__(
        description=
        "It computes Character Error Rate in the OCR detections of the model by comparing them with the ground truth OCR texts.",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        pat=pat,
        embedding_model=embedding_model,
        examples=None,
        library="jiwer",
        unit=DataTypes.float_type,
    )

  def evaluate(self, predictions: List, ground_truth: List) -> Tuple[float, List]:
    total = len(predictions)
    persample = {
        "character_error_rate": [],
    }
    for i in range(total):
      cer = jiwer.cer(ground_truth[i], predictions[i])
      persample["character_error_rate"].append(round(cer, 4))
    summary = {
        "character_error_rate": round(sum(persample["character_error_rate"]) / total, 4),
    }
    return summary, persample

  def get_graph_data(self, result: List) -> Any:
    return None


class ComputeSemanticSimilarity(BaseOCRGTEvaluator):

  def __init__(self, pat: str = None, embedding_model: str = None):
    super().__init__(
        description=
        "It computes Semantic Similarity in the OCR detections of the model by comparing them with the ground truth OCR texts.",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        pat=pat,
        embedding_model=embedding_model,
        examples=None,
        library="sklearn",
        unit=DataTypes.float_type,
    )

  def compute_embeddings_from_clarifai(self, predictions: List,
                                       ground_truth: List) -> Tuple[List, List]:
    preds_batch = []
    input_obj = Inputs(pat=self.pat)
    preds_batch = [
        input_obj.get_text_input(input_id=str(i), raw_text=pred)
        for i, pred in enumerate(predictions)
    ]
    gt_batch = [
        input_obj.get_text_input(input_id=str(i), raw_text=gt) for i, gt in enumerate(ground_truth)
    ]

    preds_embeds = []
    gt_embeds = []

    try:
      resp = self.embedding_model.predict(inputs=preds_batch)
      preds_embeds = [list(output.data.embeddings[0].vector) for output in resp.outputs]
      resp = self.embedding_model.predict(inputs=gt_batch)
      gt_embeds = [list(output.data.embeddings[0].vector) for output in resp.outputs]
    except Exception as e:
      error_msg = f"Error in processing computing embeddings for the response: {e}"
      raise error_msg

    return preds_embeds, gt_embeds

  def evaluate(self, predictions: List, ground_truth: List) -> Tuple[float, List]:

    preds_embeds, gt_embeds = self.compute_embeddings_from_clarifai(predictions, ground_truth)
    total = len(predictions)
    persample = {
        "cosine_similarity": [],
    }
    for i in range(total):
      cosine_sim = cosine_similarity([preds_embeds[i]], [gt_embeds[i]])
      persample["cosine_similarity"].append(round(cosine_sim[0][0], 4))
    summary = {
        "cosine_similarity": round(sum(persample["cosine_similarity"]) / total, 4),
    }
    return summary, persample

  def get_graph_data(self, result: List) -> Any:
    return None


class ComputeClassicalMetrics(BaseOCRGTEvaluator):

  def __init__(self, pat: str = None, embedding_model: str = None):
    super().__init__(
        description=
        "It computes the metrics in the OCR detections of the model by comparing them with the ground truth OCR texts.",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        library="sklearn",
        unit=DataTypes.float_type,
        pat=pat,
        embedding_model=embedding_model)

  def evaluate(self, predictions: List, ground_truth: List) -> Tuple[float, List]:

    precision_list = []
    recall_list = []
    f1_score_list = []

    for i in range(len(predictions)):
      gt_set = set(ground_truth[i])
      pred_set = set(predictions[i])
      common_words = gt_set.intersection(pred_set)
      num_common = len(common_words)

      precision = num_common / len(pred_set) if pred_set else 0
      recall = num_common / len(gt_set) if gt_set else 0
      f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0

      precision_list.append(round(precision, 4))
      recall_list.append(round(recall, 4))
      f1_score_list.append(round(f1_score, 4))

    res_avg = {
        "precision": round(sum(precision_list) / len(precision_list), 4),
        "recall": round(sum(recall_list) / len(recall_list), 4),
        "f1_score": round(sum(f1_score_list) / len(f1_score_list), 4),
    }

    res_per_sample = {
        "precision": precision_list,
        "recall": recall_list,
        "f1_score": f1_score_list,
    }

    return res_avg, res_per_sample

  def get_graph_data(self, result: List) -> Any:
    return None
