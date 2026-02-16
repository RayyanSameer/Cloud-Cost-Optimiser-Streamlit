# ☁️ AWS Cloud Cost Optimizer

**Stop burning money on invisible AWS resources.**

A Python CLI tool that scans your AWS account for idle, unused, and "zombie" resources. Calculates potential monthly savings using real-world pricing (focused on `ap-south-1`) and generates a detailed terminal dashboard.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![AWS](https://img.shields.io/badge/AWS-Boto3-orange?style=for-the-badge&logo=amazon-aws)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ⚡ Quick Start
```bash
# Clone and run in 60 seconds
git clone https://github.com/RayyanSameer/aws-cost-optimizer.git
cd aws-cost-optimizer
pip install -r requirements.txt
aws configure  # Enter your AWS credentials
python3 main.py
```

> **First-time user?** See [detailed setup](#%EF%B8%8F-installation--setup) below.

---

## 🚀 Key Features

Unlike AWS Trusted Advisor (which requires a support plan for full checks), this tool performs deep scans for specific "money pits":

| Resource Scanner | What it detects | Why it matters |
|:-----------------|:----------------|:---------------|
| **EKS Clusters** | Idle Control Planes | Saves **$72.00/month** per idle cluster |
| **VPC & Public IPs** | Unattached Public IPs | Saves **$3.60/month** per IP (AWS started charging Feb 2024) |
| **EBS Volumes** | Unattached/Orphaned Volumes | Detects leftover storage from deleted instances |
| **Snapshots** | Stale Snapshots (>90 days) | Cleans up backup clutter |
| **EC2 Instances** | Zombie instances (<1% CPU) | Identifies servers doing nothing |
| **S3 Buckets** | Stale/Empty Buckets | Finds storage unused for months |
| **NAT Gateways** | Idle Gateways | Saves **$33.00/month** on zero-traffic gateways |

---

## 🛠️ Installation & Setup

### Prerequisites

* **Python 3.8+** installed
* **AWS Account** with IAM permissions:
  - `ec2:Describe*`
  - `s3:ListAllMyBuckets`
  - `eks:DescribeCluster`
  - `cloudwatch:GetMetricStatistics`
  - *(Full policy in `iam_policy.json`)*
* **AWS CLI** configured

### 1. Clone the Repository
```bash
git clone https://github.com/RayyanSameer/aws-cost-optimizer.git
cd aws-cost-optimizer
```

### 2. Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure AWS Credentials
```bash
aws configure
# Enter Access Key, Secret Key, and Region (e.g., ap-south-1)
```

---

## 💻 Usage
```bash
python3 main.py
```

### Sample Output
```
============================================================
     ☁️   AWS COST OPTIMIZER REPORT   ☁️
============================================================

📊 EXECUTIVE SUMMARY
╒════════════╤═════════╤═════════════════╕
│ Service    │   Count │ Monthly Waste   │
╞════════════╪═════════╪═════════════════╡
│ EBS Volumes│       2 │ $2.40           │
│ Public IPs │       3 │ $10.80          │
╘════════════╧═════════╧═════════════════╛

🕵️ DETAILED FINDINGS
Service      Resource ID          Reason                        Est. Cost
----------   -------------------  ----------------------------  -----------
Public IPs   13.234.57.200        Public IPv4 ($0.005/hr)       $3.60
EBS Volumes  vol-0abc12345        Unattached Volume (20GB)      $2.00

------------------------------------------------------------
💰 TOTAL POTENTIAL SAVINGS: $13.20 / month
------------------------------------------------------------
```

---

## 📂 Project Structure
```
cost-optimizer/
├── main.py                 # Controller - Orchestrates scans
├── dashboard.py            # View - Terminal UI generation
├── services/               # Modular service scanners
│   ├── ec2.py              # EC2 instances
│   ├── ebs.py              # EBS volumes
│   ├── s3.py               # S3 buckets (size + age)
│   ├── eks.py              # EKS clusters
│   ├── vpc.py              # Public IPs & VPCs
│   ├── pricing.py          # Centralized pricing (Mumbai region)
│   └── ...
├── requirements.txt
├── iam_policy.json         # Minimal IAM permissions required
└── README.md
```

---

## ⚙️ Customization

### Change Region Pricing

To use a different region (e.g., `us-east-1`), update `services/pricing.py`:
```python
# services/pricing.py
PRICING = {
    't2.micro': 8.61,    # USD/month for ap-south-1
    'gp3': 0.08,         # USD/GB/month
    # Update these values for your region
}
```

---

## 💡 Why I Built This

After leaving EC2 instances running for "just testing," I watched my AWS bill hit **$87** in one month. AWS Trusted Advisor didn't flag most issues (limited on free tier), so I built this to:

- **Learn Boto3** and AWS SDK patterns
- **Solve a real problem** (saved $500+ annually)
- **Practice modular Python** (each scanner is independent)

This project taught me to think like a **cloud cost engineer**, not just a developer who uses AWS.

---

## 🚧 Roadmap

- [ ] **Web Dashboard** (React + Recharts) - *In Progress*
- [ ] **Auto-remediation** (`--fix` flag) - *v2.0 planned*
- [ ] **Multi-region scanning** - *Q2 2026*
- [ ] **Slack/Email notifications** - *Community requested*
- [ ] **Historical cost tracking** (SQLite storage)

---

## 🤝 Contributing

Contributions welcome! Please open an issue before submitting a PR.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-scanner`)
3. Commit changes (`git commit -m 'Add NAT Gateway scanner'`)
4. Push to branch (`git push origin feature/amazing-scanner`)
5. Open a Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 📧 Contact

**Rayyan Sameer**  
[GitHub](https://github.com/RayyanSameer) • 

> **Built with ☕ and frustration over AWS bills**