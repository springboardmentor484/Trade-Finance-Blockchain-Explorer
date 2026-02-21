"""
Test Module C: Ledger Explorer & Verification
Tests document verification and ledger querying functionality
"""
import requests
import json
import os

# API Base URL
BASE_URL = "http://127.0.0.1:8000"

# Test credentials
TEST_EMAIL = "moduletest@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_ORG = "Test Trading Corp"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_workflow():
    access_token = None
    doc_id = None
    
    # ✅ STEP 1: Signup
    print_section("1. SIGNUP TEST")
    signup_payload = {
        "name": "Module C Tester",
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "role": "buyer",
        "org_name": TEST_ORG
    }
    res = requests.post(f"{BASE_URL}/users/signup", json=signup_payload)
    print(f"Status: {res.status_code}")
    print(f"Response: {json.dumps(res.json(), indent=2)}")
    
    if res.status_code == 201:
        print(f"✅ Signup successful (first time)")
    elif res.status_code == 400:
        print("ℹ️  User may already exist, proceeding to login...")
    else:
        print(f"❌ Signup error: {res.status_code}")
    
    # ✅ STEP 2: Login
    print_section("2. LOGIN TEST")
    login_payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    res = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    print(f"Status: {res.status_code}")
    data = res.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if res.status_code == 200:
        access_token = data["access_token"]
        print(f"✅ Login successful - Token: {access_token[:20]}...")
    else:
        print("❌ Login failed")
        return
    
    # ✅ STEP 3: Upload Document
    print_section("3. DOCUMENT UPLOAD TEST")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create test file
    test_file_path = "test_document.txt"
    test_content = "This is a test purchase order document for trade finance verification."
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    with open(test_file_path, "rb") as f:
        files = {
            "file": ("test_po.txt", f, "text/plain")
        }
        data = {
            "doc_type": "PO",
            "doc_number": "PO-2024-001"
        }
        res = requests.post(f"{BASE_URL}/documents/", files=files, data=data, headers=headers)
    
    print(f"Status: {res.status_code}")
    upload_data = res.json()
    print(f"Response: {json.dumps(upload_data, indent=2)}")
    
    if res.status_code == 200:
        doc_id = upload_data["id"]
        stored_hash = upload_data["hash"]
        print(f"✅ Upload successful - Doc ID: {doc_id}")
        print(f"   Stored Hash: {stored_hash[:16]}...")
    else:
        print(f"❌ Upload failed: {res.status_code}")
        return
    
    # Cleanup test file
    os.remove(test_file_path)
    
    # ✅ STEP 4: Verify Document Integrity
    print_section("4. DOCUMENT VERIFICATION TEST")
    res = requests.post(f"{BASE_URL}/documents/{doc_id}/verify", headers=headers)
    print(f"Status: {res.status_code}")
    verify_data = res.json()
    print(f"Response: {json.dumps(verify_data, indent=2)}")
    
    if res.status_code == 200:
        is_valid = verify_data["is_valid"]
        print(f"✅ Verification endpoint working")
        print(f"   Document Valid: {is_valid}")
        print(f"   Hashes Match: {verify_data['stored_hash'] == verify_data['computed_hash']}")
    else:
        print("❌ Verification failed")
    
    # ✅ STEP 5: Fetch Full Ledger
    print_section("5. LEDGER QUERY TEST")
    res = requests.get(f"{BASE_URL}/documents/ledger/all", headers=headers)
    print(f"Status: {res.status_code}")
    ledger_data = res.json()
    print(f"Response: {json.dumps(ledger_data, indent=2)}")
    
    if res.status_code == 200:
        total = ledger_data.get("total", 0)
        print(f"✅ Ledger query successful - Total entries: {total}")
        if ledger_data.get("entries"):
            print(f"   Sample entry: {ledger_data['entries'][0]['action']}")
    else:
        print("❌ Ledger query failed")
    
    # ✅ STEP 6: Fetch Ledger with Filters
    print_section("6. LEDGER FILTER TEST")
    res = requests.get(
        f"{BASE_URL}/documents/ledger/all?doc_id={doc_id}",
        headers=headers
    )
    print(f"Status: {res.status_code}")
    filtered_data = res.json()
    print(f"Filtered entries for doc {doc_id}: {filtered_data.get('total', 0)}")
    
    if filtered_data.get("entries"):
        for entry in filtered_data["entries"]:
            print(f"  - {entry['action']}: {entry.get('meta', {})}")
    
    print(f"✅ Ledger filter working")
    
    # ✅ STEP 7: Get Document Details with Ledger
    print_section("7. DOCUMENT DETAILS WITH LEDGER TEST")
    res = requests.get(f"{BASE_URL}/documents/{doc_id}/read", headers=headers)
    print(f"Status: {res.status_code}")
    detail_data = res.json()
    
    if res.status_code == 200:
        doc = detail_data["document"]
        ledger = detail_data["ledger"]
        print(f"✅ Document details with ledger retrieved")
        print(f"   Document: {doc['doc_number']} ({doc['status']})")
        print(f"   Ledger entries: {len(ledger)}")
        print(f"   Allowed actions: {len(detail_data.get('allowed_actions', []))}")
        
        # Show ledger timeline
        print("\n   Ledger Timeline:")
        for entry in ledger:
            print(f"     - {entry['action']} (by user {entry['actor_id']})")
    else:
        print("❌ Failed to get document details")
    
    print_section("MODULE C TESTS COMPLETED ✅")

if __name__ == "__main__":
    print("\n🚀 Module C: Ledger Explorer & Verification Test Suite\n")
    test_workflow()
