import boto3
from datetime import datetime, timezone

class S3Scanner:
    def __init__(self, s3_client):
        self.s3 = s3_client

    def get_stale_buckets(self):
        try:
            response = self.s3.list_buckets()
            buckets = response['Buckets']
        except Exception as e:
            print(f"Error listing buckets: {e}")
            return []

        waste_list = []
        
        for bucket in buckets:
            b_name = bucket['Name']
            
            try:
                
                objects = self.s3.list_objects_v2(Bucket=b_name, MaxKeys=1000)
                
                total_size_bytes = 0
                last_modified = bucket['CreationDate'] # Default to creation date
                
                if 'Contents' in objects:
                    for obj in objects['Contents']:
                        total_size_bytes += obj['Size']
                  
                        if obj['LastModified'] > last_modified:
                            last_modified = obj['LastModified']
                
          
                total_size_gb = total_size_bytes / (1024 ** 3)
                
             # (Mumbai Standard: $0.023/GB)
                estimated_cost = total_size_gb * 0.023
                
               
                if estimated_cost < 0.01:
                    continue

                days_inactive = (datetime.now(timezone.utc) - last_modified).days
                
                if days_inactive > 90:
                    item = {
                        "ID": b_name,
                        "Reason": f"Stale ({days_inactive} days) - {total_size_gb:.4f} GB",
                        "Cost": estimated_cost
                    }
                    waste_list.append(item)

            except Exception as e:
            
                continue
                
        return waste_list

def scan_s3(s3_client):
    scanner = S3Scanner(s3_client)
    return scanner.get_stale_buckets()