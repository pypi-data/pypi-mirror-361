#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import sys
from share.render_helper import entry_point
from .work_dir_context import WorkDirContext
from dotenv import load_dotenv


def main():
    source_path, dest_abs_path, template_index, output_config = entry_point()
    load_dotenv()

    output_template_dir_path = Path(
        os.path.expanduser(
            os.getenv("template_dir", default="~/repo/md-render-template"))
    ) / output_config["template"]
    if not output_template_dir_path.is_dir():
        print(f"Error: {output_template_dir_path} is not a directory.")
        sys.exit(1)
        return

    context = WorkDirContext(source_path, dest_abs_path,
                             output_template_dir_path,
                             template_index)
    context.render()
    sys.exit(0)


if __name__ == "__main__":
    main()
