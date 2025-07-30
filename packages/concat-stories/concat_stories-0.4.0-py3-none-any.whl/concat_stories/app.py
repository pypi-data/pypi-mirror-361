import argparse
import subprocess
from loguru import logger
import sys
import shutil
from importlib.metadata import version

from concat_stories.snapchat_dl import SnapchatDL
from concat_stories.con_stories import ConcatStories


def is_ffmpeg_installed() -> bool:
  try:
    result = subprocess.run(
      ["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.returncode == 0
  except FileNotFoundError:
    return False


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "-u",
    "--username",
    help="Snapchat username ex. djkhaled305",
    type=str,
    required=True,
    dest="username",
  )
  parser.add_argument(
    "-o",
    "--output",
    help="Output video name ex. dj_khaled_stories",
    type=str,
    dest="output",
    metavar="OUTPUT_NAME",
  )
  parser.add_argument(
    "-r",
    "--resolution",
    help="Set video resolution (Default: 480x852)",
    type=str,
    metavar="WIDTHxHEIGHT",
    default="480x852",
    dest="resolution",
  )
  parser.add_argument(
    "-d",
    "--delete",
    help="Delete stories after download.",
    action="store_true",
    default=False,
    dest="delete",
  )
  parser.add_argument(
    "-w",
    "--wait",
    help="Wait for user to delete unwanted stories.",
    action="store_true",
    default=False,
    dest="wait",
  )
  parser.add_argument(
    "-l",
    "--limit-story",
    help="Set maximum number of stories to download.",
    type=int,
    default=-1,
    dest="limit_story",
    metavar="LIMIT",
  )
  parser.add_argument(
    "-v",
    "--verbose",
    help="FFmpeg output verbosity.",
    action="store_true",
    default=False,
    dest="verbose",
  )
  parser.add_argument(
    "--sleep-interval",
    help="Sleep between downloads in seconds. (Default: 1s)",
    type=int,
    default=1,
    dest="sleep_interval",
    metavar="INTERVAL",
  )
  parser.add_argument(
    "--image-duration",
    help="Set duration for image in seconds. (Default: 1s)",
    type=int,
    default=1,
    dest="loop_duration_image",
    metavar="DURATION",
  )
  parser.add_argument(
    "--version", action="version", version=f"%(prog)s {version('concat_stories')}"
  )

  if not is_ffmpeg_installed():
    logger.error("FFmpeg binary not found. Please install FFmpeg or add it to PATH.")
    logger.error("Download FFmpeg from https://ffmpeg.org/download.html")
    sys.exit(1)

  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

  args = parser.parse_args()

  dirty_res: str = args.resolution.split("x")
  if len(dirty_res) != 2 or not all(res.isdigit() for res in dirty_res):
    logger.error(
      "Invalid resolution format. Use WIDTHxHEIGHT (e.g., 480x852). Using default resolution (480x852)."
    )
    resolution = None
  else:
    resolution = (int(dirty_res[0]), int(dirty_res[1]))

  try:
    sorted_stories = SnapchatDL(
      sleep_interval=args.sleep_interval, limit_story=args.limit_story
    ).download(args.username)

    # We know sorted_stories is not empty
    dir_path = sorted_stories[0].rsplit("/", 1)[0]

    folder_name = dir_path.split("/")[-1]
    output_name = args.output or folder_name

    if args.wait:
      logger.info("Press Enter to continue after deleting unwanted stories.")
      logger.info(f"Location of downloaded stories: {dir_path}")
      input("Press Enter to continue...")

    concat_stories = ConcatStories(
      sorted_stories,
      output_name,
      resolution,
      loop_duration_image=args.loop_duration_image,
      is_quiet=not args.verbose,
    )
    concat_stories.concat()

    if args.delete:
      shutil.rmtree(dir_path)
      logger.info(f"Stories deleted from {dir_path}")
  except KeyboardInterrupt:
    logger.info("Process interrupted by user.")
  except Exception as e:
    logger.error(f"An error occurred: {e}")
    sys.exit(1)


if __name__ == "__main__":
  sys.exit(main())
