#!/usr/bin/env python3
import argparse
import json
import os
import signal
import threading
import time
import shutil
import subprocess
import sys
from typing import List, Dict, Any


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        print(f"Error: '{name}' not found in PATH.")
        if name == "yt-dlp":
            print("Install yt-dlp (package or pip) and try again.")
        elif name == "mpv":
            print("Install mpv and try again.")
        sys.exit(1)


def _progress_bar(label: str, stop_event: threading.Event) -> None:
    width = 20
    pos = 0
    direction = 1
    while not stop_event.is_set():
        bar = [" "] * width
        bar[pos] = "#"
        sys.stdout.write(f"\r{label} [{''.join(bar)}]")
        sys.stdout.flush()
        pos += direction
        if pos == 0 or pos == width - 1:
            direction *= -1
        time.sleep(0.08)
    sys.stdout.write("\r" + " " * (len(label) + width + 3) + "\r")
    sys.stdout.flush()


def run_yt_dlp_json(args: List[str], label: str = "") -> Dict[str, Any]:
    cmd = ["yt-dlp", "--dump-single-json"] + args
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stop_event = threading.Event()
    spinner_thread = None
    if label and sys.stdout.isatty():
        spinner_thread = threading.Thread(
            target=_progress_bar, args=(label, stop_event), daemon=True
        )
        spinner_thread.start()
    out, err = proc.communicate()
    stop_event.set()
    if spinner_thread is not None:
        spinner_thread.join()
    if proc.returncode != 0:
        print("yt-dlp failed:")
        if err:
            print(err.strip())
        sys.exit(proc.returncode)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        print("Failed to parse yt-dlp output.")
        sys.exit(1)


def search(query: str, limit: int) -> List[Dict[str, Any]]:
    target = f"ytsearch{limit}:{query}"
    data = run_yt_dlp_json([target], label="Searching")
    entries = data.get("entries") or []
    return entries


def format_duration(seconds: Any) -> str:
    if seconds is None:
        return "?"
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return "?"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"


def print_results(entries: List[Dict[str, Any]]) -> None:
    for idx, entry in enumerate(entries, start=1):
        title = entry.get("title") or "(no title)"
        uploader = entry.get("uploader") or entry.get("channel") or "?"
        duration = format_duration(entry.get("duration"))
        url = entry.get("webpage_url") or entry.get("url") or ""
        print(f"{idx:>2}. {title} [{duration}] - {uploader}")
        if url:
            print(f"    {url}")


def play_url(url: str, video: bool) -> None:
    require_tool("mpv")
    cmd = ["mpv", "--ytdl=yes"]
    if not video:
        cmd.append("--no-video")
    cmd.append(url)
    subprocess.run(cmd)


def clear_screen() -> None:
    if not sys.stdout.isatty():
        return
    os.system("cls" if os.name == "nt" else "clear")


def play_queue(entries: List[Dict[str, Any]], start_idx: int, video: bool) -> None:
    if not entries:
        return
    if start_idx < 0 or start_idx >= len(entries):
        return
    print("Autoplay aktif: akan memutar urutan berikutnya. Tekan Ctrl+C untuk berhenti.")
    for i in range(start_idx, len(entries)):
        entry = entries[i]
        url = entry.get("webpage_url") or entry.get("url")
        title = entry.get("title") or "(no title)"
        if not url:
            continue
        clear_screen()
        print(f"Now playing: {title}")
        play_url(url, video=video)


def interactive() -> None:
    require_tool("yt-dlp")
    require_tool("mpv")

    print("Ketik 'q' untuk keluar kapan saja.")
    query = input("Search YouTube: ").strip()
    if query.lower() in {"q", "quit", "exit"}:
        return
    if not query:
        print("No query provided.")
        return
    entries = search(query, limit=10)
    if not entries:
        print("No results.")
        return
    print_results(entries)
    choice = input("Pick a number to play (or blank to exit): ").strip()
    if choice.lower() in {"q", "quit", "exit"}:
        return
    if not choice:
        return
    try:
        idx = int(choice)
    except ValueError:
        print("Invalid number.")
        return
    if idx < 1 or idx > len(entries):
        print("Out of range.")
        return
    mode = input("Play as (a)udio or (v)ideo? [a]: ").strip().lower()
    if mode in {"q", "quit", "exit"}:
        return
    video = mode == "v"
    play_queue(entries, idx - 1, video)


def main() -> None:
    def handle_sigint(signum, frame) -> None:
        print("\nKeluar.")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    parser = argparse.ArgumentParser(
        description="Terminal YouTube music/video player (yt-dlp + mpv)"
    )
    parser.add_argument(
        "-s",
        "--search",
        dest="quick_search",
        help="Cari dan langsung putar hasil (autoplay urutan berikutnya)",
    )
    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=10,
        help="Jumlah hasil untuk mode -s/--search",
    )
    parser.add_argument(
        "-v",
        "--video",
        action="store_true",
        help="Mainkan video (default audio) untuk mode -s/--search",
    )
    sub = parser.add_subparsers(dest="cmd")

    s = sub.add_parser("search", help="Search YouTube")
    s.add_argument("query", nargs="+", help="Search query")
    s.add_argument("--limit", type=int, default=10, help="Max results")

    p = sub.add_parser("play", help="Play a URL or search term")
    p.add_argument("target", nargs="+", help="URL or search query")
    p.add_argument("--video", action="store_true", help="Play video instead of audio")
    p.add_argument("--search", action="store_true", help="Treat target as search query")

    sub.add_parser("interactive", help="Interactive search and play")

    args = parser.parse_args()

    if args.quick_search:
        require_tool("yt-dlp")
        require_tool("mpv")
        entries = search(args.quick_search, limit=args.limit)
        if not entries:
            print("No results.")
            return
        print_results(entries)
        choice = input("Pick a number to play (or blank to exit): ").strip()
        if choice.lower() in {"q", "quit", "exit"}:
            return
        if not choice:
            return
        try:
            idx = int(choice)
        except ValueError:
            print("Invalid number.")
            return
        if idx < 1 or idx > len(entries):
            print("Out of range.")
            return
        play_queue(entries, idx - 1, video=args.video)
        return

    if args.cmd is None:
        interactive()
        return

    if args.cmd == "search":
        require_tool("yt-dlp")
        query = " ".join(args.query)
        entries = search(query, limit=args.limit)
        if not entries:
            print("No results.")
            return
        print_results(entries)
        return

    if args.cmd == "play":
        require_tool("yt-dlp")
        target = " ".join(args.target)
        if args.search:
            entries = search(target, limit=1)
            if not entries:
                print("No results.")
                return
            url = entries[0].get("webpage_url") or entries[0].get("url")
            if not url:
                print("Missing URL for selection.")
                return
        else:
            url = target
        play_url(url, video=args.video)
        return

    if args.cmd == "interactive":
        interactive()


if __name__ == "__main__":
    main()
