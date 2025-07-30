import ffmpeg
from ffmpeg.nodes import FilterableStream
import os
from loguru import logger

RESOLUTION = (480, 852)
FRAMERATE = 30


class ConcatStories:
  def __init__(
    self,
    sorted_stories: list[str],
    output: str,
    resolution: tuple[int, int] | None = RESOLUTION,
    loop_duration_image: int = 1,
    is_quiet: bool = True,
  ):
    self.stories = sorted_stories
    self.output = output
    self.resolution = resolution if resolution else RESOLUTION
    self.loop_duration_image = loop_duration_image
    self.is_quiet = is_quiet

  def _fix_aspect_ratio(self, stream: FilterableStream) -> FilterableStream:
    stream = ffmpeg.filter_(
      stream["v"],
      "scale",
      width=self.resolution[0],
      height=self.resolution[1],
      force_original_aspect_ratio="decrease",
    )
    stream = ffmpeg.filter_(
      stream,
      "pad",
      width=self.resolution[0],
      height=self.resolution[1],
      x="(ow-iw)/2",
      y="(oh-ih)/2",
      color="black",
    )
    return stream

  def concat(self) -> None:
    input_streams_spread = []

    for path in self.stories:
      if not os.path.exists(path):
        continue

      if path.endswith(".mp4"):
        stream = ffmpeg.input(path)
        probe = ffmpeg.probe(path)

        stream_adjusted = self._fix_aspect_ratio(stream)
        if len(probe["streams"]) < 2:
          empty_audio = ffmpeg.input(
            "anullsrc", f="lavfi", t=probe["streams"][0]["duration"]
          )
          input_streams_spread.extend([stream_adjusted, empty_audio])
        else:
          input_streams_spread.extend([stream_adjusted, stream["a"]])
      else:
        stream = ffmpeg.input(
          path,
          t=self.loop_duration_image,
          loop=1,
          framerate=FRAMERATE,
        )
        stream = self._fix_aspect_ratio(stream)

        empty_audio = ffmpeg.input("anullsrc", f="lavfi", t=self.loop_duration_image)
        input_streams_spread.extend([stream, empty_audio])

    joined = ffmpeg.concat(*input_streams_spread, v=1, a=1, unsafe=True).node
    loglevel = "quiet" if self.is_quiet else "info"
    ffmpeg.output(
      joined[0], joined[1], os.path.join(".", self.output + ".mp4"), loglevel=loglevel
    ).run()
    logger.info(f"Stories concatenated to {self.output}.mp4")
