"""Compatibility entry point for the current edition-switch browser checks."""
import subprocess
import sys
from pathlib import Path

command = [sys.executable, str(Path(__file__).with_name("profile_switch_acceptance.py"))]
if len(sys.argv) > 1:
    command += ["--exe", sys.argv[1]]
raise SystemExit(subprocess.call(command))
