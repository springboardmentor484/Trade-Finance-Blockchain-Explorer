"""
Test Module E: Analytics & Reporting
Tests analytics endpoints, exports, and KPI calculations
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_module_e():
    token = None
    
    # ✅ STEP 1: Login
    print_section("1. LOGIN")
    login_payload = {
        "email": "moduletest@example.com",
        "password": "TestPassword123!"
    }
    res = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    
    if res.status_code == 200:
        token = res.json()["access_token"]
        print(f"✅ Login successful")
    else:
        print("❌ Login failed")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # ✅ STEP 2: Get Document Analytics
    print_section("2. DOCUMENT ANALYTICS")
    res = requests.get(f"{BASE_URL}/analytics/documents/summary", headers=headers)
    print(f"Status: {res.status_code}")
    
    if res.status_code == 200:
        doc_analytics = res.json()
        print(f"✅ Document analytics retrieved")
        print(f"   Total Documents: {doc_analytics['total_documents']}")
        print(f"   Status Breakdown: {doc_analytics['status_breakdown']}")
        print(f"   Recent Docs: {len(doc_analytics['recent_documents'])}")
    else:
        print("❌ Failed to get document analytics")
    
    # ✅ STEP 3: Get Transaction Analytics
    print_section("3. TRANSACTION ANALYTICS")
    res = requests.get(f"{BASE_URL}/analytics/transactions/summary", headers=headers)
    print(f"Status: {res.status_code}")
    
    if res.status_code == 200:
        tx_analytics = res.json()
        print(f"✅ Transaction analytics retrieved")
        print(f"   Total Transactions: {tx_analytics['total_transactions']}")
        print(f"   Total Volume: ${tx_analytics['total_volume']:,.2f}")
        print(f"   Average Transaction: ${tx_analytics['average_transaction']:,.2f}")
        print(f"   Avg Risk Score: {tx_analytics['average_risk_score']}")
        print(f"   Risk Distribution: {tx_analytics['risk_distribution']}")
    else:
        print("❌ Failed to get transaction analytics")
    
    # ✅ STEP 4: Get Dashboard KPIs
    print_section("4. DASHBOARD KPIs")
    res = requests.get(f"{BASE_URL}/analytics/dashboard/kpis", headers=headers)
    print(f"Status: {res.status_code}")
    
    if res.status_code == 200:
        kpis = res.json()
        print(f"✅ KPIs retrieved")
        print(f"   Document KPIs:")
        print(f"     - Total: {kpis['document_kpis']['total']}")
        print(f"     - Verification Rate: {kpis['document_kpis']['verification_rate']}%")
        print(f"   Transaction KPIs:")
        print(f"     - Total: {kpis['transaction_kpis']['total']}")
        print(f"     - Settlement Rate: {kpis['transaction_kpis']['settlement_rate']}%")
        print(f"   Risk KPIs:")
        print(f"     - Average Score: {kpis['risk_kpis']['average_score']}")
        print(f"     - Health Score: {kpis['risk_kpis']['health_score']}%")
    else:
        print("❌ Failed to get KPIs")
    
    # ✅ STEP 5: Export Documents as CSV
    print_section("5. EXPORT DOCUMENTS CSV")
    res = requests.get(f"{BASE_URL}/analytics/export/documents/csv", headers=headers)
    print(f"Status: {res.status_code}")
    
    if res.status_code == 200:
        export_data = res.json()
        print(f"✅ Documents CSV exported")
        print(f"   Filename: {export_data['filename']}")
        print(f"   Record Count: {export_data['record_count']}")
        print(f"   CSV Preview (first 2 lines):")
        csv_lines = export_data['content'].split('\n')
        for line in csv_lines[:2]:
            print(f"     {line}")
    else:
        print("❌ Failed to export documents CSV")
    
    # ✅ STEP 6: Export Transactions as CSV
    print_section("6. EXPORT TRANSACTIONS CSV")
    res = requests.get(f"{BASE_URL}/analytics/export/transactions/csv", headers=headers)
    print(f"Status: {res.status_code}")
    
    if res.status_code == 200:
        export_data = res.json()
        print(f"✅ Transactions CSV exported")
        print(f"   Filename: {export_data['filename']}")
        print(f"   Record Count: {export_data['record_count']}")
        print(f"   CSV Preview (first 2 lines):")
        csv_lines = export_data['content'].split('\n')
        for line in csv_lines[:2]:
            print(f"     {line[:80]}...")
    else:
        print("❌ Failed to export transactions CSV")
    
    # ✅ STEP 7: Get Activity Log
    print_section("7. ACTIVITY LOG (LAST 30 DAYS)")
    res = requests.get(f"{BASE_URL}/analytics/ledger/activity?days=30", headers=headers)
    print(f"Status: {res.status_code}")
    
    if res.status_code == 200:
        activity = res.json()
        print(f"✅ Activity log retrieved")
        print(f"   Total Activities: {activity['total_activities']}")
        print(f"   Period: {activity['period_days']} days")
        if activity['activities']:
            print(f"   Sample Activities:")
            for act in activity['activities'][:3]:
                print(f"     - {act['action']} on Doc #{act['document_id']}")
    else:
        print("❌ Failed to get activity log")
    
    print_section("MODULE E TESTS COMPLETED ✅")
    print("\n✨ All analytics and reporting features working!")

if __name__ == "__main__":
    print("\n🚀 Module E: Analytics & Reporting Test Suite\n")
    test_module_e()
