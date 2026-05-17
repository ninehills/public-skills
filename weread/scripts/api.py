#!/usr/bin/env python3
"""微信读书 — 兼容入口，实际调用 weread.py CLI。

用法: api.py <api_name> [key=val ...]

已废弃：请使用 weread.py <子命令> 获得格式化输出。
"""

import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
cli_path = os.path.join(script_dir, "weread.py")

if len(sys.argv) < 2:
    os.execv(sys.executable, [sys.executable, cli_path, "--help"])
    sys.exit(0)

api_name = sys.argv[1]
params = {}
for arg in sys.argv[2:]:
    if "=" in arg:
        k, v = arg.split("=", 1)
        params[k] = v

# Map old api_name style to CLI subcommands
api_to_cmd = {
    "/store/search": "search",
    "/shelf/sync": "shelf",
    "/book/info": "book",
    "/book/getprogress": "book",
    "/book/chapterinfo": "book",
    "/user/notebooks": "notes",
    "/book/bookmarklist": "notes",
    "/review/list/mine": "notes",
    "/readdata/detail": "readdata",
    "/review/list": "review",
    "/book/recommend": "discover",
    "/book/similar": "discover",
    "/_list": "list-apis",
}

cmd = api_to_cmd.get(api_name)
if not cmd:
    print(f"未知 api_name: {api_name}，请直接使用 weread.py <子命令>", file=sys.stderr)
    sys.exit(1)

# Build CLI args
args = [sys.executable, cli_path, cmd]
if "bookId" in params:
    args.append(params["bookId"])
elif "keyword" in params:
    args.append(params["keyword"])
elif cmd == "readdata" and "mode" in params:
    args.extend(["--mode", params["mode"]])
elif cmd == "review" and "bookId" not in params:
    # need positional bookId
    pass
elif cmd == "notes" and "bookId" in params:
    args.extend(["--book", params["bookId"]])

os.execv(sys.executable, args)
