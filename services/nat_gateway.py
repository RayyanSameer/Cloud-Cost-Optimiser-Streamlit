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