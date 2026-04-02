from __future__ import annotations

import argparse
import logging
import sys
from importlib.metadata import PackageNotFoundError, version

from cloudpilot.cost_optimizer import get_aws_cost_optimization
from cloudpilot.k8s_autotuner import tune_deployment
from cloudpilot.scaling import recommend_scaling

try:
    _VERSION = version("cloudpilot")
except PackageNotFoundError:
    _VERSION = "0.0.0-dev"


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        description="CloudPilot CLI Utility - AI-Driven Infrastructure Optimization"
    )
    parser.add_argument("--version", action="version", version=f"CloudPilot {_VERSION}")

    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    parser_scale = subparsers.add_parser(
        "scale", help="Get scaling recommendation using the RL-based model."
    )
    parser_scale.add_argument(
        "--cpu",
        type=float,
        required=True,
        help="Average CPU utilization percentage (e.g., 75.0).",
    )
    parser_scale.add_argument(
        "--mem",
        type=float,
        required=True,
        help="Average memory utilization percentage (e.g., 65.0).",
    )
    parser_scale.add_argument(
        "--req",
        type=float,
        required=True,
        help="Average request rate (normalized or raw, e.g., 0.8).",
    )
    parser_scale.add_argument(
        "--latency",
        type=float,
        required=True,
        help="Average network latency in milliseconds (e.g., 100).",
    )
    parser_scale.add_argument(
        "--demand",
        type=float,
        required=True,
        help="Normalized user demand between 0 and 1 (e.g., 0.9).",
    )

    parser_cost = subparsers.add_parser(
        "cost", help="Get cost optimization recommendation for an AWS instance type."
    )
    parser_cost.add_argument(
        "--instance-type",
        type=str,
        default="m5.large",
        help="Current AWS instance type (default: m5.large).",
    )

    parser_tune = subparsers.add_parser(
        "tune", help="Auto-tune a Kubernetes deployment and check for anomalies."
    )
    parser_tune.add_argument(
        "--deployment",
        type=str,
        required=True,
        help="Name of the Kubernetes deployment.",
    )
    parser_tune.add_argument(
        "--namespace",
        type=str,
        default="default",
        help="Kubernetes namespace (default: 'default').",
    )

    args = parser.parse_args()

    if args.command == "scale":
        if not 0 <= args.demand <= 1:
            sys.exit("Error: --demand must be between 0 and 1.")
        recommendation = recommend_scaling(
            args.cpu, args.mem, args.req, args.latency, args.demand
        )
        print("Scaling Recommendation:", recommendation)
    elif args.command == "cost":
        recommendation = get_aws_cost_optimization(args.instance_type)
        print("Cost Optimization Recommendation:", recommendation)
    elif args.command == "tune":
        result = tune_deployment(args.deployment, args.namespace)
        print("Kubernetes Auto-Tuning Result:", result)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
