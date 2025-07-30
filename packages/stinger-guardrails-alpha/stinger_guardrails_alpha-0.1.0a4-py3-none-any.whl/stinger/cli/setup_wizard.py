"""
Setup wizard for Stinger Guardrails Framework.
Helps users configure their environment and get started quickly.
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path


class SetupWizard:
    """Interactive setup wizard for Stinger."""

    def __init__(self):
        self.config_dir = Path.home() / ".stinger"
        self.config_file = self.config_dir / "config.json"
        self.samples_dir = self.config_dir / "samples"
        self.platform = platform.system().lower()

    def run(self) -> bool:
        """Run the complete setup wizard."""
        print("\n🛡️  Welcome to Stinger Guardrails Setup Wizard")
        print("=" * 50)
        print("This wizard will help you:")
        print("  ✓ Check system requirements")
        print("  ✓ Configure API keys")
        print("  ✓ Create sample configurations")
        print("  ✓ Test your installation")
        print("=" * 50)

        # Step 1: Check environment
        if not self._check_environment():
            return False

        # Step 2: Configure API keys
        self._configure_api_keys()

        # Step 3: Create sample configurations
        self._create_sample_configs()

        # Step 4: Test installation
        if not self._test_installation():
            return False

        # Step 5: Show next steps
        self._show_next_steps()

        return True

    def _check_environment(self) -> bool:
        """Check Python version and dependencies."""
        print("\n📋 Checking Environment...")
        print("-" * 30)

        # Check Python version
        python_version = sys.version_info
        print(
            f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

        if python_version < (3, 8):
            print("❌ Python 3.8 or higher is required")
            return False
        else:
            print("✅ Python version is compatible")

        # Check if running in virtual environment
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            print("✅ Running in virtual environment")
        else:
            print("⚠️  Not running in virtual environment (recommended but not required)")

        # Check key dependencies
        dependencies = {
            "yaml": "PyYAML",
            "jsonschema": "jsonschema",
            "cryptography": "cryptography",
        }

        missing = []
        for module, package in dependencies.items():
            try:
                __import__(module)
                print(f"✅ {package} is installed")
            except ImportError:
                print(f"❌ {package} is not installed")
                missing.append(package)

        if missing:
            print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
            response = input("Would you like to install them now? (y/n): ").lower()
            if response == "y":
                return self._install_dependencies(missing)
            else:
                print("Please install missing dependencies manually")
                return False

        return True

    def _install_dependencies(self, packages: list) -> bool:
        """Install missing dependencies."""
        print("\n📦 Installing dependencies...")
        try:
            cmd = [sys.executable, "-m", "pip", "install"] + packages
            subprocess.run(cmd, check=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

    def _configure_api_keys(self):
        """Configure API keys for AI-powered guardrails."""
        print("\n🔑 API Key Configuration")
        print("-" * 30)
        print("AI-powered guardrails require an OpenAI API key.")
        print("You can skip this if you only plan to use local guardrails.\n")

        # Check if API key already exists
        existing_key = os.environ.get("OPENAI_API_KEY")
        if existing_key:
            print("✅ OPENAI_API_KEY found in environment")
            use_existing = input("Use existing key? (y/n): ").lower()
            if use_existing == "y":
                return

        # Ask for configuration method
        print("\nHow would you like to configure your API key?")
        print("1. Set as environment variable (recommended)")
        print("2. Store in macOS Keychain (macOS only)")
        print("3. Skip for now")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            self._setup_env_var()
        elif choice == "2" and self.platform == "darwin":
            self._setup_keychain()
        elif choice == "3":
            print("⚠️  Skipping API key configuration")
            print("   AI-powered guardrails will not work without an API key")
        else:
            print("Invalid choice or option not available on your platform")

    def _setup_env_var(self):
        """Set up API key as environment variable."""
        print("\nTo set your API key as an environment variable:")
        print("\n1. Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("\n2. Or create a .env file in your project:")
        print("   OPENAI_API_KEY=your-api-key-here")
        print("\n3. Then reload your shell or source the file")

        # Offer to create .env file
        create_env = input("\nCreate a .env file in the current directory? (y/n): ").lower()
        if create_env == "y":
            api_key = input("Enter your OpenAI API key: ").strip()
            if api_key:
                with open(".env", "w") as f:
                    f.write(f"OPENAI_API_KEY={api_key}\n")
                print("✅ Created .env file")
                print("⚠️  Remember to add .env to your .gitignore!")

    def _setup_keychain(self):
        """Set up API key in macOS Keychain."""
        print("\nSetting up API key in macOS Keychain...")
        api_key = input("Enter your OpenAI API key: ").strip()

        if api_key:
            try:
                # Use stdin to pass the key securely
                cmd = [
                    "security",
                    "add-generic-password",
                    "-a",
                    os.environ.get("USER", "stinger"),
                    "-s",
                    "openai-api-key",
                    "-w",  # Read password from stdin
                ]
                # Pass the API key via stdin to avoid command line exposure
                subprocess.run(cmd, input=api_key.encode("utf-8"), check=True, capture_output=True)
                print("✅ API key stored in Keychain")

                print("\nTo use this key, add to your shell profile:")
                print(
                    "export OPENAI_API_KEY=$(security find-generic-password -w -s openai-api-key)"
                )

            except subprocess.CalledProcessError:
                print("❌ Failed to store in Keychain")

    def _create_sample_configs(self):
        """Create sample configuration files."""
        print("\n📁 Creating Sample Configurations")
        print("-" * 30)

        # Create config directory
        self.config_dir.mkdir(exist_ok=True)
        self.samples_dir.mkdir(exist_ok=True)

        # Sample pipeline configuration
        sample_pipeline = {
            "input_guardrails": [
                {"type": "keyword_list", "keywords": ["hack", "exploit", "injection"]},
                {"type": "length", "max_length": 1000},
                {"type": "pii_detection", "enabled": True},
            ],
            "output_guardrails": [
                {"type": "toxicity", "threshold": 0.7},
                {"type": "code_generation", "allowed": False},
            ],
        }

        # Write sample pipeline
        pipeline_file = self.samples_dir / "sample_pipeline.yaml"
        with open(pipeline_file, "w") as f:
            import yaml

            yaml.dump(sample_pipeline, f, default_flow_style=False)
        print(f"✅ Created sample pipeline: {pipeline_file}")

        # Sample keywords file
        keywords_file = self.samples_dir / "blocked_keywords.txt"
        with open(keywords_file, "w") as f:
            f.write("# Blocked keywords (one per line)\n")
            f.write("hack\n")
            f.write("exploit\n")
            f.write("injection\n")
            f.write("malware\n")
        print(f"✅ Created keywords file: {keywords_file}")

        # User configuration
        user_config = {
            "default_preset": "customer_service",
            "audit_enabled": True,
            "samples_dir": str(self.samples_dir),
        }

        with open(self.config_file, "w") as f:
            json.dump(user_config, f, indent=2)
        print(f"✅ Created user config: {self.config_file}")

    def _test_installation(self) -> bool:
        """Test the installation with a simple example."""
        print("\n🧪 Testing Installation")
        print("-" * 30)

        try:
            # Import core modules
            print("Testing imports...")
            from stinger.guardrails.keyword_list import KeywordListGuardrail

            print("✅ Core modules imported successfully")

            # Create a simple pipeline
            print("\nTesting basic guardrail...")
            guardrail = KeywordListGuardrail({"keywords": ["test", "hack"], "match_type": "exact"})

            # Test with safe content
            safe_result = guardrail.check("This is a safe message")
            if not safe_result.blocked:
                print("✅ Safe content passed")
            else:
                print("❌ Safe content was blocked")
                return False

            # Test with blocked content
            blocked_result = guardrail.check("This is a hack attempt")
            if blocked_result.blocked:
                print("✅ Harmful content blocked")
            else:
                print("❌ Harmful content was not blocked")
                return False

            print("\n✅ All tests passed!")
            return True

        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            print("\nPlease ensure Stinger is properly installed:")
            print("  pip install stinger-guardrails-alpha")
            return False

    def _show_next_steps(self):
        """Show next steps to the user."""
        print("\n🎉 Setup Complete!")
        print("=" * 50)
        print("\n📚 Next Steps:")
        print("\n1. Try the demo:")
        print("   stinger demo")
        print("\n2. Check a prompt:")
        print('   stinger check-prompt "Your text here"')
        print("\n3. View health status:")
        print("   stinger health")
        print("\n4. Explore examples:")
        print("   - Check the examples/ directory")
        print(f"   - View samples in {self.samples_dir}")
        print("\n5. Read the documentation:")
        print("   https://github.com/virtualsteve-star/stinger")
        print("\n" + "=" * 50)
        print("Happy guarding! 🛡️\n")


def run_setup():
    """Entry point for setup command."""
    wizard = SetupWizard()
    success = wizard.run()
    return 0 if success else 1
