import json
import logging
from typing import Dict, List, Tuple

import numpy as np
from clarifai.client.input import Inputs
from clarifai.client.model import Model
from sklearn.preprocessing import OneHotEncoder

from clarifai_evals.constant import DataTypes, VisualizationTypes
from clarifai_evals.text_eval.base_eval import BaseLLMJudgeTextEvaluator
from clarifai_evals.text_eval.prompt_templates import (CLASSIFIER_JUDGE_PROMPT,
                                                       CLASSIFIER_JUDGE_PROMPT_WITH_CONTEXT)
from clarifai_evals.text_eval.text_classification_eval.eval_with_gt.evaluate import \
    TextLabelAccuracyGTEvaluator
from clarifai_evals.text_eval.utils import get_correctness, onehot_encode


class LLMJudgeTextClassificationEvaluator(BaseLLMJudgeTextEvaluator):
  """This class is used to evaluate text classification models using LLM as the judge when ground truth is not available"""

  def __init__(
      self,
      clarifai_pat: str,
      clarifai_model_url: str = "https://clarifai.com/openai/chat-completion/models/GPT-4",
  ):
    super().__init__(
        clarifai_pat=clarifai_pat,
        clarifai_model_url=clarifai_model_url,
        description="LLM Judge Text Classification Evaluator",
        task_type="classification",
        has_explanation=False,
        aggregation_type="mean",
        graph_type=VisualizationTypes.undefined,
        corrective_action=None,
        examples=None,
        library="clarifai",
        unit=DataTypes.float_type,
        judge_prompt=CLASSIFIER_JUDGE_PROMPT,
        batch_size=32,
    )
    self.onehot_encoder = OneHotEncoder()

  def evaluate(
      self,
      prediction_batch: Dict,
      available_labels: List,
      query_batch: List,
      context_batch: List = None,
  ) -> Tuple[List, List, float]:
    """This method distributes the evaluation across multiple threads
        Args:
            prediction_batch Dict: A dictionary containing the predictions in the form of one-hot encodings, confidence scores and vector encodings
            available_labels (List): A list of available labels
            query_batch (List): A list of queries
            context_batch (List): A list of contexts
        Returns:
            Tuple[List, List, float]: The judge predictions, correctness and accuracy
        """
    prediction_onehot = prediction_batch["onehot_encoding"]
    logging.info("Evaluating with LLM as Judge " + self.clarifai_model_url)
    self.model = Model(url=self.clarifai_model_url, pat=self.clarifai_pat)
    # preds_onehot = onehot_encode(prediction_batch, available_labels)
    self.onehot_encoder.fit(np.array(available_labels).reshape(-1, 1))
    self.judge_prompt = (CLASSIFIER_JUDGE_PROMPT_WITH_CONTEXT
                         if context_batch is not None else CLASSIFIER_JUDGE_PROMPT)
    results_batch = {}
    results_batch["correctness"] = []
    results_batch["judge_preds"] = []
    results_batch["judge_labels"] = []
    result = self._evaluate_with_judge(prediction_onehot, available_labels, query_batch,
                                       context_batch)

    results_batch["judge_preds"].extend(result[0])
    results_batch["correctness"].extend(result[1])
    results_batch["judge_labels"].extend(result[2])
    # self._evaluate_with_judge(prediction_batch, available_labels, query_batch, context_batch)
    acc_obj = TextLabelAccuracyGTEvaluator()
    perclass_acc, avg_acc, _ = acc_obj.evaluate(results_batch["judge_preds"], prediction_batch)
    return (
        results_batch["judge_labels"],
        results_batch["correctness"],
        perclass_acc,
        avg_acc,
    )

  def _evaluate_with_judge(
      self,
      prediction_batch: List[List],
      available_labels: List,
      query_batch: List,
      context_batch: List = None,
  ) -> Tuple[List, List, float]:
    """This method evaluates the model based on the given inputs
        Args:
            prediction_batch (List[List]): A list of lists containing the predictions
            available_labels (List): A list of available labels
            query_batch (List): A list of queries
            context_batch (List): A list of contexts
        Returns:
            Tuple[List, List, float]: The judge predictions, correctness and accuracy
        """
    correctness = []
    org_preds = np.array(prediction_batch)
    max_cats = len(available_labels)
    judge_preds = []
    judge_labels = []
    prompt_inputs = []
    for i in range(len(prediction_batch)):
      if context_batch is not None:
        edited_prompt = self.judge_prompt.format(
            labels=available_labels,
            x=query_batch[i],
            context=context_batch[i],
            max_cats=max_cats,
        )
      else:
        edited_prompt = self.judge_prompt.format(
            labels=available_labels, x=query_batch[i], max_cats=max_cats)
      inp = Inputs.get_text_input(input_id=str(i), raw_text=edited_prompt)
      prompt_inputs.append(inp)
    response = self.model.predict(prompt_inputs)

    for op in response.outputs:
      r = op.data.text.raw
      r = r.replace("\n", " ")
      # op_json = re.search(r"\{.*\}", r)[0]
      r = r.split("}", 1)[0].split("{", 1)[-1]
      op_json = "{" + r + "}"
      logging.info(f"\n**********\nop_json: {op_json}\n")
      op_json = json.loads(op_json)
      # onehot encode preds
      preds = self.onehot_encoder.transform(np.array(op_json["label"]).reshape(-1, 1)).toarray()
      preds = onehot_encode(preds, available_labels)
      preds_onehot = np.array(np.any(preds, axis=0), dtype=int)
      judge_preds.append(preds_onehot)
      judge_labels.append(op_json["label"])

    correctness = get_correctness(judge_preds, org_preds)
    sum(correctness)
    return np.array(judge_preds), np.array(correctness), judge_labels

  def get_graph_data(self, judge_preds: List, org_preds: Dict) -> dict:
    return None

    ### Keeping this code for reference when integrating with the Clarifai-web
    # """This method generates the graph data
    #     Args:
    #         judge_results (List): The judge results
    #         gt_results (List): The ground truth results
    #     Returns:
    #         dict: The graph data
    #     """
    # ## generate confusion matrix
    # acc_obj = TextLabelAccuracyGTEvaluator()
    # return acc_obj.get_graph_data(judge_preds, org_preds)
