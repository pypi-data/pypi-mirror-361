import argparse
import sys
from pathlib import Path

from share.utils import load_md_template_data


def entry_point() -> tuple:
    parser = argparse.ArgumentParser(
        description='Render md file with template.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('source', type=str,
                        help='source markdown file path as input')
    parser.add_argument('dest', type=str,
                        help='destination file path as output')
    parser.add_argument('--template-index', type=int,
                        help='index of template in the template list')
    args = parser.parse_args()

    if not args.source or not args.dest:
        sys.exit(1)

    source_path = Path(args.source)
    dest_abs_path = Path(args.dest)

    if not source_path.is_file():
        print(f"Error: {source_path} is not a file.")
        sys.exit(1)
        return

    _, data = load_md_template_data(source_path)
    if not data:
        print(f"Error: {source_path} does not have output config file.")
        sys.exit(1)
        return

    if "outputs" not in data or len(data["outputs"]) - 1 < args.template_index:
        print(
            f"Error: {data} has no output of index {args.template_index}.")
        sys.exit(1)
        return

    output_config = data["outputs"][args.template_index]

    print(
        f"source file: {source_path}, dest file: {dest_abs_path}, "
        f"output config: {output_config}")

    return source_path, dest_abs_path, args.template_index, output_config
