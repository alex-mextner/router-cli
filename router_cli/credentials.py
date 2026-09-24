"""credentials — which router, which driver, which user, and its password.

THE FILE (primary store)
    ``$XDG_CONFIG_HOME/router-cli/credentials.json`` (``~/.config/router-cli/``;
    ``ROUTER_CLI_CONFIG_DIR`` overrides the directory)::

        {
          "routers": {
            "192.168.0.1": {"driver": "ubee_evw32c", "username": "admin", "password": "..."}
          },
          "default": "192.168.0.1"
        }

    Keyed by host; ``default`` picks the router when ``--host`` is omitted. The directory
    is created 0700 and the file 0600, and router-cli REFUSES to read a file that is group-
    or world-readable rather than quietly using a password other users can read. It is
    written by ``router login`` (password from a getpass prompt) and may be written by hand.

THE OS KEYRING (optional)
    ``router login --store keyring`` puts the password in the Secret Service
    (``secret-tool``), the macOS keychain (``security``) or Windows Credential Manager, and
    writes the file entry WITHOUT a password. A password in the file always takes
    precedence; the keyring is only asked when the file has none. (A keyring that stays
    locked under autologin — common on headless boxes — is why the file is primary.)

WHAT NEVER HAPPENS
    The password never goes through argv (visible in ``ps``), an environment variable, a log
    line or dry-run output. ``secret-tool`` reads it from stdin, ``security -i`` reads its
    command from stdin, the Windows API takes a buffer.
"""

from __future__ import annotations

import ctypes
import json
import os
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from ._errors import UsageError
from .config import config_dir

SERVICE = "router-cli"
FILENAME = "credentials.json"


def host_key(host: str) -> str:
    """'http://192.168.0.1/' -> '192.168.0.1' (the file's key for a router)."""
    return host.strip().split("://", 1)[-1].rstrip("/")


def key_for(driver: str, host: str, user: str) -> str:
    return f"{driver}:{host_key(host)}:{user}"


# ── the file ─────────────────────────────────────────────────────────────────
def path() -> Path:
    return config_dir() / FILENAME


@dataclass
class Entry:
    host: str
    driver: str = ""
    username: str = ""
    password: str = ""


def _check_permissions(p: Path) -> None:
    if sys.platform == "win32":
        return
    mode = p.stat().st_mode
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise UsageError(
            what=f"refusing to use {p}: it is readable by other users",
            why=f"its mode is {stat.filemode(mode)}; a stored password must be private",
            how=f"chmod 600 {p}",
        )


def load_file() -> dict[str, Any]:
    p = path()
    if not p.exists():
        return {"routers": {}}
    _check_permissions(p)
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise UsageError(
            what=f"could not read {p}",
            why=str(exc),
            how="fix the JSON (see `router login --help` for the format) or run `router login`",
        ) from exc
    if not isinstance(raw, dict):
        raise UsageError(what=f"{p} must hold a JSON object", why="", how="run `router login`")
    routers = raw.get("routers")
    raw["routers"] = routers if isinstance(routers, dict) else {}
    return raw


def save_file(data: dict[str, Any]) -> Path:
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform != "win32":
        os.chmod(p.parent, stat.S_IRWXU)
    tmp = p.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        # codeql[py/clear-text-storage-sensitive-data]
        # Justified: this file IS the documented credential store (the OS keyring is often
        # locked on headless machines). It is created 0600 inside a 0700 directory before
        # anything is written, and load_file() refuses to read it if that ever loosens.
        handle.write(json.dumps(data, indent=2) + "\n")
    if sys.platform != "win32":
        os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)
    os.replace(tmp, p)
    return p


def entry(host: str) -> Entry | None:
    key = host_key(host)
    raw = load_file()["routers"].get(key)
    if not isinstance(raw, dict):
        return None
    return Entry(
        host=key,
        driver=str(raw.get("driver") or ""),
        username=str(raw.get("username") or ""),
        password=str(raw.get("password") or ""),
    )


