import boto3
import re
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError, NoRegionError
from tabulate import tabulate
from datetime import datetime, timedelta
import time
from pathlib import Path

DEFAULT_REGION = 'us-east-1'

def ascii():
    print(f"\n _       __        __         __               ")
    print("| |     / /____ _ / /_ _____ / /_   ___   _____")
    print("| | /| / // __ `// __// ___// __ \\ / _ \\ / ___/")
    print("| |/ |/ // /_/ // /_ / /__ / / / //  __// /    ")
    print("|__/|__/ \\__,_/ \\__/ \\___//_/ /_/ \\___//_/     ")
    print(f"                                               \n")

def load_patterns(file_path='patterns.json'):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['patterns']

def check_aws_credentials():
    sts_client = boto3.client('sts', region_name=DEFAULT_REGION)
    try:
        sts_client.get_caller_identity()
        print("[✓] AWS Credentials: Valid")
    except NoCredentialsError:
        print("[X] AWS Credentials: Not found")
        return False
    except PartialCredentialsError:
        print("[X] AWS Credentials: Incomplete")
        return False
    except ClientError as e:
        if "ExpiredToken" in str(e):
            print("[X] AWS Credentials: Expired")
        else:
            print(f"[X] AWS Credentials: Error - {str(e)}")
        return False
    except NoRegionError:
        print("[X] AWS Region: Not specified")
        return False
    return True

def check_permissions():
    try:
        logs_client = boto3.client('logs', region_name=DEFAULT_REGION)
        logs_client.describe_log_groups(limit=1)
        print(f"[✓] CloudWatch Permissions: OK\n")
    except ClientError as e:
        if 'AccessDeniedException' in str(e):
            print("CloudWatch Permissions: Access Denied")
        return False
    return True

def list_log_groups_and_streams():
    regions = boto3.session.Session().get_available_regions('logs')

    all_log_groups_streams = []
    
    for region in regions:
        logs_client = boto3.client('logs', region_name=region)
        try:
            log_groups = logs_client.describe_log_groups()['logGroups']
            
            if log_groups:
                for log_group in log_groups:
                    log_group_name = log_group['logGroupName']
                    streams = logs_client.describe_log_streams(logGroupName=log_group_name)['logStreams']
                    
                    for stream in streams:
                        log_stream_name = stream['logStreamName']
                        all_log_groups_streams.append([region, log_group_name, log_stream_name])
        
        except ClientError:
            continue

    if all_log_groups_streams:
        print("[✓] Logs found:\n")
        print(tabulate(all_log_groups_streams, headers=["Region", "Log Group", "Log Stream"], tablefmt="grid"))
    else:
        print("[X] No log groups or streams found in any region")
    
    return all_log_groups_streams

def search_secrets_in_logs(log_groups_streams, patterns):
    
    time_source = int((datetime.utcnow() - timedelta(hours=1)).timestamp() * 1000)
    current_time = datetime.utcnow().timestamp() * 1000

    print(f"\n[✓] Searching logs from {datetime.utcfromtimestamp(time_source / 1000):%Y-%m-%d %H:%M:%S} to {datetime.utcfromtimestamp(current_time / 1000):%Y-%m-%d %H:%M:%S}")

    found_any_secrets = False

    for region, log_group, log_stream in log_groups_streams:
        logs_client = boto3.client('logs', region_name=region)
        
        try:
            events = logs_client.get_log_events(logGroupName=log_group, logStreamName=log_stream, startTime=time_source)
            for event in events['events']:
                message = event['message']

                for pattern in patterns:
                    matches = re.finditer(pattern['regexx'], message)
                    for match in matches:
                        found_any_secrets = True
                        secret = match.group(0)
                        print(f"\nPotential secret found in {log_group}/{log_stream} (Region: {region}):")
                        print(f"  - Rule Name: {pattern['name']}")
                        print(f"  - Description: {pattern['description']}")
                        print(f"  - Matched Secret: {secret}")
        
        except ClientError:
            continue
    
    if not found_any_secrets:
        print(f"\n[X] No secrets found in logs")
        return

def main():

    ascii()

    file_check = Path('patterns.json')
    if file_check.is_file():
        patterns = load_patterns()
    else:
        print("[X] Patterns not found")
        return

    if not check_aws_credentials():
        return

    if not check_permissions():
        return

    log_groups_streams = list_log_groups_and_streams()

    if log_groups_streams:
        search_secrets_in_logs(log_groups_streams, patterns)

if __name__ == "__main__":
    main()
