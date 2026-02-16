
import os

# 1. DEFINE THE NEW PRICING FILE
pricing_code = """
# Real pricing for ap-south-1 (Mumbai) - Updated Feb 2026
# Assumes 730 hours/month

PRICING = {
    # EC2 (Linux On-Demand)
    't2.micro': 8.61,
    't2.small': 17.23,
    't2.medium': 34.46,
    't3.micro': 7.59,
    't3.small': 15.18,
    't3.medium': 30.37,
    'm5.large': 70.81,
    'c5.large': 62.05,
    
    # STORAGE (Per GB)
    'gp2': 0.10,
    'gp3': 0.08,
    
    # NETWORK / OTHER
    'nat_gateway': 33.58,
    'elastic_ip': 3.65,
    'alb': 16.42
}

def get_ec2_price(instance_type):
    return PRICING.get(instance_type, 50.00) # Default estimate

def get_ebs_price(size, vol_type):
    rate = PRICING.get(vol_type, 0.10)
    return float(size) * rate
"""

# 2. DEFINE THE UPDATED SCANNERS
ec2_code = """
import boto3
from datetime import datetime, timedelta
from services.pricing import get_ec2_price

class EC2Scanner:
    def __init__(self, ec2_client, cw_client):
        self.ec2 = ec2_client
        self.cw = cw_client

    def get_ec2_waste(self):
        response = self.ec2.describe_instances()
        waste_list = []

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                
                instance_id = instance['InstanceId']
                state = instance['State']['Name']
                inst_type = instance['InstanceType']
                
                # CASE 1: Stopped Instance (Paying for EBS only usually, but let's flag it)
                if state == 'stopped':
                    item = {
                        "ID": instance_id,
                        "Reason": "Stopped Instance",
                        "Cost": 2.00 # Nominal EBS cost estimate
                    }
                    waste_list.append(item)
                    continue

                # CASE 2: Zombie Instance (Running but Idle)
                if state == 'running':
                    try:
                        metric = self.cw.get_metric_statistics(
                            Namespace='AWS/EC2',
                            MetricName='CPUUtilization',
                            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                            StartTime=datetime.utcnow() - timedelta(days=7),
                            EndTime=datetime.utcnow(),
                            Period=86400,
                            Statistics=['Average']
                        )
                        
                        datapoints = metric.get('Datapoints', [])
                        if datapoints:
                            avg_cpu = datapoints[0]['Average']
                            if avg_cpu < 1.0:
                                real_cost = get_ec2_price(inst_type)
                                item = {
                                    "ID": instance_id,
                                    "Reason": f"Zombie {inst_type} (CPU {avg_cpu:.1f}%)",
                                    "Cost": real_cost
                                }
                                waste_list.append(item)
                    except Exception as e:
                        print(f"Error checking EC2 {instance_id}: {e}")
                        continue
        
        return waste_list

def scan_ec2(ec2_client, cw_client):
    scanner = EC2Scanner(ec2_client, cw_client)
    return scanner.get_ec2_waste()
"""

ebs_code = """
import boto3
from services.pricing import get_ebs_price

class EBSScanner:
    def __init__(self, ec2_client):
        self.ec2 = ec2_client

    def get_orphan_volumes(self):
        response = self.ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
        orphans = []

        for vol in response['Volumes']:
            v_id = vol['VolumeId']
            size = vol['Size']
            v_type = vol['VolumeType']
            
            real_cost = get_ebs_price(size, v_type)

            orphans.append({
                "ID": v_id,
                "Reason": "Unattached Volume",
                "Size": size,
                "Cost": real_cost
            })
        
        return orphans

def scan_ebs(ec2_client):
    scanner = EBSScanner(ec2_client)
    return scanner.get_orphan_volumes()
"""

nat_code = """
import boto3
from datetime import datetime, timedelta
from services.pricing import PRICING

class NATScanner:
    def __init__(self, ec2_client, cw_client):
        self.ec2 = ec2_client
        self.cw = cw_client

    def get_idle_nats(self):
        response = self.ec2.describe_nat_gateways()
        idle_list = []

        for nat in response.get('NatGateways', []):
            nat_id = nat['NatGatewayId']
            if nat['State'] != 'available':
                continue
            
            try:
                metric_data = self.cw.get_metric_statistics(
                    Namespace='AWS/NATGateway',
                    MetricName='ConnectionEstablishedCount',
                    Dimensions=[{'Name': 'NatGatewayId', 'Value': nat_id}],
                    StartTime=datetime.utcnow() - timedelta(days=1),
                    EndTime=datetime.utcnow(),
                    Period=86400,
                    Statistics=['Sum']
                )

                datapoints = metric_data.get("Datapoints", [])

                if not datapoints or datapoints[0].get('Sum', 0) == 0:
                    item = {
                        "ID": nat_id,
                        "Reason": "Idle NAT Gateway",
                        "Cost": PRICING['nat_gateway']
                    }
                    idle_list.append(item)
            except Exception as e:
                continue
        
        return idle_list

def scan_nat(ec2_client, cw_client): 
    scanner = NATScanner(ec2_client, cw_client)
    return scanner.get_idle_nats()
"""

# 3. WRITE THE FILES
files_to_update = {
    "services/pricing.py": pricing_code,
    "services/ec2.py": ec2_code,
    "services/ebs.py": ebs_code,
    "services/nat_gateway.py": nat_code
}

print("🚀 Starting Automatic Update...")
for filepath, content in files_to_update.items():
    try:
        with open(filepath, "w") as f:
            f.write(content.strip())
        print(f" Updated: {filepath}")
    except Exception as e:
        print(f" Failed to update {filepath}: {e}")
