# hiscores.py

from __future__ import annotations

from pathlib import Path

HISCORES_PATH = Path("hiscores.txt")
MAX_HISCORES = 10

def load_hiscores(path: Path = HISCORES_PATH) -> list[tuple[str, int]]:
    """Load highscores from text file. Format: ABC,1234 per line."""
    if not path.exists():
        return []

    hiscores: list[tuple[str, int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) != 2:
            continue  # skip malformed lines
        initials = parts[0].strip().upper()
        try:
            score = int(parts[1].strip())
        except ValueError:
            continue

        # keep only sane records
        if len(initials) != 3:
            continue
        if score <= 0:
            continue

        hiscores.append((initials, score))

    # normalize: sort and cut to MAX
    hiscores.sort(key=lambda t: t[1], reverse=True)
    return hiscores[:MAX_HISCORES]

def save_hiscores(hiscores: list[tuple[str, int]], path: Path = HISCORES_PATH) -> None:
    """Save highscores to text file. Writes top MAX_HISCORES sorted."""
    cleaned = [(ini.strip().upper(), int(sc)) for ini, sc in hiscores]
    cleaned.sort(key=lambda t: t[1], reverse=True)
    cleaned = cleaned[:MAX_HISCORES]

    text = "\n".join(f"{ini},{sc}" for ini, sc in cleaned) + ("\n" if cleaned else "")
    path.write_text(text, encoding="utf-8")


def qualifies(score: int, hiscores: list[tuple[str, int]], max_entries: int = MAX_HISCORES) -> bool:
    """Return True if score should enter the highscore table."""
    if score <= 0:
        return False
    if len(hiscores) < max_entries:
        return True
    # list is full: must beat the last entry
    return score > hiscores[-1][1]

def add_hiscore(
    initials: str,
    score: int,
    hiscores: list[tuple[str, int]],
    max_entries: int = MAX_HISCORES,
) -> list[tuple[str, int]]:
    """Return updated highscore list (sorted, capped)."""
    initials = initials.strip().upper()
    if len(initials) != 3:
        raise ValueError("Initials must be exactly 3 characters.")
    if score < 0:
        raise ValueError("Score must be >= 0.")

    new_list = list(hiscores)
    new_list.append((initials, score))
    new_list.sort(key=lambda t: t[1], reverse=True)
    return new_list[:max_entries]


def calc_hiscore(score: int) -> bool:
    """
    Minimal version of your calc_hiscore:
    returns True if the given score qualifies for top-10.
    UI (congrats message + initials input) happens in main.py.
    """
    hiscores = load_hiscores()
    return qualifies(score, hiscores)
