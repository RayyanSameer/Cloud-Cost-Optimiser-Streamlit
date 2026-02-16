import boto3
from dashboard import generate_dashboard

from services.vpc import scan_vpc
from services.ebs import scan_ebs
from services.elastic_ip import scan_eip
from services.alb import scan_alb
from services.snapshot import scan_snapshots
from services.rds import scan_rds
from services.nat_gateway import scan_nat
from services.s3 import scan_s3
from services.ec2 import scan_ec2
from services.eks import scan_eks

def main():
    region = 'ap-south-1'
    
    print(f"\n Connecting to AWS ({region})... This may take a moment...")

    try:
     
        
        ec2 = boto3.client('ec2', region_name=region)
        elb = boto3.client('elbv2', region_name=region)
        cw = boto3.client('cloudwatch', region_name=region)
        rds = boto3.client('rds', region_name=region)
        s3 = boto3.client('s3', region_name=region)
        s3 = boto3.client('s3', region_name=region)
        eks = boto3.client('eks', region_name=region)

    
        print("   ... Scanning EBS Volumes")
        ebs_data = scan_ebs(ec2)
        
        print("   ... Scanning Elastic IPs")
        eip_data = scan_eip(ec2)
        
        print("   ... Scanning Load Balancers")
        alb_data = scan_alb(elb, cw)
        
        print("   ... Scanning NAT Gateways")
        nat_data = scan_nat(ec2, cw)
        
        print("   ... Scanning Snapshots")
        snap_data = scan_snapshots(ec2)
        
        print("   ... Scanning RDS")
        rds_data = scan_rds(rds)
        
        print("   ... Scanning S3")
        s3_data = scan_s3(s3)
        
        print("   ... Scanning EC2 ")
        ec2_data = scan_ec2(ec2, cw)

        print("   ... Scanning EKS Clusters") 
        eks_data = scan_eks(eks)

        print("   ... Scanning VPCs & Public IPs")
        vpc_data = scan_vpc(ec2)

      
        cloud_data = {
            'EBS Volumes': ebs_data,
            'Elastic IPs': eip_data,
            'Load Balancers': alb_data,
            'NAT Gateways': nat_data,
            'Snapshots': snap_data,
            'RDS Instances': rds_data,
            'S3 Buckets': s3_data,
            'EC2 Instances': ec2_data,
            'EKS Clusters' :eks_data,
            'VPC & Public IPs': vpc_data
        }

    
        generate_dashboard(cloud_data)

    except Exception as e:
        print(f"\n CRITICAL ERROR IN MAIN: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()