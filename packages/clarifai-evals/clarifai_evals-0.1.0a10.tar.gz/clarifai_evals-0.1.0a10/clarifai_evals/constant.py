from enum import Enum

CLASSIFICATION_GT_THRESHOLD = 0.5
DEFAULT_TEXT_GEN_JUDGE_LLM = "GPT-4"
DEFAULT_TEXT_GEN_JUDGE_LLM_URL = ("https://clarifai.com/openai/chat-completion/models/GPT-4")
DEFAULT_BATCH_SIZE = 32


class VisualizationTypes(Enum):
  confusion_matrix = "CONFUSION_MATRIX"
  pr_curve = "PRECISION_RECALL_CURVE"
  roc_auc_curve = "ROC_AUC_CURVE"
  undefined = "VISUALIZATION_TYPE_NOT_SET"


class DataTypes(Enum):
  float_type = "FLOAT"
  int_type = "INT"
  string_type = "STRING"
  undefined = "DATA_TYPE_NOT_SET"


class TaskTypes(Enum):
  text_classification = "TEXT_CLASSIFICATION"
  image_classification = "TASK_TYPE_NOT_SET"
  image_object_detection = "TASK_TYPE_NOT_SET"
  image_segmentation = "TASK_TYPE_NOT_SET"
  text_generation = "TASK_TYPE_NOT_SET"
  image_ocr = "TASK_TYPE_NOT_SET"
