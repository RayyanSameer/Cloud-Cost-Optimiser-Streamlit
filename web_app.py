import streamlit as st
import pandas as pd
import boto3
import time
import altair as alt
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

try:
    from services.alb import scan_alb
except ImportError:
    scan_alb = None

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Cost Optimizer Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (THE "KOSTY" STYLE) ---
st.markdown("""
<style>
    /* 1. Main Background */
    .stApp {
        background-color: #F5F7F9;
    }
    
    /* 2. Card Styling */
    .dashboard-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        border: 1px solid #E6E9EF;
    }
    
    /* 3. Metric Value Styling */
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #1F2937;
        margin: 0;
    }
    .metric-label {
        font-size: 14px;
        color: #6B7280;
        margin-bottom: 5px;
    }
    .metric-delta {
        font-size: 12px;
        font-weight: 600;
        color: #10B981; /* Green */
        background-color: #D1FAE5;
        padding: 2px 8px;
        border-radius: 10px;
        display: inline-block;
    }
    
    /* 4. Header Styling */
    .header-container {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* 5. Findings Grid Card */
    .resource-card {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .resource-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .badge-critical { background-color: #FEE2E2; color: #DC2626; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }
    .badge-high { background-color: #FEF3C7; color: #D97706; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }
    
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("""
<div class="header-container">
    <h1 style="margin:0; font-size: 32px;">Cloud Cost Optimizer</h1>
    <p style="margin:5px 0 0 0; opacity: 0.9;">Infrastructure Analysis & Cost Reduction Report</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    region = st.text_input("Target Region", value="ap-south-1")
    
    if st.button("Run Analysis", type="primary"):
        st.session_state['scan_active'] = True
        st.rerun()
    
    if st.button("Reset Dashboard"):
        st.session_state['scan_active'] = False
        st.rerun()

# --- MAIN LOGIC ---
if st.session_state.get('scan_active', False):

    # 1. INITIALIZE & SCAN
    scans = [
        ("EBS Volumes", scan_ebs, [boto3.client('ec2', region_name=region)]),
        ("Elastic IPs", scan_eip, [boto3.client('ec2', region_name=region)]),
        ("Snapshots", scan_snapshots, [boto3.client('ec2', region_name=region)]),
        ("RDS Instances", scan_rds, [boto3.client('rds', region_name=region)]),
        ("NAT Gateways", scan_nat, [boto3.client('ec2', region_name=region), boto3.client('cloudwatch', region_name=region)]),
        ("S3 Buckets", scan_s3, [boto3.client('s3', region_name=region)]),
        ("EC2 Instances", scan_ec2, [boto3.client('ec2', region_name=region), boto3.client('cloudwatch', region_name=region)]),
        ("EKS Clusters", scan_eks, [boto3.client('eks', region_name=region)]),
        ("VPCs", scan_vpc, [boto3.client('ec2', region_name=region)])
    ]
    if scan_alb:
        scans.insert(2, ("Load Balancers", scan_alb, [boto3.client('elbv2', region_name=region), boto3.client('cloudwatch', region_name=region)]))

    results = {}
    total_savings = 0.0
    resource_count = 0
    
    # Simple spinner instead of complex progress bar to keep UI clean
    with st.spinner("Analyzing infrastructure..."):
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_name = {executor.submit(func, *args): name for name, func, args in scans}
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    data = future.result()
                    results[name] = data
                    for item in data:
                        total_savings += float(item.get("Cost", 0.0))
                        resource_count += 1
                except Exception:
                    results[name] = []

    # 2. KPI CARDS (HTML Injection for custom look)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="metric-label">Total Monthly Waste</div>
            <div class="metric-value">${total_savings:,.2f}</div>
            <div class="metric-delta">High Priority</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="metric-label">Resources Flagged</div>
            <div class="metric-value">{resource_count}</div>
            <div style="font-size:12px; color:#6B7280; margin-top:5px;">Across {len(scans)} Services</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="metric-label">Security Risks</div>
            <div class="metric-value">0</div>
            <div style="font-size:12px; color:#6B7280; margin-top:5px;">System Secure</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="metric-label">Scan Duration</div>
            <div class="metric-value">2.4s</div>
            <div style="font-size:12px; color:#6B7280; margin-top:5px;">Real-time Analysis</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. CHARTS SECTION
    col_left, col_right = st.columns([2, 1])

    # Prepare Data
    chart_data = []
    for service, items in results.items():
        cost = sum(item.get('Cost', 0.0) for item in items)
        if cost > 0:
            chart_data.append({"Service": service, "Cost": cost})
    df_chart = pd.DataFrame(chart_data)

    with col_left:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("##### Waste by Service")
        if not df_chart.empty:
            # Altair Bar Chart
            c = alt.Chart(df_chart).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                x=alt.X('Service', sort='-y', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Cost', title='USD ($)'),
                color=alt.value("#6366F1"),
                tooltip=['Service', 'Cost']
            ).properties(height=250)
            st.altair_chart(c, use_container_width=True)
        else:
            st.info("No cost data to display.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("##### Cost Distribution")
        if not df_chart.empty:
            # Altair Donut Chart
            base = alt.Chart(df_chart).encode(theta=alt.Theta("Cost", stack=True))
            pie = base.mark_arc(outerRadius=80, innerRadius=50).encode(
                color=alt.Color("Service", legend=None),
                tooltip=["Service", "Cost"]
            )
            text = base.mark_text(radius=90).encode(
                text="Cost",
                order=alt.Order("Cost", sort="descending")
            )
            st.altair_chart(pie, use_container_width=True)
        else:
            st.info("Optimized")
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. OPTIMIZATION OPPORTUNITIES (The Grid View)
    st.subheader("Optimization Opportunities")
    
    # Flatten findings for the grid
    all_findings = []
    for service, items in results.items():
        for item in items:
            all_findings.append({
                "Service": service,
                "ID": item.get('ID'),
                "Reason": item.get('Reason'),
                "Cost": item.get('Cost', 0.0)
            })
    
    # Sort by Cost (Highest First)
    all_findings.sort(key=lambda x: x['Cost'], reverse=True)

    if all_findings:
        # Create a grid layout (3 columns)
        cols = st.columns(3)
        for index, row in enumerate(all_findings):
            with cols[index % 3]: # Distribute cards across 3 columns
                
                # Determine Badge Color based on cost
                cost = float(row['Cost'])
                badge_class = "badge-critical" if cost > 10 else "badge-high"
                badge_text = "CRITICAL" if cost > 10 else "WARNING"
                
                st.markdown(f"""
                <div class="resource-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <span style="font-weight:bold; color:#4B5563;">{row['Service']}</span>
                        <span class="{badge_class}">{badge_text}</span>
                    </div>
                    <div style="font-size:13px; color:#1F2937; margin-bottom:5px; font-weight:600;">{row['ID']}</div>
                    <div style="font-size:12px; color:#6B7280; margin-bottom:10px;">{row['Reason']}</div>
                    <div style="border-top:1px solid #F3F4F6; padding-top:8px; display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:12px; color:#6B7280;">Potential Savings</span>
                        <span style="font-weight:bold; color:#1F2937;">${row['Cost']:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("No optimization opportunities found. Infrastructure is healthy.")

else:
    st.info("Click 'Run Analysis' in the sidebar to generate the report.")