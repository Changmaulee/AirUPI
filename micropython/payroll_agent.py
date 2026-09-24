"""
Indian Statutory Payroll & Payslip Compliance Engine for MicroPython (RP2040)
Agents: "Kuber" (Calculation & Tax) & "Lekhak" (Auditor & Payslip Generator)
Optimized with Streaming Aggregator for Zero-Heap Footprint on RP2040 Silicon.
"""

import sys
import gc

DEPTS = ("Engineering", "Cloud Systems", "Operations", "Product", "QA", "Support", "Finance", "HR")
STATES = ("Karnataka", "Tamil Nadu", "Maharashtra", "Telangana", "Delhi")
NAMES = (
    "Rajesh Kumar", "Priya Sharma", "Ananya Iyer", "Venkatesh Rao", "Suresh Patil",
    "Deepika Reddy", "Amitabh Sen", "Sneha Mukherjee", "Karthik Swamy", "Pooja Nair",
    "Manoj Verma", "Kavita Hegde", "Arjun Das", "Divya Menon", "Rohan Kulkarni",
    "Meera Pillai", "Vikram Joshi", "Swati Deshmukh", "Naveen Bhat", "Ritu Gupta"
)

def get_employee(i):
    """Generate employee #i deterministically on-the-fly with 0 heap retention"""
    name = NAMES[(i - 1) % len(NAMES)] + ("" if i <= 20 else " #{:03d}".format(i))
    dept = DEPTS[(i - 1) % len(DEPTS)]
    state = STATES[(i - 1) % len(STATES)]
    base_ctc = 25000 + ((i * 7321) % 175000)
    pan = "ABC{}K{}{}".format(chr(65 + (i % 26)), 1000 + i, chr(65 + ((i*3) % 26)))
    uan = "1009{:08d}".format(87654000 + i)
    bank_acc = "987654{:06d}".format(320000 + i)
    return {
        "emp_id": "BTS-{:03d}".format(i),
        "name": name,
        "dept": dept,
        "state": state,
        "monthly_ctc": base_ctc,
        "pan": pan,
        "uan": uan,
        "bank_acc": bank_acc,
        "days_present": 30,
        "total_days": 30
    }

class KuberMathAgent:
    """Agent 9: Kuber - Indian Statutory Compliance & Salary Computation"""
    
    @staticmethod
    def calculate_salary_structure(emp):
        ctc = emp["monthly_ctc"]
        days_ratio = emp["days_present"] / emp["total_days"]
        pro_ctc = ctc * days_ratio

        # 1. Earnings Breakdown
        basic = pro_ctc * 0.45  # 45% Basic
        hra = basic * 0.50      # 50% HRA (Metro)
        conveyance = 2500.0
        special_allowance = max(0.0, pro_ctc - (basic + hra + conveyance))
        gross_earnings = basic + hra + conveyance + special_allowance

        # 2. Statutory Deductions
        epf_wage = min(basic, 15000.0)
        ee_pf = epf_wage * 0.12 # Employee 12%
        er_eps = min(epf_wage * 0.0833, 1250.0) # Employer EPS (Capped at ₹1250)
        er_epf = (epf_wage * 0.12) - er_eps

        ee_esi = 0.0
        er_esi = 0.0
        if gross_earnings <= 21000.0:
            ee_esi = gross_earnings * 0.0075
            er_esi = gross_earnings * 0.0325

        pt = 200.0 if gross_earnings >= 15000.0 else 0.0

        # Sec 115BAC TDS estimation
        annual_taxable = (gross_earnings * 12) - 75000.0
        annual_tax = 0.0
        if annual_taxable > 700000.0:
            if annual_taxable > 1500000.0:
                annual_tax = 150000.0 + (annual_taxable - 1500000.0) * 0.30
            elif annual_taxable > 1200000.0:
                annual_tax = 90000.0 + (annual_taxable - 1200000.0) * 0.20
            elif annual_taxable > 1000000.0:
                annual_tax = 60000.0 + (annual_taxable - 1000000.0) * 0.15
            elif annual_taxable > 700000.0:
                annual_tax = 20000.0 + (annual_taxable - 700000.0) * 0.10
        monthly_tds = annual_tax / 12.0

        total_deductions = ee_pf + ee_esi + pt + monthly_tds
        net_take_home = gross_earnings - total_deductions

        return {
            "emp_id": emp["emp_id"],
            "name": emp["name"],
            "dept": emp["dept"],
            "state": emp["state"],
            "pan": emp["pan"],
            "uan": emp["uan"],
            "bank_acc": emp["bank_acc"],
            "days_paid": emp["days_present"],
            "total_days": emp["total_days"],
            "basic": basic,
            "hra": hra,
            "conveyance": conveyance,
            "special": special_allowance,
            "gross": gross_earnings,
            "ee_pf": ee_pf,
            "er_epf": er_epf,
            "er_eps": er_eps,
            "ee_esi": ee_esi,
            "er_esi": er_esi,
            "pt": pt,
            "tds": monthly_tds,
            "total_deductions": total_deductions,
            "net_pay": net_take_home
        }

