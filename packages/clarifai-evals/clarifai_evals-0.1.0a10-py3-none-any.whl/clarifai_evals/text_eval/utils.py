from typing import Dict, List

import numpy as np
from sklearn.preprocessing import OneHotEncoder

from clarifai_evals.constant import CLASSIFICATION_GT_THRESHOLD


def get_prediction_encodings(prediction_batch: List[List], available_labels: List) -> Dict:
  """
    This function takes in the prediction batch and available labels and returns the confidence scores, vector encoding and onehot encoding of the predictions.
    Args:
        prediction_batch (List[List]): A list of lists containing the predictions
        available_labels (List): A list of available labels
    Returns:
        predictions_dict (Dict): A dictionary containing the confidence scores, vector encoding and onehot encoding of the predictions
    """
  predictions_dict = dict()
  predictions_dict["confidence_scores"] = np.array(prediction_batch)
  predictions_dict["vector_encoding"] = np.argmax(prediction_batch, axis=1)
  predictions_dict["onehot_encoding"] = onehot_encode(predictions_dict["confidence_scores"],
                                                      available_labels)
  return predictions_dict


def onehot_encode(confidence_scores: List[List], available_labels) -> np.ndarray:
  """
    This function takes in the confidence scores and available labels and returns the onehot encoding of the predictions.
    Args:
        confidence_scores (List[List]): A list of lists containing the confidence scores of the predictions
        available_labels (List): A list of available labels
    Returns:
        onehot_encoder.transform(predictions_dict['vector_encoding']) (np.ndarray): The onehot encoding of the
    """
  onehot_encoder = OneHotEncoder()
  categorical_data = np.array(available_labels).reshape(-1, 1)
  onehot_encoder.fit(categorical_data)
  confidence_scores = np.array(confidence_scores)
  ## if not multilabel:
  # predictions_dict['onehot_encoding'] = onehot_encoder.transform(predictions_dict['vector_encoding'])
  ## if multilabel:
  onehot_preds = np.array(confidence_scores >= CLASSIFICATION_GT_THRESHOLD, dtype=int)
  return onehot_preds


def get_correctness(ground_truth_onehot: List[List], predictions_onehot: List[List]) -> np.ndarray:
  """
    This function takes in the ground truth onehot encoding and the predictions onehot encoding and returns if each prediction is correct or not.
    Args:
        ground_truth_onehot (List[List]): A list of lists containing the ground truth onehot encoding
        predictions_onehot (List[List]): A list of lists containing the predictions onehot encoding
    Returns:
        correctness (np.ndarray): An array containing the correctness of each prediction
    """
  ground_truth_onehot = np.array(ground_truth_onehot)
  predictions_onehot = np.array(predictions_onehot)
  tmp = np.array(predictions_onehot == ground_truth_onehot, dtype=int)
  tmp[np.where(ground_truth_onehot == 0)] = 0
  correctness = np.nan_to_num(
      np.sum(tmp, axis=1) / np.sum(ground_truth_onehot, axis=1)).astype(int)
  return correctness
