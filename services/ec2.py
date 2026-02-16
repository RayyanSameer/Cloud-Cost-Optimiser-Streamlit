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