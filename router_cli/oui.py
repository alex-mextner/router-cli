"""oui — MAC address prefix to manufacturer.

The package ships ``data/oui.tsv.gz``: the IEEE MA-L registry (every 24-bit prefix) compacted
to ``PREFIX<TAB>short vendor`` lines. ``router oui update`` downloads the current
``oui.csv`` from the IEEE into the data directory, and a downloaded table always wins over
the shipped one.

Locally administered addresses (bit 1 of the first octet: phones' per-network "private"
addresses, VMs, containers) are not in any registry; they are reported as random rather
than looked up.
"""

from __future__ import annotations

import csv
import gzip
import io
import re
import urllib.request
from functools import lru_cache
from importlib import resources
from pathlib import Path

from ._errors import NetworkError
from .config import data_dir
from .models import is_random_mac, normalize_mac

IEEE_URL = "https://standards-oui.ieee.org/oui/oui.csv"
FILENAME = "oui.tsv.gz"

_SUFFIXES = re.compile(
    r"(?:[,.]\s*|\s+)(inc|incorporated|corp|corporation|co|company|ltd|limited|llc|gmbh|ag|sa|s\.a|"
    r"bv|b\.v|oy|ab|as|srl|spa|pte|pty|plc|kg|kk|nv|sas|sarl|s\.p\.a|co\.,\s*ltd|holdings|"
    r"international|electronics?|technology|technologies|tech|communication|communications|"
    r"group|industrial|industries|manufacturing|intl|shenzhen|guangdong|beijing|shanghai)\b\.?",
    re.I,
)

_PLACES = re.compile(
    r"^(shenzhen|beijing|shanghai|guangzhou|guangdong|hangzhou|zhejiang|jiangsu|suzhou|hunan|"
    r"fujian|xiamen|dongguan|wuhan|chengdu|nanjing|qingdao|tianjin|taiwan|hong kong)\s+",
    re.I,
)


def shorten(name: str) -> str:
    """'Apple, Inc.' -> 'Apple'; 'Espressif Inc.' -> 'Espressif'; keeps the brand word(s)."""
    text = " ".join(name.replace('"', "").replace("\uff0c", ",").replace("\uff0e", ".").split())
    text = _PLACES.sub("", text).strip() or text
    if text.isupper() and len(text) > 4:
        text = " ".join(w if len(w) <= 3 else w.capitalize() for w in text.split())
    previous = None
    while previous != text:
        previous = text
        text = _SUFFIXES.sub("", text).strip(" ,.-")
    return (text or name.strip())[:40]


def compact(csv_text: str) -> dict[str, str]:
    table: dict[str, str] = {}
    reader = csv.reader(io.StringIO(csv_text))
    for row in reader:
        if len(row) < 3 or row[0] == "Registry":
            continue
        prefix = row[1].strip().upper()
        if re.fullmatch(r"[0-9A-F]{6}", prefix):
            table[prefix] = shorten(row[2])
    return table


def write_table(table: dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(f"{k}\t{v}\n" for k, v in sorted(table.items()))
    tmp = path.with_suffix(".tmp")
    with gzip.open(tmp, "wt", encoding="utf-8") as handle:
        handle.write(body)
    tmp.replace(path)


def downloaded_path() -> Path:
    return data_dir() / FILENAME


def _read_gz(data: bytes) -> dict[str, str]:
    table: dict[str, str] = {}
    for line in gzip.decompress(data).decode("utf-8").splitlines():
        prefix, _, vendor = line.partition("\t")
        if prefix and vendor:
            table[prefix] = vendor
    return table


@lru_cache(maxsize=1)
def table() -> dict[str, str]:
    local = downloaded_path()
    if local.is_file():
        try:
            return _read_gz(local.read_bytes())
        except (OSError, ValueError, EOFError):
            pass
    try:
        shipped = resources.files("router_cli").joinpath("data", FILENAME).read_bytes()
    except (FileNotFoundError, OSError):
        return {}
    return _read_gz(shipped)


def source() -> str:
    local = downloaded_path()
    return str(local) if local.is_file() else "shipped"


def vendor(mac: str) -> str | None:
    try:
        norm = normalize_mac(mac)
    except Exception:
        return None
    if is_random_mac(norm):
        return None
    return table().get(norm.replace(":", "")[:6].upper())


def update(url: str = IEEE_URL, timeout: float = 60.0) -> tuple[Path, int]:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 router-cli"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
    except OSError as exc:
        raise NetworkError(
            what=f"could not download {url}",
            why=str(exc),
            how="try again later; the shipped table keeps working meanwhile",
        ) from exc
    parsed = compact(text)
    if len(parsed) < 1000:
        raise NetworkError(
            what="the IEEE download looks truncated", why=f"{len(parsed)} rows", how=""
        )
    path = downloaded_path()
    write_table(parsed, path)
    table.cache_clear()
    return path, len(parsed)
