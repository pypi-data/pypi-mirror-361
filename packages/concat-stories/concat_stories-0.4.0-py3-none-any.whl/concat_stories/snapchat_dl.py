import concurrent.futures
from datetime import datetime, timezone
import json
import os
import re
import time
import requests
from loguru import logger


class NoStoriesFound(Exception):
  """No stories found."""

  pass


class APIResponseError(Exception):
  """Invalid API Response"""

  pass


MEDIA_TYPE = ["jpg", "mp4"]


class SnapchatDL:
  """Interact with Snapchat API to download story."""

  def __init__(
    self, directory_prefix="stories", max_workers=2, limit_story=-1, sleep_interval=1
  ):
    self.directory_prefix = os.path.abspath(os.path.normpath(directory_prefix))
    self.max_workers = max_workers
    self.limit_story = limit_story
    self.sleep_interval = sleep_interval
    self.endpoint_web = "https://www.snapchat.com/add/{}/"
    self.regexp_web_json = (
      r'<script\s*id="__NEXT_DATA__"\s*type="application\/json">([^<]+)<\/script>'
    )
    self.reaponse_ok = requests.codes.get("ok")

  def _api_response(self, username: str) -> str:
    web_url = self.endpoint_web.format(username)
    return requests.get(
      web_url,
      headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
      },
    ).text

  def _web_fetch_story(self, username: str) -> list[dict]:
    """Download user stories from Web.

    Args:
        username (str): Snapchat `username`

    Raises:
        APIResponseError: API Error

    Returns:
        list: list of stories
    """
    response = self._api_response(username)
    response_json_raw = re.findall(self.regexp_web_json, response)

    try:
      response_json = json.loads(response_json_raw[0])

      def util_web_story(content: dict):
        if "story" in content["props"]["pageProps"]:
          return content["props"]["pageProps"]["story"]["snapList"]
        return list()

      stories = util_web_story(response_json)
      return stories

    except (IndexError, KeyError, ValueError):
      raise APIResponseError

  def _download_url(self, url: str, dest: str, sleep_interval: int):
    """Download URL to destionation path.

    Args:
        url (str): url to download
        dest (str): absolute path to destination
        sleep_interval (int): sleep interval

    Raises:
        response.raise_for_status: if response is 4** or 50*
        FileExistsError: if file is already downloaded
    """
    if len(os.path.dirname(dest)) > 0:
      os.makedirs(os.path.dirname(dest), exist_ok=True)

    """Rate limiting."""
    time.sleep(sleep_interval)

    try:
      response = requests.get(url, stream=True, timeout=10)
    except requests.exceptions.ConnectTimeout:
      response = requests.get(url, stream=True, timeout=10)

    if response.status_code != requests.codes.get("ok"):
      response.raise_for_status()

    if os.path.isfile(dest) and os.path.getsize(dest) == response.headers.get(
      "content-length"
    ):
      raise FileExistsError

    if os.path.isfile(dest) and os.path.getsize(dest) == 0:
      os.remove(dest)
    try:
      with open(dest, "xb") as handle:
        try:
          for data in response.iter_content(chunk_size=4194304):
            handle.write(data)
          handle.close()
        except requests.exceptions.RequestException as e:
          logger.error(e)
    except FileExistsError:
      pass

  def download(self, username: str) -> list[str]:
    """Download Snapchat Story for `username`.

    Args:
        username (str): Snapchat `username`

    Returns:
        list: list of downloaded sorted stories by timestamp
    """
    stories = self._web_fetch_story(username)

    if len(stories) == 0:
      logger.info(f"\033[91m{username}\033[0m has no stories")
      raise NoStoriesFound

    if self.limit_story > -1:
      stories = stories[0 : self.limit_story]

    logger.info(f"[+] {username} has {len(stories)} stories")

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)

    now_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"{username}_{now_date}"
    dir_path = os.path.join(self.directory_prefix, folder_name)

    sorted_stories = []

    try:
      for media in stories:
        snap_id = media["snapId"]["value"]
        media_url = media["snapUrls"]["mediaUrl"]
        media_type = media["snapMediaType"]
        timestamp = int(media["timestampInSec"]["value"])

        filename = datetime.fromtimestamp(timestamp, timezone.utc).strftime(
          f"%Y-%m-%d_%H-%M-%S_{username}_{snap_id}.{MEDIA_TYPE[media_type]}"
        )

        media_output = os.path.join(dir_path, filename)
        executor.submit(
          self._download_url, media_url, media_output, self.sleep_interval
        )

        sorted_stories.append((timestamp, media_output))

    except KeyboardInterrupt:
      executor.shutdown(wait=False)

    # wait for all downloads to finish
    executor.shutdown(wait=True)
    logger.info(f"[✔] {username} stories downloaded")

    sorted_stories.sort(key=lambda x: x[0])
    sorted_stories = [story[1] for story in sorted_stories]
    return sorted_stories
