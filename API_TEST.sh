#!/bin/bash

# Trade Finance API - Quick Test Script
# This script demonstrates all the key API endpoints

BASE_URL="http://localhost:8000"
BANK_TOKEN=""
BUYER_TOKEN=""
SELLER_TOKEN=""
AUDITOR_TOKEN=""
BUYER_ID=""
SELLER_ID=""
BANK_ID=""
AUDITOR_ID=""
PO_DOC_ID=""

echo "=== Trade Finance Blockchain Explorer - API Test Suite ==="
echo ""

# 1. Register Users
echo "Step 1: Registering users..."

echo "Registering Buyer..."
BUYER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "email": "buyer@company.com",
    "password": "password123",
    "role": "corporate",
    "org_name": "Acme Corp"
  }')
BUYER_ID=$(echo $BUYER_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "Buyer ID: $BUYER_ID"

echo "Registering Seller..."
SELLER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "seller@company.com",
    "password": "password123",
    "role": "corporate",
    "org_name": "Global Traders"
  }')
SELLER_ID=$(echo $SELLER_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "Seller ID: $SELLER_ID"

echo "Registering Bank..."
BANK_RESPONSE=$(curl -s -X POST "$BASE_URL/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "David Johnson",
    "email": "bank@finance.com",
    "password": "password123",
    "role": "bank",
    "org_name": "International Bank"
  }')
BANK_ID=$(echo $BANK_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "Bank ID: $BANK_ID"

echo "Registering Auditor..."
AUDITOR_RESPONSE=$(curl -s -X POST "$BASE_URL/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Emily Wilson",
    "email": "auditor@compliance.com",
    "password": "password123",
    "role": "auditor",
    "org_name": "Compliance Auditors Inc"
  }')
AUDITOR_ID=$(echo $AUDITOR_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "Auditor ID: $AUDITOR_ID"
echo ""

# 2. Login Users
echo "Step 2: Logging in users..."

echo "Logging in Buyer..."
BUYER_LOGIN=$(curl -s -X POST "$BASE_URL/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "buyer@company.com",
    "password": "password123"
  }')
BUYER_TOKEN=$(echo $BUYER_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Buyer Token: ${BUYER_TOKEN:0:20}..."

echo "Logging in Seller..."
SELLER_LOGIN=$(curl -s -X POST "$BASE_URL/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@company.com",
    "password": "password123"
  }')
SELLER_TOKEN=$(echo $SELLER_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Seller Token: ${SELLER_TOKEN:0:20}..."

echo "Logging in Bank..."
BANK_LOGIN=$(curl -s -X POST "$BASE_URL/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bank@finance.com",
    "password": "password123"
  }')
BANK_TOKEN=$(echo $BANK_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Bank Token: ${BANK_TOKEN:0:20}..."

echo "Logging in Auditor..."
AUDITOR_LOGIN=$(curl -s -X POST "$BASE_URL/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "auditor@compliance.com",
    "password": "password123"
  }')
AUDITOR_TOKEN=$(echo $AUDITOR_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Auditor Token: ${AUDITOR_TOKEN:0:20}..."
echo ""

# 3. Get Users by Role
echo "Step 3: Fetching corporate users (sellers)..."
curl -s "$BASE_URL/api/users?role=corporate" \
  -H "Authorization: Bearer $BUYER_TOKEN" | jq '.'
echo ""

# 4. Create test PDF file
echo "Step 4: Creating test PDF file..."
cat > /tmp/test_po.txt << 'EOF'
%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< >>
stream
BT
/F1 12 Tf
50 750 Td
(Purchase Order) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000229 00000 n
0000000334 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
431
%%EOF
EOF

# 5. Upload PO Document (as Buyer)
echo "Step 5: Uploading Purchase Order (as Buyer)..."
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/documents/upload" \
  -H "Authorization: Bearer $BUYER_TOKEN" \
  -F "doc_number=PO-2026-001" \
  -F "doc_type=PO" \
  -F "seller_id=$SELLER_ID" \
  -F "file=@/tmp/test_po.txt")
PO_DOC_ID=$(echo $UPLOAD_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "Upload Response:"
echo $UPLOAD_RESPONSE | jq '.'
echo "PO Document ID: $PO_DOC_ID"
echo ""

# 6. Get Document Details
echo "Step 6: Fetching PO document details..."
curl -s "$BASE_URL/api/documents/$PO_DOC_ID" \
  -H "Authorization: Bearer $BUYER_TOKEN" | jq '.'
echo ""

# 7. Bank issues LOC
echo "Step 7: Bank issuing Letter of Credit for PO..."
curl -s -X POST "$BASE_URL/api/documents/action" \
  -H "Authorization: Bearer $BANK_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"doc_id\": $PO_DOC_ID,
    \"action\": \"ISSUE_LOC\",
    \"metadata\": {\"loc_amount\": 100000, \"currency\": \"USD\"}
  }" | jq '.'
echo ""

# 8. Auditor verifies PO
echo "Step 8: Auditor verifying Purchase Order..."
curl -s -X POST "$BASE_URL/api/documents/action" \
  -H "Authorization: Bearer $AUDITOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"doc_id\": $PO_DOC_ID,
    \"action\": \"VERIFIED\",
    \"metadata\": {\"verified_by\": \"Auditor\"}
  }" | jq '.'
echo ""

# 9. Get final document state with timeline
echo "Step 9: Final document state with timeline..."
curl -s "$BASE_URL/api/documents/$PO_DOC_ID" \
  -H "Authorization: Bearer $BUYER_TOKEN" | jq '.ledger_entries'
echo ""

echo "=== Test Suite Complete ==="
echo "Summary:"
echo "- Buyer ID: $BUYER_ID"
echo "- Seller ID: $SELLER_ID"
echo "- Bank ID: $BANK_ID"
echo "- Auditor ID: $AUDITOR_ID"
echo "- PO Document ID: $PO_DOC_ID"
