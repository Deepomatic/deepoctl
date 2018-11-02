# Deepomatic Controler

This controler have been made in order to help you interacting with our services via the command line.

[![Build Status](https://travis-ci.com/Deepomatic/deepoctl.svg?branch=master)](https://travis-ci.com/Deepomatic/deepoctl)

## Installation

Requirements: Python 2.7+ or 3.4+

```
pip install git+https://github.com/deepomatic/deepoctl@v0.1 --process-dependency-links
```

## Setup

In order to use models which are deployed in our cloud, you will need to set your application ID and API key in `DEEPOMATIC_APP_ID` and `DEEPOMATIC_API_KEY` environment variables, respectively.

## Commands

### `infer`: Performing inference only

"Inference" is the action of running your algorithm. Performing inference only will generate JSON files with inference results next to your files.

```sh
deepoctl infer your/path/to/a/file/or/directory --recognition_id 123
```

- The path `your/path/to/a/file/or/directory` can either be an image, a video or a directory. In the later case, `deepoctl` will look for supported images and videos in the directory.
- `123` is your recognition version ID that you have trained.

The generated files will have the same name as the original one with a suffix `.rXXX` (`XXX` being the `recognition_id`) and a `.json` extension.

### `draw`: Drawing bounding boxes

You can also call the `draw` command to additionally generate images and videos with tags and bounding boxes overlayed. The generated media will have the same suffix as for the `infer` command.

```sh
deepoctl draw your/path/to/a/file/or/directory --recognition_id 123
```

## Bugs

Please send bug reports to support@deepomatic.com
