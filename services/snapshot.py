import boto3
from datetime import datetime, timedelta, timezone

class SnapshotScanner:
    def __init__(self, ec2_client):
        self.ec2 = ec2_client

    def get_orphaned_snapshots(self):
       
        try:
            snapshots = self.ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
        except Exception as e:
            print(f"Error describing snapshots: {e}")
            return []
        

        try:
            volumes = self.ec2.describe_volumes()['Volumes']
            active_vols = [v['VolumeId'] for v in volumes]
        except Exception:
            active_vols = []
        
        trash_list = []
        threshold_date = datetime.now(timezone.utc) - timedelta(days=30)

        for snap in snapshots:
            vol_id = snap.get('VolumeId')
            start_time = snap['StartTime']

       
            if vol_id not in active_vols and start_time < threshold_date:
                item = {
                    "ID": snap['SnapshotId'],
                    "Reason": "Orphaned (>30 days old)",
                    "Cost": snap['VolumeSize'] * 0.05 # Approx $0.05/GB
                }
                trash_list.append(item)
        
        return trash_list

def scan_snapshots(ec2_client):
    scanner = SnapshotScanner(ec2_client)
    return scanner.get_orphaned_snapshots()