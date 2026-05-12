"""Compare raw scraper samples and emit text or HTML diff reports."""

from __future__ import annotations

import argparse
import difflib
from pathlib import Path


def read_lines(file_path: str | Path) -> list[str]:
    """Read a sample file as UTF-8 lines while tolerating malformed bytes."""
    return Path(file_path).read_text(encoding="utf-8", errors="replace").splitlines()


def unified_diff(old_file: str | Path, new_file: str | Path, *, context: int = 3) -> str:
    """Return a unified diff string for two sample files."""
    old_path = Path(old_file)
    new_path = Path(new_file)
    return "\n".join(
        difflib.unified_diff(
            read_lines(old_path),
            read_lines(new_path),
            fromfile=str(old_path),
            tofile=str(new_path),
            lineterm="",
            n=context,
        )
    )


def html_diff(
    old_file: str | Path,
    new_file: str | Path,
    output_file: str | Path,
    *,
    context: bool = True,
    numlines: int = 3,
) -> Path:
    """Write an HTML diff report comparing two sample files."""
    old_path = Path(old_file)
    new_path = Path(new_file)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = difflib.HtmlDiff().make_file(
        read_lines(old_path),
        read_lines(new_path),
        fromdesc=str(old_path),
        todesc=str(new_path),
        context=context,
        numlines=numlines,
    )
    output_path.write_text(report, encoding="utf-8")
    return output_path


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for ad hoc sample comparisons."""
    parser = argparse.ArgumentParser(description="Compare two raw scraper sample files.")
    parser.add_argument("old_file", help="Baseline sample file")
    parser.add_argument("new_file", help="Newly captured sample file")
    parser.add_argument(
        "--html",
        dest="html_output",
        help="Optional path for an HTML diff report; prints text diff when omitted.",
    )
    parser.add_argument("--context", type=int, default=3, help="Diff context line count")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the diff tool from the command line."""
    args = build_parser().parse_args(argv)
    if args.html_output:
        report_path = html_diff(
            args.old_file,
            args.new_file,
            args.html_output,
            numlines=args.context,
        )
        print(f"HTML diff written to {report_path}")
    else:
        print(unified_diff(args.old_file, args.new_file, context=args.context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
