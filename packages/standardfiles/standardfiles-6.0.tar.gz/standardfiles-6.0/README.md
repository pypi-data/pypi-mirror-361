standardfiles
=============

standardfiles is a simple python script to convert video, audio and images to
*standard files*.

| Type file     | format       | format lossless |
|---------------|--------------|-----------------|
| audio         | aac          | flac            |
| video         | mkv/aac/h264 | mkv/flac/ffv1   |
| image         | ff.bz2       |                 |
| image (valid) | png          |                 |


Also clear all metadata and check the standard formats.

In the lossless format don't convert. And you can't convert to lossless format
(it doesn't make sense).

Packaging
=========

- **Gentoo:** [imperium](https://gitlab.com/HansvonHohenstaufen/imperium) repository.

Requirements
============

In order to use you need install:

- `bzip2`
- `dwebp`
- `exiftool`
- `farbfeld`
- `ffmpeg`
- `imagemagick`
- `metaflac`

Installation
============

To install the command line utility, run:

```
python3 -m build
pip install dist/*.whl
```
