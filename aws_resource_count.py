import argparse
from collections import defaultdict

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError


def get_ec2_name(instance):
    for tag in instance.get("Tags", []):
        if tag.get("Key") == "Name" and tag.get("Value"):
            return tag["Value"]

    return instance["InstanceId"]


def add_resource(resources, resource_type, resource_name):
    resources[resource_type].append(resource_name)


def get_ec2_resources(region):
    client = boto3.client("ec2", region_name=region)
    paginator = client.get_paginator("describe_instances")
    resources = defaultdict(list)

    for page in paginator.paginate(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    ):
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                add_resource(
                    resources,
                    instance["InstanceType"],
                    get_ec2_name(instance),
                )

    return resources


def get_rds_resources(region):
    client = boto3.client("rds", region_name=region)
    paginator = client.get_paginator("describe_db_instances")
    resources = defaultdict(list)

    for page in paginator.paginate():
        for instance in page.get("DBInstances", []):
            if instance.get("DBInstanceStatus") == "available":
                add_resource(
                    resources,
                    instance["DBInstanceClass"],
                    instance["DBInstanceIdentifier"],
                )

    return resources


def get_elasticache_resources(region):
    client = boto3.client("elasticache", region_name=region)
    paginator = client.get_paginator("describe_cache_clusters")
    resources = defaultdict(list)

    for page in paginator.paginate(ShowCacheNodeInfo=True):
        for cluster in page.get("CacheClusters", []):
            if cluster.get("CacheClusterStatus") == "available":
                node_count = cluster.get("NumCacheNodes", 1)
                resource_name = cluster["CacheClusterId"]

                if node_count > 1:
                    resource_name = f"{resource_name} ({node_count} nodes)"

                resources[cluster["CacheNodeType"]].extend([resource_name] * node_count)

    return resources


def format_names(names):
    unique_names = []

    for name in names:
        if name not in unique_names:
            unique_names.append(name)

    return ", ".join(unique_names)


def build_rows(service_name, resources):
    rows = []

    if not resources:
        return [[service_name, "0", "-", "No running resources found"]]

    for resource_type, names in sorted(resources.items()):
        rows.append([service_name, str(len(names)), resource_type, format_names(names)])

    return rows


def print_table(rows):
    headers = ["Service", "Count", "Type", "Resource Names"]
    widths = [
        max(len(row[index]) for row in rows + [headers])
        for index in range(len(headers))
    ]

    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    header_line = "| " + " | ".join(
        headers[index].ljust(widths[index]) for index in range(len(headers))
    ) + " |"

    print(separator)
    print(header_line)
    print(separator)

    for row in rows:
        row_line = "| " + " | ".join(
            row[index].ljust(widths[index]) for index in range(len(row))
        ) + " |"
        print(row_line)

    print(separator)
    print()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Count AWS resources by type for EC2, RDS, and ElastiCache."
    )
    parser.add_argument(
        "--region",
        required=True,
        help="AWS region to scan, for example: us-east-1",
    )
    parser.add_argument(
        "--profile",
        help="Optional AWS profile name from your AWS credentials file.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.profile:
        boto3.setup_default_session(profile_name=args.profile)

    try:
        rows = []
        rows.extend(build_rows("EC2", get_ec2_resources(args.region)))
        rows.extend(build_rows("RDS", get_rds_resources(args.region)))
        rows.extend(build_rows("ElastiCache", get_elasticache_resources(args.region)))
        print_table(rows)
    except NoCredentialsError:
        print("ERROR: AWS credentials were not found.")
        print("Configure credentials using aws configure or pass --profile.")
    except (BotoCoreError, ClientError) as exc:
        print(f"ERROR: {exc}")


if __name__ == "__main__":
    main()