def default_host() -> str:
    data = load_file()
    default = data.get("default")
    if isinstance(default, str) and default:
        return default
    routers = data["routers"]
    return next(iter(routers)) if len(routers) == 1 else ""


def password_for(host: str, driver: str, user: str) -> str | None:
    """The file's password for this host (if the user matches), else the keyring's."""
    found = entry(host)
    if found and found.password and (not user or not found.username or found.username == user):
        return found.password
    return keyring_get(key_for(driver, host, user))


def store(
    host: str,
    driver: str,
    user: str,
    password: str,
    prefer: str = "file",
    make_default: bool = True,
) -> tuple[str, Path]:
    """Save a router's credentials; return (where the password went, the file path)."""
    if prefer not in ("file", "keyring"):
        raise UsageError(what=f"unknown store {prefer!r}", why="", how="use file or keyring")
    data = load_file()
    key = host_key(host)
    record: dict[str, str] = {"driver": driver, "username": user}
    where = "file"
    if prefer == "keyring":
        keyring = available_keyring()
        if keyring is None:
            raise UsageError(
                what="no OS keyring is available",
                why="no Secret Service (secret-tool + D-Bus session), macOS keychain or Windows",
                how="use the default file store (omit --store)",
            )
        try:
            keyring.set(key_for(driver, key, user), password)
        except (OSError, subprocess.SubprocessError) as exc:
            raise UsageError(
                what=f"the {keyring.name} keyring refused the password",
                why=str(exc),
                how="it may be locked; omit --store to use the file",
            ) from exc
        where = keyring.name
    else:
        record["password"] = password
    data["routers"][key] = record
    if make_default or not data.get("default"):
        data["default"] = key
    return where, save_file(data)


def remove(host: str) -> list[str]:
    """Forget a router: its file entry and any keyring item. Returns what was removed."""
    key = host_key(host)
    removed: list[str] = []
    data = load_file()
    found = data["routers"].pop(key, None)
    if isinstance(found, dict):
        removed.append("file")
        driver, user = str(found.get("driver", "")), str(found.get("username", ""))
        if data.get("default") == key:
            data["default"] = next(iter(data["routers"]), "")
        save_file(data)
        for store_ in keyring_stores():
            if store_.available():
                try:
                    if store_.delete(key_for(driver, key, user)):
                        removed.append(store_.name)
                except (OSError, subprocess.SubprocessError):
                    continue
    return removed


# ── OS keyrings (optional) ───────────────────────────────────────────────────
class Store(Protocol):
    name: str

    def available(self) -> bool: ...
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, secret: str) -> None: ...
    def delete(self, key: str) -> bool: ...


