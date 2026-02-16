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