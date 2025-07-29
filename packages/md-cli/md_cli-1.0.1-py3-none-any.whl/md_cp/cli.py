#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
md-cp
==========

Copy markdown file with all referenced resource files while maintaining relative paths.

我有一个markdown文件，其中使用相对地址引用了外部图片、视频、下载文件等资源。我希望写一个python程序md-cp，这个程序接受2个参数：md-cp src/index.md dst/index.md

命令将这个md文件从src/index.md目录复制到dst/index.md，同时将src目录下面的index.md文件以相对路径引用的资源文件也全部复制到dst目录下，自动创建相对于dst目录的相同的目录结构，保持引用的资源路径和资源文件名不变。

注意：

复制资源时需要检查md文件中引用的资源文件是否在dst目录下已经存在。如果已经存在，则需要比较src文件和dst文件的时间戳，如果src文件更新，则覆盖dst文件；dst目录中的文件时间戳更新或与src文件时间戳相同，则跳过不再复制。
"""

import os
import re
import sys
import shutil
from pathlib import Path
import argparse

# 匹配 Markdown 中的资源引用
RESOURCE_PATTERNS = [
    r'!$$[^$$]*\]$([^)]+)$',  # 图片 ![alt](path)
    r'$$[^$$]*\]$([^)]+)$',   # 链接 [text](path)
    r'="([^"]+)"',              # HTML 属性 src="path"
    # HTML 标签
    r'<\s*(img|video|audio|source)\s+[^>]*src\s*=\s*["\']([^"\']+)["\']',
]


class MarkdownCopier:
    def __init__(self, src_file, dst_file):
        self.src_file = Path(src_file).resolve()
        self.dst_file = Path(dst_file).resolve()
        self.src_dir = self.src_file.parent
        self.dst_dir = self.dst_file.parent
        self.copied_files = set()

    def extract_resources(self):
        """从 Markdown 文件中提取所有引用的资源路径"""
        resources = set()

        try:
            content = self.src_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            print(
                f"Warning: Could not read {self.src_file} as UTF-8, trying system default encoding")
            content = self.src_file.read_text()

        for pattern in RESOURCE_PATTERNS:
            for match in re.finditer(pattern, content):
                # 对于 HTML 标签，group(2) 是 src 属性值
                path = match.group(2) if len(
                    match.groups()) > 1 else match.group(1)

                # 排除网络资源和锚点
                if not path or path.startswith(('http://', 'https://', 'ftp://', '#')):
                    continue

                # 处理可能包含 URL 编码的路径
                path = self._decode_url_path(path)
                resources.add(path)

        return sorted(resources)

    def _decode_url_path(self, path):
        """处理可能包含 URL 编码的路径"""
        from urllib.parse import unquote
        return unquote(path)

    def _should_copy(self, src, dst):
        """判断是否需要复制文件"""
        if not dst.exists():
            return True

        src_mtime = src.stat().st_mtime
        dst_mtime = dst.stat().st_mtime

        return src_mtime > dst_mtime

    def copy_resources(self):
        """复制所有引用的资源文件"""
        resources = self.extract_resources()
        if not resources:
            print("No external resources found in markdown file.")
            return

        print(f"Found {len(resources)} resource references in markdown file.")

        for rel_path in resources:
            # 处理跨平台路径分隔符
            rel_path = rel_path.replace('/', os.sep).replace('\\', os.sep)

            # 获取源文件绝对路径
            src_abs = (self.src_dir / rel_path).resolve()

            # 跳过不存在的文件
            if not src_abs.exists():
                print(f"Warning: Resource file not found: {src_abs}")
                continue

            # 计算目标路径
            dst_abs = (self.dst_dir / rel_path).resolve()

            # 确保目标目录存在
            dst_abs.parent.mkdir(parents=True, exist_ok=True)

            # 检查是否需要复制
            if self._should_copy(src_abs, dst_abs):
                print(f"Copying {src_abs} -> {dst_abs}")
                shutil.copy2(src_abs, dst_abs)
                self.copied_files.add(str(dst_abs))
            else:
                print(f"Skipping {dst_abs} (up to date)")

    def copy_markdown(self):
        """复制 Markdown 文件"""
        if self._should_copy(self.src_file, self.dst_file):
            print(f"Copying markdown file {self.src_file} -> {self.dst_file}")
            self.dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.src_file, self.dst_file)
        else:
            print(f"Skipping markdown file {self.dst_file} (up to date)")

    def run(self):
        """执行复制操作"""
        self.copy_resources()
        self.copy_markdown()
        print(
            f"Copied {len(self.copied_files)} resource files and markdown file.")


def main():
    parser = argparse.ArgumentParser(
        description='Copy markdown file with resource files.',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('source', type=str,
                        help='source markdown file path as input')
    parser.add_argument('dest', type=str,
                        help='dest markdown file path as output')
    args = parser.parse_args()

    src_file = Path(args.source).expanduser()
    dst_file = Path(args.dest).expanduser()

    if not src_file.is_file():
        print(f"Error: {src_file} is not a file.")
        sys.exit(1)

    copier = MarkdownCopier(src_file, dst_file)
    copier.run()
    sys.exit(0)


if __name__ == "__main__":
    main()
