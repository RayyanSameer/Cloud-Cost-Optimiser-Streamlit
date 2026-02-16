import boto3
from moto import mock_aws
from services.nat_gateway import scan_nat
from services.snapshot import scan_snapshots
from services.eks import scan_eks

@mock_aws
def test_my_tool():
    print(" STARTING SIMULATION...")
    
    # 1. SETUP: Create fake AWS clients
    ec2 = boto3.client('ec2', region_name='ap-south-1')
    eks = boto3.client('eks', region_name='ap-south-1')
    cw = boto3.client('cloudwatch', region_name='ap-south-1')

    # 2. CREATE DUMMY RESOURCES (The "Waste")
    print("   ... Creating an idle NAT Gateway ($33/mo waste)")
    vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')['Vpc']['VpcId']
    subnet = ec2.create_subnet(VpcId=vpc, CidrBlock='10.0.1.0/24')['Subnet']['SubnetId']
    nat = ec2.create_nat_gateway(SubnetId=subnet)['NatGateway']
    
    print("   ... Creating an old Snapshot ($0.05/mo waste)")
    vol = ec2.create_volume(AvailabilityZone='ap-south-1a', Size=10)['VolumeId']
    snap = ec2.create_snapshot(VolumeId=vol, Description='Test Snap')['SnapshotId']
    ec2.delete_volume(VolumeId=vol) # Delete volume 

    print("   ... Creating an idle EKS Cluster ($72/mo waste)")
    eks.create_cluster(name='Unused-Cluster', roleArn='arn:aws:iam::123456789012:role/TestingRole', resourcesVpcConfig={})

    # 3. RUN  SCANNERS
    print("\n RUNNING YOUR TOOL...")
    nat_waste = scan_nat(ec2, cw)
    snap_waste = scan_snapshots(ec2)
    eks_waste = scan_eks(eks)

    # 4. VERIFY RESULTS
    print("\n RESULTS:")
    if len(nat_waste) > 0: print(f" PASSED: Found NAT Gateway ({nat_waste[0]['Cost']})")
    else: print(" FAILED: Missed NAT Gateway")

    if len(snap_waste) > 0: print(f" PASSED: Found Snapshot ({snap_waste[0]['Cost']})")
    else: print(" FAILED: Missed Snapshot")

    if len(eks_waste) > 0: print(f" PASSED: Found EKS Cluster ({eks_waste[0]['Cost']})")
    else: print(" FAILED: Missed EKS Cluster")

if __name__ == "__main__":
    test_my_tool()