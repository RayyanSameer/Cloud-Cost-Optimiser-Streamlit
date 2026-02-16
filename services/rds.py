import boto3

class rds_scanner():
    def __init__(self,client):
        self.client = client


        #Get the list of RDS instances
    def get_rds(self):
        list_of_rds = self.client.describe_db_instances()['DBInstances']

        clean_list = []

        for rds in list_of_rds:
            if rds['DBInstanceStatus'] == 'available':
                item = {
                    "ID": rds['DBInstanceIdentifier'],
                    "Engine": rds['Engine'],
                    "Cost": 15.0
                }
                clean_list.append(item)
        return clean_list
    
    #Function to scan for RDS instances
def scan_rds(rds_client):
    rds_instance = rds_scanner(rds_client)
    return rds_instance.get_rds()



