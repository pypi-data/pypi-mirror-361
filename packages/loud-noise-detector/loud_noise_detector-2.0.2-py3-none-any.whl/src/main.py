#!/usr/bin/env python3
import argparse
import os
import sys
from typing import List

from dotenv import load_dotenv

from src.detector.audio_detector import AudioDetector
from src.notifiers.base import BaseNotifier
from src.notifiers.slack import SlackNotifier
from src.recorders.wave_recorder import WaveRecorder
from src.utils.config import Config
from src.utils.logger import setup_logger

load_dotenv()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Loud Noise Detector")
    parser.add_argument(
        "--config",
        type=str,
        default="config/default_config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="data/recordings",
        help="Directory to save recordings",
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        help="RMS threshold to trigger detection",
    )
    parser.add_argument(
        "--language",
        "-l",
        type=str,
        choices=["en", "es"],
        default="en",
        help="Language for messages",
    )
    parser.add_argument(
        "--no-keep-files",
        action="store_true",
        dest="delete_files",
        help="Delete recording files after sending (don't keep them)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    config = Config(args.config)
    config.verbose = args.verbose or config.verbose
    config.language = args.language or config.language
    if args.delete_files:
        config.keep_files = False

    if args.threshold:
        config.threshold = args.threshold

    logger = setup_logger(config.verbose)
    config.logger = logger

    output_dir = args.output_dir or "data/recordings"
    os.makedirs(output_dir, exist_ok=True)

    recorder = WaveRecorder(
        output_dir=output_dir, temporary=not config.keep_files
    )

    notifiers: List[BaseNotifier] = []
    if slack_notifier := SlackNotifier.create_if_configured(config):
        notifiers.append(slack_notifier)

    detector = AudioDetector(config, [recorder], notifiers)

    try:
        detector.start()
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
