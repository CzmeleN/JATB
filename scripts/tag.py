"""Tag a recorded route offline

Usage: py tag.py <input.csv> <output.csv>

Keybinds:
    H / h / J / j  -1000 / -100 / -10 / -1 frames
    k / K / l / L  +1 / +10 / +100 / +1000 frames
    s / e          jump to start / end
    [ / ]          jump to previous / next tag
    t, then 1-4    add tag at the current frame (any to cancel)
    r              remove tag at the current frame
    f              print all tags to the terminal
    q              quit

Loads / creates and edits <output.csv>, saves after every change
"""

import csv
import sys

import matplotlib.pyplot as plt
import numpy as np

TAGS = {
    "1": "left_turn_start",
    "2": "left_turn_end",
    "3": "right_turn_start",
    "4": "right_turn_end",
}

STEPS = {"H": -1000, "h": -100, "J": -10, "j": -1, "k": 1, "K": 10, "l": 100, "L": 1000}

KEYS_HELP = "\n".join([
    "H/h/J/j: -1000/-100/-10/-1    k/K/l/L: +1/+10/+100/+1000",
    "s/e: start/end    [/]: prev/next tag    r: remove tag    f: print tags    q: quit",
    "t + " + "  ".join(f"{key}: {name}" for key, name in TAGS.items()),
])

HIGHLIGHT = "\033[30;47m" # black text on white background
RESET = "\033[0m"
CLEAR = "\033[H\033[2J\033[3J" # cursor home, clear screen, clear scrolled

for name in plt.rcParams:
    if name.startswith("keymap."):
        plt.rcParams[name] = []

def load_tags(path: str) -> dict[int, str]:
    try:
        with open(path, newline="") as f:
            return {int(row["race_time"]): row["tag"] for row in csv.DictReader(f)}
    except FileNotFoundError:
        return {}

def save_tags(path: str, tags: dict[int, str]) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["race_time", "tag"])
        for rt in sorted(tags):
            writer.writerow([rt, tags[rt]])

def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    data = np.genfromtxt(src, delimiter=",", names=True)
    x, z = data["pos_x"], data["pos_z"]
    t = data["race_time"].astype(int)
    speed = np.linalg.norm(np.stack([data["vel_x"], data["vel_y"], data["vel_z"]]), axis=0) * 3.6
    last = len(t) - 1

    tags = load_tags(dst)
    state = {"i": 0, "awaiting_tag": False}

    fig, ax = plt.subplots()
    ax.scatter(x, z, c=np.arange(len(x)), cmap="viridis", s=4)
    ax.plot(x[0], z[0], "o", color="green", ms=10, label="start")
    ax.plot(x[-1], z[-1], "s", color="red", ms=10, label="end")
    tag_pts, = ax.plot([], [], "x", color="black", ms=9, mew=2, label="tags")
    cur, = ax.plot([], [], "o", ms=14, mfc="none", mec="magenta", mew=2)
    ax.set_aspect("equal")
    ax.legend(loc="upper right")
    fig.subplots_adjust(bottom=0.2)
    fig.text(0.5, 0.02, KEYS_HELP, ha="center", va="bottom", family="monospace", fontsize=8)

    def index_of(rt: int) -> int:
        return int(np.argmin(np.abs(t - rt)))

    def print_tags() -> None:
        """tag list with the current position highlighted, add <no tag> row if between"""
        cur_t = int(t[state["i"]])
        no_tag = f"{HIGHLIGHT}{cur_t:>8}  <no tag>{RESET}"
        lines, placed = [], False
        for rt in sorted(tags):
            if not placed and cur_t < rt:
                lines.append(no_tag)
                placed = True
            if rt == cur_t:
                lines.append(f"{HIGHLIGHT}{rt:>8}  {tags[rt]}{RESET}")
                placed = True
            else:
                lines.append(f"{rt:>8}  {tags[rt]}")
        if not placed:
            lines.append(no_tag)
        print(CLEAR + "\n".join(lines), flush=True)

    def redraw() -> None:
        i = state["i"]
        cur.set_data([x[i]], [z[i]])
        idx = [index_of(rt) for rt in tags]
        tag_pts.set_data(x[idx], z[idx])
        mode = "   [press 1-4]" if state["awaiting_tag"] else ""
        ax.set_title(
            f"frame {i}/{last}   t={t[i]} ms   {speed[i]:.0f} km/h   "
            f"tag: {tags.get(int(t[i]), '-')}{mode}"
        )
        fig.canvas.draw_idle()

    def on_key(event) -> None:
        k, i = event.key, state["i"]

        if state["awaiting_tag"]:
            state["awaiting_tag"] = False
            if k in TAGS:
                tags[int(t[i])] = TAGS[k]
                save_tags(dst, tags)
        elif k in STEPS:
            state["i"] = int(np.clip(i + STEPS[k], 0, last))
        elif k == "s":
            state["i"] = 0
        elif k == "e":
            state["i"] = last
        elif k == "t":
            state["awaiting_tag"] = True
        elif k == "r":
            if tags.pop(int(t[i]), None) is not None:
                save_tags(dst, tags)
        elif k in ("[", "]"):
            if k == "[":
                prev = [rt for rt in sorted(tags) if rt < t[i]]
                if prev:
                    state["i"] = index_of(prev[-1])
            else:
                nxt = [rt for rt in sorted(tags) if rt > t[i]]
                if nxt:
                    state["i"] = index_of(nxt[0])
        elif k == "f":
            print_tags()
        elif k == "q":
            plt.close(fig)
            return
        redraw()

    fig.canvas.mpl_connect("key_press_event", on_key)
    redraw()
    plt.show()

if __name__ == "__main__":
    main()
