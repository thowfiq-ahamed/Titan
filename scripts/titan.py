#!/usr/bin/env python3
"""
TITAN CLI - Platform Engineering & Reliability Intelligence Command-Line Interface
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_API_URL = os.environ.get("TITAN_API_URL", "http://localhost:8000")
DEFAULT_API_KEY = os.environ.get("TITAN_API_KEY", "titan-platform-master-key-2026")


def make_request(path: str, method: str = "GET", payload: dict = None) -> dict:
    url = f"{DEFAULT_API_URL}{path}"
    headers = {
        "User-Agent": "titan-cli/1.0",
        "Content-Type": "application/json",
        "X-Titan-API-Key": DEFAULT_API_KEY
    }
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            if res.status == 204:
                return {}
            content = res.read().decode("utf-8")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as exc:
        err_msg = exc.read().decode("utf-8")
        try:
            parsed = json.loads(err_msg)
            print(f"Error ({exc.code}): {parsed.get('detail') or parsed.get('message') or err_msg}", file=sys.stderr)
        except Exception:
            print(f"Error ({exc.code}): {err_msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"Connection failure to {url}: {exc.reason}", file=sys.stderr)
        print("Ensure TITAN Platform API is running (`uvicorn services.platform_api.src.main:app`).", file=sys.stderr)
        sys.exit(1)


def cmd_health(args):
    res = make_request("/health/ready")
    print(f"TITAN Platform API Status: {res.get('status', 'unknown').upper()}")
    print(f"Service: {res.get('service')} v{res.get('version')}")


def cmd_service_list(args):
    services = make_request("/api/v1/services")
    print(f"\n{'NAME':<20} {'TIER':<10} {'TEAM':<24} {'HEALTH ENDPOINT':<20}")
    print("-" * 76)
    for s in services:
        print(f"{s['name']:<20} {s['tier']:<10} {s['owner_team']:<24} {s['health_endpoint']:<20}")
    print(f"\nTotal registered services: {len(services)}")


def cmd_service_register(args):
    payload = {
        "name": args.name,
        "display_name": args.display_name or args.name.replace("-", " ").title(),
        "description": args.description or f"Microservice {args.name}",
        "owner_team": args.owner_team,
        "tier": args.tier,
        "health_endpoint": args.health,
        "metrics_endpoint": args.metrics
    }
    res = make_request("/api/v1/services", method="POST", payload=payload)
    print(f"Successfully registered service '{res['name']}' (ID: {res['id']})")


def cmd_env_list(args):
    envs = make_request("/api/v1/environments")
    print(f"\n{'ENVIRONMENT':<12} {'NAMESPACE':<20} {'CLUSTER':<22} {'REPLICAS':<10} {'CPU/MEM LIMIT'}")
    print("-" * 80)
    for e in envs:
        print(f"{e['name']:<12} {e['namespace']:<20} {e['cluster_name']:<22} {e['replicas']:<10} {e['cpu_limit']}/{e['memory_limit']}")


def cmd_incident_list(args):
    incidents = make_request("/api/v1/incidents")
    print(f"\n{'ID':<38} {'SEVERITY':<10} {'CATEGORY':<20} {'STATUS':<15} {'CAUSE'}")
    print("-" * 110)
    for inc in incidents:
        cause_snip = (inc['suspected_cause'][:35] + '..') if len(inc['suspected_cause']) > 35 else inc['suspected_cause']
        print(f"{inc['id']:<38} {inc['severity']:<10} {inc['category']:<20} {inc['recovery_status']:<15} {cause_snip}")
    print(f"\nTotal recorded incidents: {len(incidents)}")


def cmd_benchmark_summary(args):
    summary = make_request("/api/v1/benchmarks/summary")
    print("\n" + "=" * 60)
    print("      TITAN RELIABILITY BENCHMARK & RESILIENCE REPORT      ")
    print("=" * 60)
    print(f"Total Experiment Trials:     {summary['total_experiments']}")
    print(f"Successful Recoveries:       {summary['successful_recoveries']}")
    print(f"Failed Recoveries:           {summary['failed_recoveries']}")
    print(f"Overall Recovery Rate:       {summary['recovery_success_rate_pct']}%")
    print(f"Mean Time To Detect (MTTD):  {summary['mean_time_to_detect_seconds']}s")
    print(f"Mean Time To Diagnose:       {summary['mean_time_to_diagnose_seconds']}s")
    print(f"Mean Time To Recover (MTTR): {summary['mean_time_to_recover_seconds']}s")
    print("-" * 60)
    print(f"{'STRATEGY':<22} {'TRIALS':<10} {'SUCCESS RATE':<15} {'MTTR (SEC)'}")
    print("-" * 60)
    for strat, data in summary.get("strategy_breakdown", {}).items():
        print(f"{strat:<22} {data['trials']:<10} {data['success_rate_pct']:<15}% {data['mean_recovery_sec']}s")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        prog="titan",
        description="TITAN: Cloud-Native Platform Engineering & Reliability Intelligence CLI"
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # health
    subparsers.add_parser("health", help="Check Platform API health")

    # service
    service_parser = subparsers.add_parser("service", help="Manage service catalog")
    service_sub = service_parser.add_subparsers(dest="action", help="Service actions")
    service_sub.add_parser("list", help="List registered services")
    reg_parser = service_sub.add_parser("register", help="Register a service")
    reg_parser.add_argument("--name", required=True, help="Unique service name")
    reg_parser.add_argument("--display-name", help="Display name")
    reg_parser.add_argument("--description", help="Description")
    reg_parser.add_argument("--owner-team", default="platform-engineering")
    reg_parser.add_argument("--tier", default="tier-1", choices=["tier-0", "tier-1", "tier-2"])
    reg_parser.add_argument("--health", default="/health/ready")
    reg_parser.add_argument("--metrics", default="/metrics")

    # env
    env_parser = subparsers.add_parser("env", help="Manage environments")
    env_sub = env_parser.add_subparsers(dest="action", help="Environment actions")
    env_sub.add_parser("list", help="List environments")

    # incident
    inc_parser = subparsers.add_parser("incident", help="Inspect incidents")
    inc_sub = inc_parser.add_subparsers(dest="action", help="Incident actions")
    inc_sub.add_parser("list", help="List incidents")

    # benchmark
    bm_parser = subparsers.add_parser("benchmark", help="Reliability benchmarks")
    bm_sub = bm_parser.add_subparsers(dest="action", help="Benchmark actions")
    bm_sub.add_parser("summary", help="Show reliability benchmark summary")

    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "health":
        cmd_health(args)
    elif args.subcommand == "service":
        if args.action == "list":
            cmd_service_list(args)
        elif args.action == "register":
            cmd_service_register(args)
        else:
            service_parser.print_help()
    elif args.subcommand == "env":
        if args.action == "list":
            cmd_env_list(args)
        else:
            env_parser.print_help()
    elif args.subcommand == "incident":
        if args.action == "list":
            cmd_incident_list(args)
        else:
            inc_parser.print_help()
    elif args.subcommand == "benchmark":
        if args.action == "summary":
            cmd_benchmark_summary(args)
        else:
            bm_parser.print_help()


if __name__ == "__main__":
    main()
