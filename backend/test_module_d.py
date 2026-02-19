"""
Test Module D: Trade Transactions & Risk Scoring
Tests transaction creation, risk calculation, and status updates
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_module_d():
    token = None
    buyer_id = 4  # From Module C test
    
    # ✅ STEP 1: Login
    print_section("1. LOGIN")
    login_payload = {
        "email": "moduletest@example.com",
        "password": "TestPassword123!"
    }
    res = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    print(f"Status: {res.status_code}")
    
    if res.status_code == 200:
        token = res.json()["access_token"]
        print(f"✅ Login successful - Token: {token[:20]}...")
    else:
        print("❌ Login failed")
        return
    
    # ✅ STEP 2: Create seller user (for transaction)
    print_section("2. CREATE SELLER USER")
    seller_payload = {
        "name": "Module D Seller",
        "email": "seller@moduletest.com",
        "password": "TestPassword123!",
        "role": "seller",
        "org_name": "Seller Corp"
    }
    res = requests.post(f"{BASE_URL}/users/signup", json=seller_payload)
    print(f"Status: {res.status_code}")
    
    if res.status_code == 201:
        seller_id = res.json()["id"]
        print(f"✅ Seller created - ID: {seller_id}")
    elif res.status_code == 400:
        print("ℹ️  Seller already exists")
        seller_id = 5
    else:
        print("❌ Failed to create seller")
        return
    
    # ✅ STEP 3: Create Transaction
    print_section("3. CREATE TRANSACTION")
    headers = {"Authorization": f"Bearer {token}"}
    
    tx_payload = {
        "buyer_id": buyer_id,
        "seller_id": seller_id,
        "amount": 50000.00,
        "currency": "USD",
        "description": "Purchase of goods - Test Transaction",
        "lc_number": "LC-2024-001",
        "lc_issuer_id": None
    }
    res = requests.post(f"{BASE_URL}/transactions/", json=tx_payload, headers=headers)
    print(f"Status: {res.status_code}")
    tx_data = res.json()
    print(f"Response: {json.dumps(tx_data, indent=2)}")
    
    if res.status_code in [200, 201]:
        tx_id = tx_data["id"]
        risk_score = tx_data["risk_score"]
        print(f"✅ Transaction created - ID: {tx_id}")
        print(f"   Risk Score: {risk_score}")
        print(f"   Risk Factors: {tx_data.get('risk_factors', {})}")
    else:
        print("❌ Transaction creation failed")
        return
    
    # ✅ STEP 4: Get Transaction Details
    print_section("4. GET TRANSACTION DETAILS")
    res = requests.get(f"{BASE_URL}/transactions/{tx_id}", headers=headers)
    print(f"Status: {res.status_code}")
    detail_data = res.json()
    print(f"Transaction: {detail_data['description']}")
    print(f"Amount: ${detail_data['amount']} {detail_data['currency']}")
    print(f"Risk Score: {detail_data['risk_score']}")
    print(f"Status: {detail_data['status']}")
    
    if res.status_code == 200:
        print("✅ Transaction details retrieved")
    else:
        print("❌ Failed to get transaction details")
    
    # ✅ STEP 5: Update Transaction Status
    print_section("5. UPDATE TRANSACTION STATUS")
    status_payload = {
        "status": "CONFIRMED",
        "notes": "Buyer confirmed receipt of LC"
    }
    res = requests.post(
        f"{BASE_URL}/transactions/{tx_id}/status",
        json=status_payload,
        headers=headers
    )
    print(f"Status: {res.status_code}")
    updated_data = res.json()
    print(f"New Status: {updated_data['status']}")
    
    if res.status_code == 200:
        print("✅ Status updated successfully")
    else:
        print("❌ Failed to update status")
    
    # ✅ STEP 6: Get Risk Summary
    print_section("6. RISK SUMMARY ANALYTICS")
    res = requests.get(f"{BASE_URL}/transactions/analytics/risk-summary", headers=headers)
    print(f"Status: {res.status_code}")
    
    if res.status_code == 200:
        summary = res.json()
        print(f"✅ Risk summary retrieved")
        print(f"   Total Transactions: {summary['total_transactions']}")
        print(f"   Average Risk Score: {summary['average_risk_score']}")
        print(f"   Risk Distribution: {summary['risk_distribution']}")
        print(f"   High Risk Count: {summary['high_risk_count']}")
        print(f"   Total Volume: ${summary['total_volume']:,.2f}")
    else:
        print("❌ Failed to get risk summary")
    
    # ✅ STEP 7: List All Transactions
    print_section("7. LIST ALL TRANSACTIONS")
    res = requests.get(f"{BASE_URL}/transactions/", headers=headers)
    print(f"Status: {res.status_code}")
    
    if res.status_code == 200:
        txns = res.json()
        print(f"✅ Retrieved {len(txns)} transaction(s)")
        for tx in txns:
            print(f"   - TX#{tx['id']}: {tx['description']} | ${tx['amount']} | Risk: {tx['risk_score']}")
    else:
        print("❌ Failed to list transactions")
    
    print_section("MODULE D TESTS COMPLETED ✅")

if __name__ == "__main__":
    print("\n🚀 Module D: Trade Transactions & Risk Scoring Test Suite\n")
    test_module_d()
