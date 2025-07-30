# Concat Stories 
[![PyPI Downloads](https://static.pepy.tech/badge/concat-stories)](https://pepy.tech/projects/concat-stories) 
[![Version](https://img.shields.io/pypi/v/concat-stories)](https://pypi.org/project/concat-stories/)
[![License](https://img.shields.io/pypi/l/concat-stories)](https://pypi.org/project/concat-stories/)

Concat Stories is a Python package that allows you to download Snapchat stories and merge them into a single video file.

## Features

- Download Snapchat stories
- Merge multiple stories into one video
- Easy to use

## Installation

You can install Concat Stories CLI using pip:

```bash
pip install concat-stories
```

or using UV:

```bash
uv tool install concat-stories
```

## Usage

Here is an example of how to use Concat Stories:

```
usage: concat-stories [-h] -u USERNAME [-o OUTPUT_NAME] [-r WIDTHxHEIGHT] [-d] [-w] [-l LIMIT] [-v] [--sleep-interval INTERVAL] [--image-duration DURATION] [--version]

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Snapchat username ex. djkhaled305
  -o OUTPUT_NAME, --output OUTPUT_NAME
                        Output video name ex. dj_khaled_stories
  -r WIDTHxHEIGHT, --resolution WIDTHxHEIGHT
                        Set video resolution (Default: 480x852)
  -d, --delete          Delete stories after download.
  -w, --wait            Wait for user to delete unwanted stories.
  -l LIMIT, --limit-story LIMIT
                        Set maximum number of stories to download.
  -v, --verbose         FFmpeg output verbosity.
  --sleep-interval INTERVAL
                        Sleep between downloads in seconds. (Default: 1s)
  --image-duration DURATION
                        Set duration for image in seconds. (Default: 1s)
  --version             show program's version number and exit
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
