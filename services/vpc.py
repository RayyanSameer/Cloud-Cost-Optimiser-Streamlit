import boto3

class VPCScanner:
    def __init__(self, ec2_client):
        self.ec2 = ec2_client

    def get_vpc_waste(self):
        waste_list = []
        
        # 1. SCAN FOR PUBLIC IPS (The Real Cost: $0.005/hr)
       
        try:
            
            response = self.ec2.describe_network_interfaces()
            
            for eni in response['NetworkInterfaces']:
                if 'Association' in eni and 'PublicIp' in eni['Association']:
                    public_ip = eni['Association']['PublicIp']
                    
                    
                    waste_list.append({
                        "ID": public_ip,
                        "Reason": "Public IPv4 ($0.005/hr) - Attached to " + eni.get('Attachment', {}).get('InstanceId', 'Unknown'),
                        "Cost": 3.60 
                    })
        except Exception as e:
            print(f"Error scanning IPs: {e}")

        # 2. SCAN FOR EMPTY VPCS 
        try:
            vpcs = self.ec2.describe_vpcs()['Vpcs']
            for vpc in vpcs:
                vpc_id = vpc['VpcId']
                
                
                enis = self.ec2.describe_network_interfaces(
                    Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
                )['NetworkInterfaces']
                
                if len(enis) == 0:
                    waste_list.append({
                        "ID": vpc_id,
                        "Reason": "Empty VPC (No Active Resources)",
                        "Cost": 0.00 
                    })
        except Exception:
            pass
            
        return waste_list

def scan_vpc(ec2_client):
    scanner = VPCScanner(ec2_client)
    return scanner.get_vpc_waste()