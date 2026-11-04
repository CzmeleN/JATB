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

def unbind_all() -> None:
    for name in plt.rcParams:
        if name.startswith("keymap."):
            plt.rcParams[name] = []

def try_load_tags(path: str) -> dict[int, str]:
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

class Tagger:
    def __init__(self, src: str, dst: str) -> None:
        self.dst = dst
        data = np.genfromtxt(src, delimiter=",", names=True)
        self.x, self.z = data["pos_x"], data["pos_z"]
        self.t = data["race_time"].astype(int)
        self.speed = np.linalg.norm(np.stack([data["vel_x"], data["vel_y"], data["vel_z"]]), axis=0) * 3.6
        self.last = len(self.t) - 1

        self.tags = try_load_tags(dst)
        self.i = 0
        self.awaiting_tag = False

        self.fig, self.ax = plt.subplots()
        x, z = self.x, self.z
        self.ax.scatter(x, z, c=np.arange(len(x)), cmap="viridis", s=4)
        self.ax.plot(x[0], z[0], "o", color="green", ms=10, label="start")
        self.ax.plot(x[-1], z[-1], "s", color="red", ms=10, label="end")
        self.tag_pts, = self.ax.plot([], [], "x", color="black", ms=9, mew=2, label="tags")
        self.cur, = self.ax.plot([], [], "o", ms=14, mfc="none", mec="magenta", mew=2)
        self.ax.set_aspect("equal")
        self.ax.legend(loc="upper right")
        self.fig.subplots_adjust(bottom=0.2)
        self.fig.text(0.5, 0.02, KEYS_HELP, ha="center", va="bottom", family="monospace", fontsize=8)

        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        self.redraw()

    def run(self) -> None:
        plt.show()

    def index_of(self, rt: int) -> int:
        return int(np.argmin(np.abs(self.t - rt)))

    def print_tags(self) -> None:
        """tag list with the current position highlighted, add <no tag> row if between"""
        cur_t = int(self.t[self.i])
        no_tag = f"{HIGHLIGHT}{cur_t:>8}  <no tag>{RESET}"
        lines, placed = [], False
        for rt in sorted(self.tags):
            if not placed and cur_t < rt:
                lines.append(no_tag)
                placed = True
            if rt == cur_t:
                lines.append(f"{HIGHLIGHT}{rt:>8}  {self.tags[rt]}{RESET}")
                placed = True
            else:
                lines.append(f"{rt:>8}  {self.tags[rt]}")
        if not placed:
            lines.append(no_tag)
        print(CLEAR + "\n".join(lines), flush=True)

    def redraw(self) -> None:
        i = self.i
        self.cur.set_data([self.x[i]], [self.z[i]])
        idx = [self.index_of(rt) for rt in self.tags]
        self.tag_pts.set_data(self.x[idx], self.z[idx])
        mode = "   [press 1-4]" if self.awaiting_tag else ""
        self.ax.set_title(
            f"frame {i}/{self.last}   t={self.t[i]} ms   {self.speed[i]:.0f} km/h   "
            f"tag: {self.tags.get(int(self.t[i]), '-')}{mode}"
        )
        self.fig.canvas.draw_idle()

    def on_key(self, event) -> None:
        k, i, t, tags = event.key, self.i, self.t, self.tags

        if self.awaiting_tag:
            self.awaiting_tag = False
            if k in TAGS:
                tags[int(t[i])] = TAGS[k]
                save_tags(self.dst, tags)
        elif k in STEPS:
            self.i = int(np.clip(i + STEPS[k], 0, self.last))
        elif k == "s":
            self.i = 0
        elif k == "e":
            self.i = self.last
        elif k == "t":
            self.awaiting_tag = True
        elif k == "r":
            if tags.pop(int(t[i]), None) is not None:
                save_tags(self.dst, tags)
        elif k in ("[", "]"):
            if k == "[":
                prev = [rt for rt in sorted(tags) if rt < t[i]]
                if prev:
                    self.i = self.index_of(prev[-1])
            else:
                nxt = [rt for rt in sorted(tags) if rt > t[i]]
                if nxt:
                    self.i = self.index_of(nxt[0])
        elif k == "f":
            self.print_tags()
        elif k == "q":
            plt.close(self.fig)
            return
        self.redraw()

def main() -> None:
    unbind_all()
    tagger = Tagger(sys.argv[1], sys.argv[2])
    tagger.run()

if __name__ == "__main__":
    main()
