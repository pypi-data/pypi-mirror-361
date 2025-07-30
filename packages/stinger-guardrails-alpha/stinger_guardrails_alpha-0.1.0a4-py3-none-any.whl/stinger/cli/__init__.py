"""Stinger CLI module."""

from .main import main
from .setup_wizard import SetupWizard, run_setup

__all__ = ["SetupWizard", "run_setup", "main"]
