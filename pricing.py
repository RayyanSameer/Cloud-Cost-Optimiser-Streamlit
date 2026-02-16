# Real pricing for ap-south-1 (Mumbai) as of Feb 2026

# COST PER MONTH 
PRICING = {
    # 1. EC2 INSTANCES (Linux, On-Demand)
    't2.micro': 8.61,    
    't2.small': 17.23,
    't2.medium': 34.46,
    't3.micro': 7.59,
    't3.small': 15.18,
    't3.medium': 30.37,
    'm5.large': 70.81,
    'c5.large': 62.05,
    
    # 2. STORAGE (Per GB per Month)
    'gp2': 0.10,         # $0.10 per GB
    'gp3': 0.08,         # $0.08 per GB
    'standard': 0.05,    
    
    # 3. NETWORK
    'nat_gateway': 33.58, # $0.046/hr * 730
    'elastic_ip': 3.65,   # $0.005/hr
    'alb': 16.42          # $0.0225/hr
}

def get_ec2_price(instance_type):
    """Returns the monthly cost of an instance type."""
    return PRICING.get(instance_type, 50.00)

def get_ebs_price(size_gb, volume_type='gp2'):
    """Returns the monthly cost of a volume."""
    rate = PRICING.get(volume_type, 0.10)
    return size_gb * rate