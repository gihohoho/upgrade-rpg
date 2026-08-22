#!/usr/bin/env python3
"""Create and verify local secret/artifact paths with an exact private ACL.

Errors intentionally omit paths, account names, and SID values. Windows paths
keep only the current user, LocalSystem, and Builtin Administrators as explicit
FullControl allow entries, are owned by the current user, and do not inherit
rules. POSIX paths require current ownership and exact 0600/0700 modes.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path
import secrets
import stat
import subprocess


class PrivatePathError(RuntimeError):
    """A private-path failure whose message is safe for logs and reports."""


_WINDOWS_ACL_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
$path = [Environment]::GetEnvironmentVariable('UPGRADE_RPG_PRIVATE_PATH', 'Process')
$action = [Environment]::GetEnvironmentVariable('UPGRADE_RPG_PRIVATE_ACTION', 'Process')
$expectedKind = [Environment]::GetEnvironmentVariable('UPGRADE_RPG_PRIVATE_KIND', 'Process')
if ([string]::IsNullOrWhiteSpace($path)) { exit 40 }

$currentSid = [Security.Principal.WindowsIdentity]::GetCurrent().User
$systemSid = New-Object Security.Principal.SecurityIdentifier('S-1-5-18')
$administratorsSid = New-Object Security.Principal.SecurityIdentifier('S-1-5-32-544')
$expectedSids = @($currentSid.Value, $systemSid.Value, $administratorsSid.Value)

function New-PrivateSecurity([bool]$isDirectory) {
    if ($isDirectory) {
        $security = New-Object Security.AccessControl.DirectorySecurity
        $inheritance = [Security.AccessControl.InheritanceFlags]::ContainerInherit -bor
            [Security.AccessControl.InheritanceFlags]::ObjectInherit
    } else {
        $security = New-Object Security.AccessControl.FileSecurity
        $inheritance = [Security.AccessControl.InheritanceFlags]::None
    }
    $security.SetOwner($currentSid)
    $security.SetAccessRuleProtection($true, $false)
    foreach ($sid in @($currentSid, $systemSid, $administratorsSid)) {
        $rule = New-Object Security.AccessControl.FileSystemAccessRule(
            $sid,
            [Security.AccessControl.FileSystemRights]::FullControl,
            $inheritance,
            [Security.AccessControl.PropagationFlags]::None,
            [Security.AccessControl.AccessControlType]::Allow
        )
        [void]$security.AddAccessRule($rule)
    }
    return $security
}

if ($action -eq 'create-file') {
    if (Test-Path -LiteralPath $path) { exit 41 }
    $parent = Get-Item -LiteralPath ([IO.Path]::GetDirectoryName($path)) -Force
    if (-not $parent.PSIsContainer) { exit 42 }
    if (($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { exit 43 }
    $security = New-PrivateSecurity($false)
    $stream = [IO.FileStream]::new(
        $path,
        [IO.FileMode]::CreateNew,
        [Security.AccessControl.FileSystemRights]::FullControl,
        [IO.FileShare]::None,
        4096,
        [IO.FileOptions]::WriteThrough,
        $security
    )
    $stream.Dispose()
} elseif ($action -eq 'create-directory') {
    if (Test-Path -LiteralPath $path) { exit 44 }
    $parent = Get-Item -LiteralPath ([IO.Path]::GetDirectoryName($path)) -Force
    if (-not $parent.PSIsContainer) { exit 45 }
    if (($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { exit 46 }
    $security = New-PrivateSecurity($true)
    [void][IO.Directory]::CreateDirectory($path, $security)
} else {
    $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { exit 47 }
    $isDirectory = [bool]$item.PSIsContainer
    if (($expectedKind -eq 'directory') -ne $isDirectory) { exit 48 }
    if ($action -eq 'harden') {
        $acl = Get-Acl -LiteralPath $path -ErrorAction Stop
        $acl.SetAccessRuleProtection($true, $false)
        foreach ($rule in @($acl.Access)) {
            [void]$acl.RemoveAccessRuleSpecific($rule)
        }
        $acl.SetOwner($currentSid)
        $inheritance = if ($isDirectory) {
            [Security.AccessControl.InheritanceFlags]::ContainerInherit -bor
                [Security.AccessControl.InheritanceFlags]::ObjectInherit
        } else {
            [Security.AccessControl.InheritanceFlags]::None
        }
        foreach ($sid in @($currentSid, $systemSid, $administratorsSid)) {
            $rule = New-Object Security.AccessControl.FileSystemAccessRule(
                $sid,
                [Security.AccessControl.FileSystemRights]::FullControl,
                $inheritance,
                [Security.AccessControl.PropagationFlags]::None,
                [Security.AccessControl.AccessControlType]::Allow
            )
            [void]$acl.AddAccessRule($rule)
        }
        if ($isDirectory) {
            $item.SetAccessControl($acl)
        } else {
            [IO.File]::SetAccessControl($path, $acl)
        }
    } elseif ($action -ne 'verify') {
        exit 49
    }
}

$item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { exit 50 }
$isDirectory = [bool]$item.PSIsContainer
if (($expectedKind -eq 'directory') -ne $isDirectory) { exit 51 }
$observed = Get-Acl -LiteralPath $path -ErrorAction Stop
if (-not $observed.AreAccessRulesProtected) { exit 52 }
$ownerAccount = New-Object Security.Principal.NTAccount($observed.Owner)
$ownerSid = $ownerAccount.Translate([Security.Principal.SecurityIdentifier]).Value
if ($ownerSid -ne $currentSid.Value) { exit 53 }
$rules = @($observed.GetAccessRules(
    $true,
    $true,
    [Security.Principal.SecurityIdentifier]
))
if ($rules.Count -ne 3) { exit 54 }
$seen = @{}
$expectedInheritance = if ($isDirectory) {
    [Security.AccessControl.InheritanceFlags]::ContainerInherit -bor
        [Security.AccessControl.InheritanceFlags]::ObjectInherit
} else {
    [Security.AccessControl.InheritanceFlags]::None
}
foreach ($rule in $rules) {
    $sid = $rule.IdentityReference.Value
    if ($expectedSids -notcontains $sid) { exit 55 }
    if ($seen.ContainsKey($sid)) { exit 56 }
    $seen[$sid] = $true
    if ($rule.AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow) {
        exit 57
    }
    if ($rule.IsInherited) { exit 58 }
    if ($rule.FileSystemRights -ne [Security.AccessControl.FileSystemRights]::FullControl) {
        exit 59
    }
    if ($rule.InheritanceFlags -ne $expectedInheritance) { exit 60 }
    if ($rule.PropagationFlags -ne [Security.AccessControl.PropagationFlags]::None) {
        exit 61
    }
}
if ($seen.Count -ne 3) { exit 62 }
exit 0
"""


