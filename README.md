# AWS Resource Count Script

This script fetches AWS resources from EC2, RDS, and ElastiCache, groups them by type, and prints the count with resource names in a readable table.

## Services Covered

- EC2 running instances
- RDS available DB instances
- ElastiCache available cache clusters

## Clone and Setup

Clone the repo and enter the folder:

```powershell
git clone https://github.com/ops-tanmayr/aws-resource-count.git
cd aws-resource-count
```

Use Python 3.10 or later.

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure AWS credentials:

```powershell
aws configure
```

Or use an existing AWS profile.

You can also set credentials only for the current PowerShell session:

```powershell
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_DEFAULT_REGION="region"
```

Do not add AWS keys directly inside the Python script or commit them to GitHub.

## Run

Run with a region:

```powershell
python aws_resource_count.py --region <region>
```

```

## Example Output

```text
+--------------+-------+-----------------+----------------------------+
| Service      | Count | Type            | Resource Names             |
+--------------+-------+-----------------+----------------------------+
| EC2          | 4     | c5.large        | app-server-1, app-server-2 |
| EC2          | 2     | t3.medium       | web-server-1, web-server-2 |
| RDS          | 2     | db.m5.large     | prod-db, reporting-db      |
| RDS          | 1     | db.t3.micro     | dev-db                     |
| ElastiCache | 3     | cache.m6g.large | prod-cache (3 nodes)       |
| ElastiCache | 1     | cache.t3.micro  | dev-cache                  |
+--------------+-------+-----------------+----------------------------+
```

## Required AWS Permissions

The AWS user or role needs read-only permissions for:

- `ec2:DescribeInstances`
- `rds:DescribeDBInstances`
- `elasticache:DescribeCacheClusters`
