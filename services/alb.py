import boto3
from datetime import datetime, timedelta


class ALBScanner():
    def __init__(self, elb_client, cw_client):
        self.client = elb_client
        self.cw_client = cw_client

    def get_idle_albs(self):
        # 1. Fetch all ALBs
        response = self.client.describe_load_balancers()
        albs = response.get('LoadBalancers', [])
        idle_list = []

        for alb in albs:
            name = alb['LoadBalancerName']
            # Extracting the correct suffix for ALB metrics
            # Dimensions usually need the suffix part of the ARN
            alb_id = alb['LoadBalancerArn'].split('/')[-3:]
            dimension_value = f"{alb_id[0]}/{alb_id[1]}/{alb_id[2]}"

            # 2. Fetch metrics from CloudWatch
            metric_data = self.cw_client.get_metric_statistics(
                Namespace='AWS/ApplicationELB',
                MetricName='RequestCount',
                Dimensions=[{'Name': 'LoadBalancer', 'Value': dimension_value}],
                StartTime=datetime.utcnow() - timedelta(days=1), # Checking last 24h
                EndTime=datetime.utcnow(),
                Period=86400, # 24 hours
                Statistics=['Sum']
            )

            # 3. Check if it's a "Zombie"
            datapoints = metric_data.get('Datapoints', [])
            
            # If no traffic exists in 24 hours, it's idle
            if not datapoints or datapoints[0].get('Sum', 0) == 0:
                item = {
                    "ID": alb['LoadBalancerArn'].split('/')[-1],
                    "Name": name,
                    "Cost": 18.25
                }
                idle_list.append(item)

        return idle_list

def scan_alb(elb_client, cw_client):
    scanner = ALBScanner(elb_client, cw_client)
    return scanner.get_idle_albs()