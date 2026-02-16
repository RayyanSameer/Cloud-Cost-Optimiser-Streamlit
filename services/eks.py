import boto3

class EKSScanner:
    def __init__(self, eks_client):
        self.eks = eks_client

    def get_clusters(self):
        waste = []
        
        try:
            
            response = self.eks.list_clusters()
            
            
            clusters = response.get('clusters', [])
            
           
            for cluster in clusters:
                waste.append({
                    "ID": cluster,
                    "Reason": "EKS Control Plane (Active)",
                    "Cost": 72.00  # $0.10/hr * 720 hours
                })
                
        except Exception as e:
            print(f"  Error scanning EKS: {e}")
            return []

        return waste

def scan_eks(eks_client):
    scanner = EKSScanner(eks_client)
    return scanner.get_clusters()