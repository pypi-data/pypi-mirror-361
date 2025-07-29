# audio-dataset-converter-faster-whisper
Adds support for transcribing audio files (.wav, .mp3) using [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

## Installation

```bash
pip install git+https://github.com/waikato-llm/audio-dataset-converter.git
pip install git+https://github.com/waikato-llm/audio-dataset-converter-faster-whisper.git
```

## Tools

### Generating SRT subtitles

```
usage: adc-srt [-h] -i FILE [FILE ...] [-o DIR] [-m MODEL_SIZE] [-d DEVICE]
               [-c COMPUTE_TYPE] [-b BEAM_SIZE] [-u UPDATE_INTERVAL]
               [--placeholders FILE] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

Tool for generating SRT subtitle files from video/audio files.

options:
  -h, --help            show this help message and exit
  -i FILE [FILE ...], --input FILE [FILE ...]
                        The audio/video files to process; supports glob
                        syntax. Supported placeholders: {HOME}, {CWD}, {TMP}
                        (default: None)
  -o DIR, --output DIR  The directory to store the generated subtitle files
                        in; places them in the same locations as the input
                        files if not provided. Supported placeholders: {HOME},
                        {CWD}, {TMP} (default: None)
  -m MODEL_SIZE, --model_size MODEL_SIZE
                        The size of the whisper model to use, e.g., 'base' or
                        'large-v3' (default: base)
  -d DEVICE, --device DEVICE
                        The device to run on, e.g., 'cuda' or 'cpu' (default:
                        cpu)
  -c COMPUTE_TYPE, --compute_type COMPUTE_TYPE
                        The compute type to use, e.g., 'float16' or 'int8'
                        (default: int8)
  -b BEAM_SIZE, --beam_size BEAM_SIZE
                        The beam size to use for decoding (default: 5)
  -u UPDATE_INTERVAL, --update_interval UPDATE_INTERVAL
                        The number of segments when to output info logging
                        messages during processing (default: 100)
  --placeholders FILE   The file with custom placeholders to load (format:
                        key=value). (default: None)
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
```

## Plugins

See [here](plugins/README.md) for an overview of all plugins.
