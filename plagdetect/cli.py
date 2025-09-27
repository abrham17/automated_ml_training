import argparse
import json
import sys
from pathlib import Path
from typing import List

from .core import run_detection


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="plagdetect",
        description="Detect similarities between student assignments/projects using shingling and winnowing.",
    )
    parser.add_argument("inputs", nargs="+", help="Files or directories to analyze")
    parser.add_argument(
        "--include-glob",
        action="append",
        default=[],
        help="Glob(s) to include (e.g., *.py). Can be provided multiple times.",
    )
    parser.add_argument(
        "--exclude-glob",
        action="append",
        default=["**/.git/**", "**/node_modules/**", "**/__pycache__/**"],
        help="Glob(s) to exclude. Can be provided multiple times.",
    )
    parser.add_argument("--strip-comments", action="store_true", help="Attempt to strip comments for known languages")
    parser.add_argument(
        "--k-gram",
        type=int,
        default=5,
        help="Size of k-gram for shingling (chars if --unit=char, words if --unit=word)",
    )
    parser.add_argument("--unit", choices=["char", "word"], default="word", help="Unit for shingling")
    parser.add_argument("--winnow", action="store_true", help="Use winnowing fingerprinting")
    parser.add_argument("--window", type=int, default=4, help="Winnowing window size (t)")
    parser.add_argument("--threshold", type=float, default=0.5, help="Similarity threshold to report (0-1)")
    parser.add_argument(
        "--report",
        choices=["json", "csv", "html"],
        default="json",
        help="Output report format",
    )
    parser.add_argument("--output", type=Path, default=Path("plagdetect_report.json"), help="Output file path")
    parser.add_argument("--jobs", type=int, default=0, help="Parallel workers (0=auto)")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        result = run_detection(
            inputs=[Path(p) for p in args.inputs],
            include_globs=args.include_glob,
            exclude_globs=args.exclude_glob,
            strip_comments=args.strip_comments,
            k_gram=args.k_gram,
            unit=args.unit,
            use_winnowing=args.winnow,
            window_size=args.window,
            threshold=args.threshold,
            report_format=args.report,
            output_path=args.output,
            num_workers=args.jobs,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.report == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Report written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

