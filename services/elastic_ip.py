import boto3 

class elastic_ip_scanner(): #Class to scan for unattached elastic IPs
    def __init__(self,client):
        self.client = client
    

    def get_elastic_ip(self): #Get the list of elastic IPs
        list_of_eips = self.client.describe_addresses()['Addresses']

        clean_list = []

        for eip in list_of_eips: #Loop through the list of elastic IPs
            if 'AssociationId' not in eip: 
                item = { 
                    "ID": eip['AllocationId'], 
                    "Public IP": eip['Public Ip'], 
                    "Cost": 3.6
                }
            

            clean_list.append(item) #Append the item to the clean list
        return clean_list #Return the clean list of elastic IPs
        
def scan_eip(ec2_client): #Function to scan for unattached elastic IPs
    eip_instance = elastic_ip_scanner(ec2_client)
    return eip_instance.get_elastic_ip()