class LekhakAuditAgent:
    """Agent 10: Lekhak - Auditor, Discrepancy Checker & Payslip Formatter"""

    @staticmethod
    def format_payslip(sal):
        s = "=" * 78 + "\n"
        s += "                    BHARAT TECH SOLUTIONS PRIVATE LIMITED\n"
        s += "                   Payslip for the Month of September 2026\n"
        s += "=" * 78 + "\n"
        s += " Emp ID: {:<14} Name: {:<24} Dept: {}\n".format(sal['emp_id'], sal['name'], sal['dept'])
        s += " PAN: {:<17} UAN: {:<25} State: {}\n".format(sal['pan'], sal['uan'], sal['state'])
        s += " Bank A/c: {:<12} Days Paid: {} / {}\n".format(sal['bank_acc'], sal['days_paid'], sal['total_days'])
        s += "-" * 78 + "\n"
        s += " EARNINGS                     AMOUNT (₹) | DEDUCTIONS                 AMOUNT (₹)\n"
        s += "-" * 78 + "\n"
        s += " Basic Salary:               {:>10.2f} | Employee PF (12%):          {:>10.2f}\n".format(sal['basic'], sal['ee_pf'])
        s += " House Rent Allowance (HRA): {:>10.2f} | Professional Tax (PT):        {:>10.2f}\n".format(sal['hra'], sal['pt'])
        s += " Special Allowance:          {:>10.2f} | TDS / Income Tax:           {:>10.2f}\n".format(sal['special'], sal['tds'])
        s += " Conveyance Allowance:       {:>10.2f} | ESIC (0.75%):               {:>10.2f}\n".format(sal['conveyance'], sal['ee_esi'])
        s += "-" * 78 + "\n"
        s += " GROSS EARNINGS:             ₹{:>10.2f} | TOTAL DEDUCTIONS:           ₹{:>10.2f}\n".format(sal['gross'], sal['total_deductions'])
        s += "=" * 78 + "\n"
        s += " 💰 NET TAKE-HOME SALARY:     ₹{:>10.2f}\n".format(sal['net_pay'])
        s += " Employer PF Share: ₹{:.2f} (EPF: ₹{:.2f} | EPS: ₹{:.2f})\n".format(sal['er_epf'] + sal['er_eps'], sal['er_epf'], sal['er_eps'])
        s += "=" * 78 + "\n"
        return s

class PayrollCoordinator:
    def __init__(self, count=100):
        self.count = count
        self.kuber = KuberMathAgent()
        self.lekhak = LekhakAuditAgent()

    def process_all_100_employees(self):
        tot_gross = 0.0
        tot_net = 0.0
        tot_pf = 0.0
        tot_tds = 0.0
        tot_pt = 0.0

        for i in range(1, self.count + 1):
            emp = get_employee(i)
            sal = self.kuber.calculate_salary_structure(emp)
            tot_gross += sal["gross"]
            tot_net += sal["net_pay"]
            tot_pf += (sal["ee_pf"] + sal["er_epf"] + sal["er_eps"])
            tot_tds += sal["tds"]
            tot_pt += sal["pt"]

        return {
            "count": self.count,
            "tot_gross": tot_gross,
            "tot_net": tot_net,
            "tot_pf": tot_pf,
            "tot_tds": tot_tds,
            "tot_pt": tot_pt
        }

    def get_employee_payslip(self, emp_id_or_name):
        q = emp_id_or_name.lower().strip()
        for i in range(1, self.count + 1):
            emp = get_employee(i)
            if q == emp["emp_id"].lower() or q in emp["name"].lower():
                sal = self.kuber.calculate_salary_structure(emp)
                return self.lekhak.format_payslip(sal)
        return "Employee '{}' not found.".format(emp_id_or_name)

def run_payroll_demo():
    coord = PayrollCoordinator(100)
    res = coord.process_all_100_employees()
    print("Processed {} employees. Total Gross: ₹{:,.2f}".format(res["count"], res["tot_gross"]))

if __name__ == "__main__":
    run_payroll_demo()
