import argparse
import logging
import os
import sys
import traceback
from typing import List
from datetime import timedelta

from wai.logging import init_logging, set_logging_level, add_logging_level
from seppl.io import locate_files
from seppl.placeholders import load_user_defined_placeholders, placeholder_list, expand_placeholders
from adc.core import ENV_ADC_LOGLEVEL
from faster_whisper import WhisperModel


SRT = "adc-srt"

_logger = logging.getLogger(SRT)


def _seconds_to_timestamp(seconds: float) -> str:
    """
    Converts the fractional seconds into an SRT timestamp.

    :param seconds: the seconds to convert
    :type seconds: float
    :return: the generated string
    :rtype: str
    """
    td = timedelta(seconds=seconds)
    mm, ss = divmod(td.seconds, 60)
    hh, mm = divmod(mm, 60)
    result = "%d:%02d:%02d,%03d" % (hh, mm, ss, td.microseconds // 1000)
    return result


def generate_subtitles(paths: List[str], output: str = None, model_size: str = "base", device: str = "cpu",
                       compute_type: str = "int8", beam_size: int = 5, update_interval: int = 100):
    """
    Finds the files in the dir(s) and stores the full paths in text file(s).

    :param paths: the dir(s) to scan for files
    :type paths: list
    :param output: the output file to store the files in; when splitting, the split names get used as suffix (before .ext)
    :type output: str
    :param model_size: the fast-whisper model size to use
    :type model_size: str
    :param device: the device to run whisper on, e.g., "cuda" or "cpu"
    :type device: str
    :param compute_type: the data type to use for the computation, e.g., "float16" or "int8"
    :type compute_type: str
    :param beam_size: the size of the search beam
    :type beam_size: int
    :param update_interval: the number of segments when to output info logging messages during processing
    :type update_interval: int
    """
    all_paths = locate_files(paths, fail_if_empty=True, default_glob="*.wav")
    if len(all_paths) > 1:
        _logger.info("Found %d input files" % len(all_paths))

    _logger.info("Configuring model: %s/%s/%s" % (model_size, device, compute_type))
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    for path in all_paths:
        _logger.info("Processing: %s" % path)
        if output is None:
            path_srt = os.path.splitext(path)[0] + ".srt"
        else:
            path_srt = os.path.join(expand_placeholders(output), os.path.splitext(os.path.basename(path))[0] + ".srt")
        lines = []
        count = 0
        segments, info = model.transcribe(path, beam_size=beam_size)
        for segment in segments:
            count += 1
            start = _seconds_to_timestamp(segment.start)
            end = _seconds_to_timestamp(segment.end)
            text = segment.text.strip()
            lines.extend([
                str(count),
                start + " --> " + end,
                text,
                "",
            ])
            if count % update_interval == 0:
                _logger.info("%d segments processed..." % count)

        _logger.info("Total segments processed: %d" % count)
        _logger.info("Writing: %s" % path_srt)
        with open(path_srt, "w") as fp:
            fp.write("\n".join(lines))


def main(args=None):
    """
    The main method for parsing command-line arguments.

    :param args: the commandline arguments, uses sys.argv if not supplied
    :type args: list
    """
    init_logging(env_var=ENV_ADC_LOGLEVEL)
    parser = argparse.ArgumentParser(
        description="Tool for generating SRT subtitle files from video/audio files.",
        prog=SRT,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", metavar="FILE", help="The audio/video files to process; supports glob syntax. " + placeholder_list(input_based=False), default=None, type=str, required=True, nargs="+")
    parser.add_argument("-o", "--output", metavar="DIR", help="The directory to store the generated subtitle files in; places them in the same locations as the input files if not provided. " + placeholder_list(input_based=False), type=str, required=False, default=None)
    parser.add_argument("-m", "--model_size", type=str, help="The size of the whisper model to use, e.g., 'base' or 'large-v3'", required=False, default="base")
    parser.add_argument("-d", "--device", type=str, help="The device to run on, e.g., 'cuda' or 'cpu'", required=False, default="cpu")
    parser.add_argument("-c", "--compute_type", type=str, help="The compute type to use, e.g., 'float16' or 'int8'", required=False, default="int8")
    parser.add_argument("-b", "--beam_size", type=int, help="The beam size to use for decoding", required=False, default=5)
    parser.add_argument("-u", "--update_interval", type=int, help="The number of segments when to output info logging messages during processing", required=False, default=100)
    parser.add_argument("--placeholders", metavar="FILE", help="The file with custom placeholders to load (format: key=value).", required=False, default=None, type=str)
    add_logging_level(parser)
    parsed = parser.parse_args(args=args)
    set_logging_level(_logger, parsed.logging_level)
    if parsed.placeholders is not None:
        if not os.path.exists(parsed.placeholders):
            _logger.error("Placeholder file not found: %s" % parsed.placeholders)
        else:
            _logger.info("Loading custom placeholders from: %s" % parsed.placeholders)
            load_user_defined_placeholders(parsed.placeholders)
    generate_subtitles(parsed.input, output=parsed.output, model_size=parsed.model_size, device=parsed.device,
                       compute_type=parsed.compute_type, beam_size=parsed.beam_size)


def sys_main() -> int:
    """
    Runs the main function using the system cli arguments, and
    returns a system error code.

    :return: 0 for success, 1 for failure.
    """
    try:
        main()
        return 0
    except Exception:
        traceback.print_exc()
        print("options: %s" % str(sys.argv[1:]), file=sys.stderr)
        return 1


if __name__ == '__main__':
    main()
