import streamlit as st
import pandas as pd
import boto3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- IMPORT SCANNERS ---
from services.ebs import scan_ebs
from services.elastic_ip import scan_eip
from services.snapshot import scan_snapshots
from services.rds import scan_rds
from services.nat_gateway import scan_nat
from services.s3 import scan_s3
from services.ec2 import scan_ec2
from services.eks import scan_eks
from services.vpc import scan_vpc

# Handle optional ALB scanner
try:
    from services.alb import scan_alb
except ImportError:
    scan_alb = None

# --- PAGE CONFIG ---
st.set_page_config(page_title="AWS Cost Optimizer", layout="wide", page_icon="")

st.title(" AWS Cost Optimizer")
st.markdown("""
**Stop wasting money.** This tool scans your AWS account in parallel to find idle resources instantly.
""")

# --- SIDEBAR ---
with st.sidebar:
    st.header(" Configuration")
    region = st.text_input("AWS Region", value="ap-south-1")
    
    if st.button(" Run Fast Scan"):
        st.session_state['scan_in_progress'] = True
    
    # Reset button
    if st.button(" Reset"):
        st.session_state['scan_in_progress'] = False
        st.rerun()

# --- MAIN LOGIC ---
if st.session_state.get('scan_in_progress', False):
    
    # 1. INITIALIZE CLIENTS (Fast)
    with st.spinner(f" Connecting to AWS ({region})..."):
        try:
            session = boto3.Session(region_name=region)
            ec2 = session.client('ec2')
            elb = session.client('elbv2')
            cw = session.client('cloudwatch')
            rds = session.client('rds')
            s3 = session.client('s3')
            eks = session.client('eks')
        except Exception as e:
            st.error(f"AWS Connection Error: {e}")
            st.stop()

    # 2. DEFINE SCANS
    scans = [
        ("EBS Volumes", scan_ebs, [ec2]),
        ("Elastic IPs", scan_eip, [ec2]),
        ("Snapshots", scan_snapshots, [ec2]),
        ("RDS Instances", scan_rds, [rds]),
        ("NAT Gateways", scan_nat, [ec2, cw]),
        ("S3 Buckets", scan_s3, [s3]),
        ("EC2 Instances", scan_ec2, [ec2, cw]),
        ("EKS Clusters", scan_eks, [eks]),
        ("VPCs", scan_vpc, [ec2])
    ]

    if scan_alb:
        scans.insert(2, ("Load Balancers", scan_alb, [elb, cw]))

    # 3. RUN PARALLEL SCANS
    results = {}
    total_savings = 0.0
    
    # UI Elements for Progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # The ThreadPool Engine
    with st.spinner("⚡ Scanning all services simultaneously..."):
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit all tasks to the pool
            future_to_name = {
                executor.submit(func, *args): name 
                for name, func, args in scans
            }
            
            completed_count = 0
            total_scans = len(scans)
            
            # Process as they finish (First Come, First Served)
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    data = future.result()
                    results[name] = data
                    
                    # Calculate savings immediately
                    for item in data:
                        total_savings += float(item.get("Cost", 0.0))
                        
                except Exception as e:
                    results[name] = []
                    st.toast(f" Error scanning {name}: {e}")
                
                # Update Progress
                completed_count += 1
                progress = int((completed_count / total_scans) * 100)
                progress_bar.progress(progress)
                status_text.text(f" Finished: {name}")

    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()

    # 4. DASHBOARD UI
    st.divider()
    
    # Top Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Monthly Waste", f"${total_savings:.2f}", delta="Potential Savings")
    c2.metric("Services Scanned", len(scans))
    c3.metric("Resources Flagged", sum(len(v) for v in results.values()))

    # Detailed Table
    st.subheader("🕵️ Detailed Findings")
    
    all_rows = []
    chart_data = []

    for service, items in results.items():
        service_total = 0.0
        for item in items:
            cost = float(item.get('Cost', 0.0))
            service_total += cost
            all_rows.append({
                "Service": service,
                "Resource ID": item.get('ID'),
                "Reason": item.get('Reason'),
                "Cost": cost  # Keep as number for sorting
            })
        
        if service_total > 0:
            chart_data.append({"Service": service, "Cost": service_total})

    if all_rows:
        df = pd.DataFrame(all_rows)
        # Format Cost column for display
        df['Cost ($)'] = df['Cost'].apply(lambda x: f"${x:.2f}")
        
        # Sort by most expensive
        df = df.sort_values(by="Cost", ascending=False)
        
        st.dataframe(
            df[["Service", "Resource ID", "Reason", "Cost ($)"]], 
            use_container_width=True,
            hide_index=True
        )

        # Bar Chart
        st.subheader(" Waste by Service")
        if chart_data:
            chart_df = pd.DataFrame(chart_data).set_index("Service")
            st.bar_chart(chart_df)
    else:
        st.balloons()
        st.success(" Your AWS account is squeaky clean! No waste found.")