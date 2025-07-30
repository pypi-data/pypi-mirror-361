"""
First run experience for Stinger.
Shows a welcome message and guides users through initial setup.
"""

import os
from pathlib import Path
from typing import Optional


class FirstRunExperience:
    """Handles the first run experience for new users."""

    def __init__(self):
        self.config_dir = Path.home() / ".stinger"
        self.first_run_file = self.config_dir / ".first_run_complete"

    def should_show(self) -> bool:
        """Check if we should show the first run experience."""
        # Skip if explicitly disabled
        if os.environ.get("STINGER_SKIP_FIRST_RUN") == "1":
            return False

        # Skip if already completed
        if self.first_run_file.exists():
            return False

        return True

    def show(self) -> Optional[int]:
        """Show the first run experience."""
        print("\n" + "=" * 60)
        print("🎉 Welcome to Stinger Guardrails Framework!")
        print("=" * 60)
        print("\nIt looks like this is your first time using Stinger.")
        print("Let's get you set up!\n")

        # Ask if they want to run setup
        response = (
            input("Would you like to run the setup wizard? (recommended) [Y/n]: ").strip().lower()
        )

        if response in ["", "y", "yes"]:
            print("\nStarting setup wizard...\n")
            from stinger.cli.setup_wizard import run_setup

            result = run_setup()

            # Mark first run as complete
            self._mark_complete()

            return result
        else:
            print("\nYou can run setup later with: stinger setup")
            print("\nHere are some commands to get started:")
            print("  stinger demo              - Run a demo")
            print("  stinger check-prompt TEXT - Check a prompt")
            print("  stinger health           - Show system status")
            print("  stinger setup            - Run setup wizard")

            # Mark first run as complete
            self._mark_complete()

            return None

    def _mark_complete(self):
        """Mark the first run as complete."""
        self.config_dir.mkdir(exist_ok=True)
        self.first_run_file.touch()


def check_first_run() -> Optional[int]:
    """Check and potentially show first run experience."""
    first_run = FirstRunExperience()
    if first_run.should_show():
        return first_run.show()
    return None