def _encoded_windows_script() -> str:
    return base64.b64encode(_WINDOWS_ACL_SCRIPT.encode("utf-16le")).decode("ascii")


def _lexists(path: Path) -> bool:
    return os.path.lexists(os.fspath(path))


def _metadata(path: Path) -> os.stat_result:
    try:
        metadata = path.lstat()
    except OSError:
        raise PrivatePathError("private path is missing or unreadable") from None
    if stat.S_ISLNK(metadata.st_mode):
        raise PrivatePathError("private path type is unsafe")
    if os.name == "nt" and (
        getattr(metadata, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    ):
        raise PrivatePathError("private path type is unsafe")
    return metadata


def _reject_unsafe_type(path: Path, *, directory: bool) -> os.stat_result:
    metadata = _metadata(path)
    expected = stat.S_ISDIR(metadata.st_mode) if directory else stat.S_ISREG(metadata.st_mode)
    if not expected:
        raise PrivatePathError("private path type is unsafe")
    return metadata


def ensure_private_path_location(anchor: Path, path: Path) -> None:
    """Reject traversal outside an exact anchor and every existing reparse hop."""
    selected_anchor = Path(os.path.abspath(os.fspath(anchor)))
    selected = Path(os.path.abspath(os.fspath(path)))
    try:
        relative = selected.relative_to(selected_anchor)
    except ValueError:
        raise PrivatePathError("private path escaped its trusted root") from None
    anchor_metadata = _reject_unsafe_type(selected_anchor, directory=True)
    if not stat.S_ISDIR(anchor_metadata.st_mode):  # pragma: no cover - defensive
        raise PrivatePathError("private path root is unsafe")
    current = selected_anchor
    for part in relative.parts:
        current = current / part
        if not _lexists(current):
            continue
        _metadata(current)
    try:
        resolved_anchor = selected_anchor.resolve(strict=True)
        existing = selected
        while not _lexists(existing):
            if existing == selected_anchor:
                break
            existing = existing.parent
        resolved_existing = existing.resolve(strict=True)
        resolved_existing.relative_to(resolved_anchor)
    except (OSError, RuntimeError, ValueError):
        raise PrivatePathError("private path resolution is unsafe") from None


def _system_powershell() -> Path:
    try:
        import ctypes

        buffer = ctypes.create_unicode_buffer(32768)
        length = ctypes.windll.kernel32.GetSystemDirectoryW(buffer, len(buffer))
    except (AttributeError, OSError):
        raise PrivatePathError("private ACL system helper is unavailable") from None
    if not length or length >= len(buffer):
        raise PrivatePathError("private ACL system helper is unavailable")
    executable = Path(buffer.value) / "WindowsPowerShell/v1.0/powershell.exe"
    _reject_unsafe_type(executable, directory=False)
    return executable


def _windows_acl(path: Path, *, directory: bool, action: str) -> None:
    if action not in {"verify", "harden", "create-file", "create-directory"}:
        raise PrivatePathError("private ACL action is invalid")
    environment = os.environ.copy()
    environment.update(
        {
            "UPGRADE_RPG_PRIVATE_PATH": os.fspath(Path(os.path.abspath(path))),
            "UPGRADE_RPG_PRIVATE_ACTION": action,
            "UPGRADE_RPG_PRIVATE_KIND": "directory" if directory else "file",
        }
    )
    try:
        completed = subprocess.run(
            [
                str(_system_powershell()),
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-EncodedCommand",
                _encoded_windows_script(),
            ],
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        raise PrivatePathError("private ACL operation failed") from None
    if completed.returncode != 0:
        raise PrivatePathError("private ACL verification failed")


def _posix_verify(path: Path, *, directory: bool) -> None:
    metadata = _reject_unsafe_type(path, directory=directory)
    expected_mode = 0o700 if directory else 0o600
    if stat.S_IMODE(metadata.st_mode) != expected_mode:
        raise PrivatePathError("private mode verification failed")
    if metadata.st_uid != os.geteuid():
        raise PrivatePathError("private ownership verification failed")


def verify_private_path(path: Path, *, directory: bool) -> None:
    """Fail closed unless one path has the exact platform-private boundary."""
    selected = Path(path)
    _reject_unsafe_type(selected, directory=directory)
    if os.name == "nt":
        _windows_acl(selected, directory=directory, action="verify")
    else:
        _posix_verify(selected, directory=directory)


def harden_private_path(path: Path, *, directory: bool) -> None:
    """Replace one existing path's permissions with the private boundary."""
    selected = Path(path)
    _reject_unsafe_type(selected, directory=directory)
    try:
        if os.name == "nt":
            _windows_acl(selected, directory=directory, action="harden")
        else:
            selected.chmod(0o700 if directory else 0o600)
    except PrivatePathError:
        raise
    except OSError:
        raise PrivatePathError("private permission update failed") from None
    verify_private_path(selected, directory=directory)


def harden_private_file(path: Path) -> None:
    harden_private_path(path, directory=False)


def verify_private_file(path: Path) -> None:
    verify_private_path(path, directory=False)


def harden_private_directory(path: Path, *, create: bool = False) -> None:
    selected = Path(path)
    if create and not _lexists(selected):
        if not _lexists(selected.parent):
            raise PrivatePathError("private directory parent is missing")
        try:
            if os.name == "nt":
                _windows_acl(selected, directory=True, action="create-directory")
            else:
                selected.mkdir(exist_ok=False, mode=0o700)
        except PrivatePathError:
            raise
        except OSError:
            raise PrivatePathError("private directory creation failed") from None
    harden_private_path(selected, directory=True)


def verify_private_directory(path: Path) -> None:
    verify_private_path(path, directory=True)


def verify_private_tree(path: Path) -> None:
    """Verify every entry in one dedicated private tree without mutating it."""
    root = Path(path)
    verify_private_directory(root)
    try:
        entries = list(root.iterdir())
    except OSError:
        raise PrivatePathError("private directory traversal failed") from None
    for entry in entries:
        metadata = _metadata(entry)
        if stat.S_ISDIR(metadata.st_mode):
            verify_private_tree(entry)
        elif stat.S_ISREG(metadata.st_mode):
            verify_private_file(entry)
        else:
            raise PrivatePathError("private path type is unsafe")
    verify_private_directory(root)


def harden_private_tree(path: Path, *, create: bool = False) -> None:
    """Harden one dedicated artifact tree without touching its source parent."""
    root = Path(path)
    harden_private_directory(root, create=create)
    try:
        entries = list(root.iterdir())
    except OSError:
        raise PrivatePathError("private directory traversal failed") from None
    for entry in entries:
        metadata = _metadata(entry)
        if stat.S_ISDIR(metadata.st_mode):
            harden_private_tree(entry)
        elif stat.S_ISREG(metadata.st_mode):
            harden_private_file(entry)
        else:
            raise PrivatePathError("private path type is unsafe")
    verify_private_directory(root)


def create_private_file(path: Path) -> int:
    """Create an empty private file before content exists and return it open."""
    selected = Path(path)
    if _lexists(selected):
        raise PrivatePathError("private staging file already exists")
    descriptor: int | None = None
    try:
        if os.name == "nt":
            _windows_acl(selected, directory=False, action="create-file")
        else:
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(selected, flags, 0o600)
            os.close(descriptor)
            descriptor = None
            harden_private_file(selected)
        if selected.stat().st_size != 0:
            raise PrivatePathError("private staging file is not empty")
        flags = os.O_WRONLY | getattr(os, "O_BINARY", 0)
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(selected, flags)
        opened = os.fstat(descriptor)
        observed = selected.stat(follow_symlinks=False)
        if (opened.st_dev, opened.st_ino) != (observed.st_dev, observed.st_ino):
            raise PrivatePathError("private staging identity changed")
        verify_private_file(selected)
        return descriptor
    except PrivatePathError:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        try:
            selected.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    except OSError:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        try:
            selected.unlink(missing_ok=True)
        except OSError:
            pass
        raise PrivatePathError("private staging file creation failed") from None


def _fsync_parent_directory(path: Path) -> None:
    """Persist one created/replaced directory entry on POSIX filesystems."""
    if os.name == "nt":
        # Windows creation uses FileOptions.WriteThrough and the file itself is
        # flushed below. Windows does not expose the POSIX directory-fsync API.
        return
    parent = Path(path).parent
    descriptor: int | None = None
    try:
        expected = _reject_unsafe_type(parent, directory=True)
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(parent, flags)
        opened = os.fstat(descriptor)
        if not stat.S_ISDIR(opened.st_mode):
            raise PrivatePathError("private parent directory type is unsafe")
        if (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino):
            raise PrivatePathError("private parent directory identity changed")
        os.fsync(descriptor)
    except PrivatePathError:
        raise
    except OSError:
        raise PrivatePathError("private parent directory sync failed") from None
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


def write_private_bytes_atomic(path: Path, payload: bytes) -> None:
    """Write bytes through a private staging file and atomically replace."""
    selected = Path(path)
    if _lexists(selected):
        harden_private_file(selected)
    temporary = selected.with_name(
        f".{selected.name}.private.{os.getpid()}.{secrets.token_hex(8)}.tmp"
    )
    descriptor: int | None = None
    try:
        descriptor = create_private_file(temporary)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = None
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        harden_private_file(temporary)
        os.replace(temporary, selected)
        verify_private_file(selected)
        _fsync_parent_directory(selected)
    except PrivatePathError:
        raise
    except OSError:
        raise PrivatePathError("private atomic file write failed") from None
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


def write_private_bytes_exclusive(path: Path, payload: bytes) -> None:
    """Create one private file once; retain it as an attempt marker on failure."""
    selected = Path(path)
    descriptor: int | None = None
    try:
        descriptor = create_private_file(selected)
        stream = os.fdopen(descriptor, "wb")
        descriptor = None
        with stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        verify_private_file(selected)
        _fsync_parent_directory(selected)
    except PrivatePathError:
        raise
    except OSError:
        raise PrivatePathError("private exclusive file write failed") from None
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


def write_private_text_atomic(path: Path, text: str, *, encoding: str) -> None:
    write_private_bytes_atomic(path, text.encode(encoding))


def write_private_text_exclusive(path: Path, text: str, *, encoding: str) -> None:
    write_private_bytes_exclusive(path, text.encode(encoding))
