#!/usr/bin/env python3
"""
Universal binary download script for HipHops Hook.

This script works in both build-time (cibuildwheel) and runtime contexts,
automatically detecting the appropriate platform and downloading the correct binary.
"""

import os
import ssl
import stat
import sys
import urllib.request
import urllib.error
from pathlib import Path


def get_binary_name():
    """Get the binary name based on platform detection."""
    import platform as platform_module

    # Detect platform and architecture
    system = platform_module.system().lower()

    # Check if we're in a cibuildwheel context
    cibw_archs = os.environ.get("CIBW_ARCHS", "").lower().strip()
    if cibw_archs:
        # Build-time context: use CIBW_ARCHS
        arch = cibw_archs
        print(f"Build context - System: {system}, CIBW_ARCHS: '{arch}'")
    else:
        # Runtime context: detect from machine
        machine = platform_module.machine().lower()
        print(f"Runtime context - System: {system}, Machine: {machine}")

        # Normalize architecture names
        if machine in ["x86_64", "amd64"]:
            arch = "x86_64"
        elif machine in ["arm64", "aarch64"]:
            arch = "arm64"
        else:
            arch = machine

    # Map platform and architecture to binary names
    if system == "linux":
        if arch in ["x86_64", "amd64"]:
            return "hook-linux-amd64"
        elif arch in ["aarch64", "arm64"]:
            return "hook-linux-arm64"
    elif system == "darwin":
        if arch in ["x86_64", "amd64"]:
            return "hook-darwin-amd64"
        elif arch in ["arm64"]:
            return "hook-darwin-arm64"
    elif system == "windows":
        if arch in ["amd64", "x86_64"]:
            return "hook-windows-amd64.exe"

    raise RuntimeError(f"Unsupported platform/arch combination: {system}/{arch}")


def get_version():
    """Get the package version, detecting build vs runtime context."""
    # First try to import from the package (runtime context)
    try:
        from hiphops_hook import __version__

        return __version__
    except ImportError:
        # Fall back to parsing pyproject.toml (build context or package not installed)
        import re

        script_dir = Path(__file__).parent

        # Try build context path first (scripts/ in project root)
        project_root = script_dir.parent.parent
        pyproject_path = project_root / "pyproject.toml"

        # If not found, try runtime context path (scripts/ in package)
        if not pyproject_path.exists():
            project_root = script_dir.parent.parent
            pyproject_path = project_root / "pyproject.toml"

        if not pyproject_path.exists():
            raise RuntimeError(f"Could not find pyproject.toml at {pyproject_path}")

        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if not match:
            raise RuntimeError("Could not find version in pyproject.toml")

        return match.group(1)


def get_bin_directory():
    """Get the appropriate bin directory based on context."""
    script_dir = Path(__file__).parent

    # Check if we're in build context (scripts/ in project root)
    if (script_dir.parent / "pyproject.toml").exists():
        # Build context: put binaries in hiphops_hook/bin/
        return script_dir.parent / "hiphops_hook" / "bin"
    else:
        # Runtime context: put binaries in package bin/
        return script_dir.parent / "bin"


def download_binary():
    """Download the Hook binary for the current platform."""
    try:
        binary_name = get_binary_name()
        version = get_version()

        print(f"Package version: {version}")
        print(f"Binary name: {binary_name}")

        # Get appropriate bin directory
        bin_dir = get_bin_directory()
        bin_dir.mkdir(exist_ok=True)

        binary_path = bin_dir / binary_name

        # Skip if binary already exists
        if binary_path.exists():
            print(f"Binary already exists at: {binary_path}")
            return

        # Download URL
        download_url = f"https://github.com/hiphops-io/hook/releases/download/v{version}/{binary_name}"

        print(f"Downloading from: {download_url}")
        print(f"Saving to: {binary_path}")

        # Try to download with SSL verification first, fallback to no verification
        response = None
        try:
            # Create SSL context that handles certificate verification
            ssl_context = ssl.create_default_context()
            response = urllib.request.urlopen(download_url, context=ssl_context)
        except urllib.error.URLError as e:
            if "certificate verify failed" in str(e):
                print(
                    "WARNING: SSL certificate verification failed, retrying without verification..."
                )
                # Create unverified SSL context as fallback
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                response = urllib.request.urlopen(download_url, context=ssl_context)
            else:
                raise

        # Download the binary
        with response:
            if response.status != 200:
                raise RuntimeError(
                    f"Failed to download binary. Status code: {response.status}"
                )

            # Write binary to file
            with open(binary_path, "wb") as f:
                f.write(response.read())

        # Make binary executable on Unix-like systems
        if not binary_name.endswith(".exe"):
            current_mode = binary_path.stat().st_mode
            binary_path.chmod(current_mode | stat.S_IEXEC)

        print(f"Successfully downloaded binary to {binary_path}")
        print(f"Binary size: {binary_path.stat().st_size} bytes")

    except Exception as e:
        print(f"Error during binary download: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    print("Starting Hook binary download...")
    download_binary()
    print("Binary download completed successfully!")