def _run(cmd: list[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=15, check=False)


class SecretToolStore:
    name = "secret-service"

    def available(self) -> bool:
        if not sys.platform.startswith("linux") or not shutil.which("secret-tool"):
            return False
        runtime = os.environ.get("XDG_RUNTIME_DIR", "")
        return bool(os.environ.get("DBUS_SESSION_BUS_ADDRESS")) or (
            bool(runtime) and Path(runtime, "bus").exists()
        )

    def get(self, key: str) -> str | None:
        result = _run(["secret-tool", "lookup", "service", SERVICE, "account", key])
        return result.stdout.rstrip("\n") if result.returncode == 0 and result.stdout else None

    def set(self, key: str, secret: str) -> None:
        result = _run(
            [
                "secret-tool",
                "store",
                f"--label={SERVICE} {key}",
                "service",
                SERVICE,
                "account",
                key,
            ],
            stdin=secret,
        )
        if result.returncode != 0:
            raise OSError(result.stderr.strip() or "secret-tool store failed")

    def delete(self, key: str) -> bool:
        return _run(["secret-tool", "clear", "service", SERVICE, "account", key]).returncode == 0


class KeychainStore:
    name = "macos-keychain"

    def available(self) -> bool:
        return sys.platform == "darwin" and bool(shutil.which("security"))

    def get(self, key: str) -> str | None:
        result = _run(["security", "find-generic-password", "-s", SERVICE, "-a", key, "-w"])
        return result.stdout.rstrip("\n") if result.returncode == 0 else None

    def set(self, key: str, secret: str) -> None:
        def q(text: str) -> str:
            return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'

        # `security -i` reads the command from stdin, so the password never reaches argv.
        command = f"add-generic-password -U -s {q(SERVICE)} -a {q(key)} -w {q(secret)}\n"
        result = _run(["security", "-i"], stdin=command)
        if result.returncode != 0:
            raise OSError(result.stderr.strip() or "security add-generic-password failed")

    def delete(self, key: str) -> bool:
        return (
            _run(["security", "delete-generic-password", "-s", SERVICE, "-a", key]).returncode == 0
        )


class _FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", ctypes.c_uint32), ("dwHighDateTime", ctypes.c_uint32)]


class _CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ("Flags", ctypes.c_uint32),
        ("Type", ctypes.c_uint32),
        ("TargetName", ctypes.c_wchar_p),
        ("Comment", ctypes.c_wchar_p),
        ("LastWritten", _FILETIME),
        ("CredentialBlobSize", ctypes.c_uint32),
        ("CredentialBlob", ctypes.c_void_p),
        ("Persist", ctypes.c_uint32),
        ("AttributeCount", ctypes.c_uint32),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", ctypes.c_wchar_p),
        ("UserName", ctypes.c_wchar_p),
    ]


def _advapi() -> Any:
    loader = getattr(ctypes, "WinDLL", ctypes.CDLL)
    return loader("advapi32")


class WindowsCredentialStore:
    """Windows Credential Manager via advapi32 (CredWriteW / CredReadW / CredDeleteW)."""

    name = "windows-credential-manager"

    def available(self) -> bool:
        return sys.platform == "win32"

    @staticmethod
    def _target(key: str) -> str:
        return f"{SERVICE}:{key}"

    def get(self, key: str) -> str | None:
        if not self.available():
            return None
        cred = ctypes.POINTER(_CREDENTIAL)()
        api = _advapi()
        if not api.CredReadW(self._target(key), 1, 0, ctypes.byref(cred)):
            return None
        try:
            blob = ctypes.string_at(cred.contents.CredentialBlob, cred.contents.CredentialBlobSize)
            return blob.decode("utf-16-le")
        finally:
            api.CredFree(cred)

    def set(self, key: str, secret: str) -> None:
        if not self.available():
            raise OSError("not Windows")
        blob = secret.encode("utf-16-le")
        buffer = ctypes.create_string_buffer(blob, len(blob))
        cred = _CREDENTIAL()
        cred.Type = 1  # CRED_TYPE_GENERIC
        cred.TargetName = self._target(key)
        cred.CredentialBlobSize = len(blob)
        cred.CredentialBlob = ctypes.cast(buffer, ctypes.c_void_p).value
        cred.Persist = 2  # CRED_PERSIST_LOCAL_MACHINE
        cred.UserName = key.rsplit(":", 1)[-1]
        if not _advapi().CredWriteW(ctypes.byref(cred), 0):
            raise OSError("CredWriteW failed")

    def delete(self, key: str) -> bool:
        if not self.available():
            return False
        return bool(_advapi().CredDeleteW(self._target(key), 1, 0))


def keyring_stores() -> list[Store]:
    return [SecretToolStore(), KeychainStore(), WindowsCredentialStore()]


def available_keyring() -> Store | None:
    for store_ in keyring_stores():
        if store_.available():
            return store_
    return None


def keyring_get(key: str) -> str | None:
    for store_ in keyring_stores():
        if store_.available():
            try:
                found = store_.get(key)
            except (OSError, subprocess.SubprocessError):
                found = None
            if found:
                return found
    return None
