# Real pricing for ap-south-1 (Mumbai) - Updated Feb 2026
# Assumes 730 hours/month

PRICING = {
    # EC2 (Linux On-Demand)
    't2.micro': 8.61,
    't2.small': 17.23,
    't2.medium': 34.46,
    't3.micro': 7.59,
    't3.small': 15.18,
    't3.medium': 30.37,
    'm5.large': 70.81,
    'c5.large': 62.05,
    
    # STORAGE (Per GB)
    'gp2': 0.10,
    'gp3': 0.08,
    
    # NETWORK / OTHER
    'nat_gateway': 33.58,
    'elastic_ip': 3.65,
    'alb': 16.42
}

def get_ec2_price(instance_type):
    return PRICING.get(instance_type, 50.00) # Default estimate

def get_ebs_price(size, vol_type):
    rate = PRICING.get(vol_type, 0.10)
    return float(size) * rate