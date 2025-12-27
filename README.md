# CompressVids

This is a video compression wrapper for python using the `ffmpeg` library. While it can compress a single video file, it also allows compressing all videos in a directory (recursively). Non-video files in the directory are directly copied to the specified directory.

**NOTE**:
- This repository is being archived.
- The tool is available as a part of the Unified [CompressMedia](https://github.com/nitinkamra1992/CompressMedia) tool.

## Compatibility
The tool has been written for Ubuntu and tested on Python v3.8 and above but should be compatible with other versions of python too.

## Dependencies
The tool requires python3 (generally present by default). Also install the other dependencies:

```
sudo apt update
sudo apt install ffmpeg libmediainfo-dev
pip install pymediainfo
```

## Usage

The tool can be run as a Python script, e.g.:
```
python3 compress_vids.py -d <data_dir> -o <out_dir> -m 5000000 -rec -v -vcodec libx265 -crf 24 -s half
```
To check the script parameters in detail, type:
```
python3 compress_vids.py --help
```

**Notes**:
1. The tool only processes video files. All other unsupported files are copied over directly. Any file smaller than `--minsize` is copied over directly. If `-rec` is not specified, all subdirectories are copied directly to the output directory.
2. You can pass the video scaling arguments via the convenient `-s` (or `--scale`) parameter or via the `ffmpeg` style scale string `-vf` (or `--vf`). If `--scale` is passed, it will override `--vf`.
