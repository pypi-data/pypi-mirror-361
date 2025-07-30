import argparse
import sys
from importlib.metadata import version

from stinger.cli.first_run import check_first_run
from stinger.cli.setup_wizard import run_setup
from stinger.core.health_monitor import HealthMonitor, print_health_status
from stinger.core.pipeline import GuardrailPipeline


def get_version():
    """Get the version of the stinger package."""
    try:
        return version("stinger-guardrails-alpha")
    except Exception:
        return "unknown"


def run_demo():
    print("\n[Stinger Demo]\n")
    pipeline = GuardrailPipeline.from_preset("customer_service")
    prompt = "My credit card number is 1234-5678-9012-3456."
    print(f"User Prompt: {prompt}")
    result = pipeline.check_input(prompt)
    print(f"Result: {'BLOCKED' if result['blocked'] else 'ALLOWED'}")
    if result["reasons"]:
        print("Reasons:")
        for reason in result["reasons"]:
            print(f"  - {reason}")


def check_prompt(prompt: str):
    pipeline = GuardrailPipeline.from_preset("customer_service")
    result = pipeline.check_input(prompt)
    print(f"Prompt: {prompt}\nResult: {'BLOCKED' if result['blocked'] else 'ALLOWED'}")
    if result["reasons"]:
        print("Reasons:")
        for reason in result["reasons"]:
            print(f"  - {reason}")


def check_response(response: str):
    pipeline = GuardrailPipeline.from_preset("customer_service")
    result = pipeline.check_output(response)
    print(f"Response: {response}\nResult: {'BLOCKED' if result['blocked'] else 'ALLOWED'}")
    if result["reasons"]:
        print("Reasons:")
        for reason in result["reasons"]:
            print(f"  - {reason}")


def show_health(detailed: bool = False):
    """Show system health status."""
    try:
        # Create a pipeline for health monitoring
        pipeline = GuardrailPipeline.from_preset("customer_service")

        # Create health monitor
        monitor = HealthMonitor(pipeline=pipeline)

        # Get health status
        health = monitor.get_system_health()

        # Print health status
        print_health_status(health, detailed=detailed)

    except Exception as e:
        print(f"❌ Error getting health status: {e}")
        return False

    return True


def main():
    # Check for first run experience
    if len(sys.argv) == 1:  # No command provided
        first_run_result = check_first_run()
        if first_run_result is not None:
            return first_run_result

    parser = argparse.ArgumentParser(description="Stinger CLI - LLM Guardrails")
    parser.add_argument("--version", action="version", version=f"%(prog)s {get_version()}")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("demo", help="Run a demo guardrail check")

    prompt_parser = subparsers.add_parser("check-prompt", help="Check a user prompt for safety")
    prompt_parser.add_argument("prompt", type=str, help="Prompt to check")

    response_parser = subparsers.add_parser(
        "check-response", help="Check a model response for safety"
    )
    response_parser.add_argument("response", type=str, help="Response to check")

    health_parser = subparsers.add_parser("health", help="Show system health status")
    health_parser.add_argument(
        "--detailed", "-d", action="store_true", help="Show detailed health information"
    )

    subparsers.add_parser("setup", help="Run interactive setup wizard")

    args = parser.parse_args()
    if args.command == "demo":
        run_demo()
    elif args.command == "check-prompt":
        check_prompt(args.prompt)
    elif args.command == "check-response":
        check_response(args.response)
    elif args.command == "health":
        show_health(detailed=args.detailed)
    elif args.command == "setup":
        return run_setup()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
