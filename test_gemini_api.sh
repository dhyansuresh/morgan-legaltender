#!/bin/bash

# Test script for Gemini Conversation API endpoints
# Make sure the backend is running: cd backend && python main.py

BASE_URL="http://localhost:8000/api"

echo "======================================================================"
echo "🧪 Testing Gemini Conversational API"
echo "======================================================================"

# Check if server is running
echo -e "\n🔍 Checking if server is running..."
if ! curl -s "${BASE_URL%/api}/health" > /dev/null 2>&1; then
    echo "❌ Server is not running!"
    echo "Start it with: cd backend && python main.py"
    exit 1
fi
echo "✅ Server is running"

# Test 1: Start a conversation
echo -e "\n======================================================================"
echo "TEST 1: Start a conversation"
echo "======================================================================"
CONV_START=$(curl -s -X POST "${BASE_URL}/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "system_instruction": "You are a legal research assistant specializing in personal injury law.",
    "initial_message": "What are the four elements of negligence?"
  }')

echo "$CONV_START" | python3 -m json.tool

# Extract conversation ID
CONV_ID=$(echo "$CONV_START" | python3 -c "import sys, json; print(json.load(sys.stdin).get('conversation_id', ''))")

if [ -z "$CONV_ID" ]; then
    echo "❌ Failed to start conversation. Check if GOOGLE_AI_API_KEY is set."
    exit 1
fi

echo -e "\n📝 Conversation ID: $CONV_ID"

# Test 2: Continue the conversation
echo -e "\n======================================================================"
echo "TEST 2: Continue the conversation"
echo "======================================================================"
curl -s -X POST "${BASE_URL}/conversation/continue" \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"message\": \"Can you give me a specific example from a real case?\"
  }" | python3 -m json.tool

# Test 3: Get conversation history
echo -e "\n======================================================================"
echo "TEST 3: Get conversation history"
echo "======================================================================"
curl -s "${BASE_URL}/conversation/${CONV_ID}/history" | python3 -m json.tool

# Test 4: Continue again
echo -e "\n======================================================================"
echo "TEST 4: Continue conversation (third turn)"
echo "======================================================================"
curl -s -X POST "${BASE_URL}/conversation/continue" \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"message\": \"How does this apply to car accidents specifically?\"
  }" | python3 -m json.tool

# Test 5: Multi-turn chat (stateless)
echo -e "\n======================================================================"
echo "TEST 5: Multi-turn chat (stateless)"
echo "======================================================================"
curl -s -X POST "${BASE_URL}/chat/multi-turn" \
  -H "Content-Type: application/json" \
  -d '{
    "system_instruction": "You are a compassionate client communication specialist.",
    "messages": [
      {"role": "user", "content": "How should I tell a client their case might take 6 months?"},
      {"role": "assistant", "content": "Be honest but reassuring. Explain the process clearly."},
      {"role": "user", "content": "What specific timeline should I share?"}
    ]
  }' | python3 -m json.tool

# Test 6: List active conversations
echo -e "\n======================================================================"
echo "TEST 6: List active conversations"
echo "======================================================================"
curl -s "${BASE_URL}/conversations/active" | python3 -m json.tool

# Test 7: End conversation
echo -e "\n======================================================================"
echo "TEST 7: End conversation"
echo "======================================================================"
curl -s -X DELETE "${BASE_URL}/conversation/${CONV_ID}" | python3 -m json.tool

# Test 8: Legal researcher specialist
echo -e "\n======================================================================"
echo "TEST 8: Legal Researcher Specialist (using Gemini)"
echo "======================================================================"
curl -s -X POST "${BASE_URL}/specialists/legal-researcher/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Client was rear-ended at a red light. They have whiplash and missed 2 weeks of work. The other driver was texting.",
    "case_id": "CASE-TEST-001"
  }' | python3 -m json.tool

# Test 9: Client communication specialist
echo -e "\n======================================================================"
echo "TEST 9: Client Communication Specialist (using Gemini)"
echo "======================================================================"
curl -s -X POST "${BASE_URL}/specialists/client-communication/draft" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "John Smith",
    "purpose": "case update",
    "text": "We sent the demand letter to the insurance company. They are reviewing it and should respond within 30 days. The demand includes $50,000 for medical expenses and lost wages."
  }' | python3 -m json.tool

echo -e "\n======================================================================"
echo "✅ All tests completed!"
echo "======================================================================"
echo ""
echo "📚 Next steps:"
echo "  1. Review the responses above"
echo "  2. Try modifying the prompts"
echo "  3. Check the API docs: http://localhost:8000/docs"
echo "  4. See GEMINI_CONVERSATION_GUIDE.md for detailed usage"
echo ""

