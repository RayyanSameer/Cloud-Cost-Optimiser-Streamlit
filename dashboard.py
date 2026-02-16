from tabulate import tabulate
from colorama import Fore, Style, init

init()

def generate_dashboard(cloud_data):
    print(Style.BRIGHT + Fore.CYAN + "\n" + "="*60)
    print("     AWS COST OPTIMIZER REPORT   ")
    print("="*60 + Style.RESET_ALL)
    
    grand_total = 0.0
    summary_data = []
    all_details = []

    for service, resources in cloud_data.items():
        service_total = 0.0
        count = len(resources)
        
        for item in resources:
            cost = item.get('Cost', 0.0)
            service_total += cost
            grand_total += cost
            all_details.append([service, item.get('ID', 'N/A'), item.get('Reason', 'Unused'), f"${cost:.2f}"])
            
        if count > 0:
            summary_data.append([service, count, f"${service_total:.2f}"])

    print(Fore.YELLOW + "\n  SUMMARY" + Style.RESET_ALL)
    if summary_data:
        print(tabulate(summary_data, headers=["Service", "Count", "Monthly Waste"], tablefmt="fancy_grid"))
    else:
        print(Fore.GREEN + "  No waste found." + Style.RESET_ALL)

    if all_details:
        print(Fore.YELLOW + "\n DETAILED FINDINGS" + Style.RESET_ALL)
        all_details.sort(key=lambda x: float(x[3].replace('$', '')), reverse=True)
        print(tabulate(all_details, headers=["Service", "Resource ID", "Reason", "Est. Cost"], tablefmt="simple"))

    print(Style.BRIGHT + "\n" + "-"*60)
    print(f" TOTAL POTENTIAL SAVINGS: ${grand_total:.2f} / month")
    print("-"*60 + "\n")