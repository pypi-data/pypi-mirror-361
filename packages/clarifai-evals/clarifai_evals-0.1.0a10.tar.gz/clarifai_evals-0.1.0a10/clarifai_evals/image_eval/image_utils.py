import base64
import logging
from io import BytesIO
from typing import List, Tuple

import requests
from clarifai_grpc.grpc.api import resources_pb2
from PIL import Image


def get_image_dimensions(
    image_data: List[resources_pb2.Data],
    clarifai_pat: str = None,
) -> List[Tuple[int, int]]:
  """Get the dimensions of the images in the batch.

    Args:
        image_data (List[resources_pb2.Data]): A list of Data containing the images.

    Returns:
        List[Tuple[int, int]]: A list of tuples containing the width and height of each image.
    """

  def is_base64(data: bytes) -> bool:
    """Check if the given data is already a Base64-encoded string."""
    try:
      decoded = base64.b64decode(data, validate=True)
      re_encoded = base64.b64encode(decoded)
      return re_encoded == data.strip()
    except Exception:
      return False

  def get_dims_from_base64(img_bytes):
    try:
      if is_base64(img_bytes):
        img_bytes = base64.b64decode(img_bytes)
      image = Image.open(BytesIO(img_bytes))
      return image.size  # (width, height)
    except Exception as e:
      print(f"Error: {e}")
      logging.error(f"Failed to decode base64 image: {e}")
      return None

  def download_image(url: str) -> Image.Image:
    headers = {
        "Authorization": f"Bearer {clarifai_pat}",
    }
    response = requests.get(url, headers=headers)
    image = Image.open(BytesIO(response.content))
    return image

  def get_dims_from_url(url):
    try:
      # Download the image from the URL
      image = download_image(url)
      return image.size  # (width, height)
    except Exception as e:
      print(f"Error: {e}")
      logging.error(f"Failed to download image from URL: {url}, error: {e}")
      return None

  dimensions = []
  for idata in image_data:
    if idata.image.image_info.width and idata.image.image_info.height:
      dimensions.append((idata.image.image_info.width, idata.image.image_info.height))
    elif idata.image.base64:
      # Decode the base64 string and get dimensions
      dims = get_dims_from_base64(idata.image.base64)
      if dims:
        dimensions.append(dims)
    elif idata.image.url:
      # Download the image from the URL and get dimensions
      dims = get_dims_from_url(idata.image.url)
      if dims:
        dimensions.append(dims)
    else:
      raise ValueError("Image data must contain either base64 or URL.")

  return dimensions
