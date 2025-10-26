#!/usr/bin/env python3
"""
Test script for Gemini conversational capabilities

This demonstrates:
1. Single-shot prompts
2. Multi-turn conversations with context
3. System instructions for specialized roles
4. Stateful vs stateless conversation modes

Usage:
    python test_gemini_conversation.py
"""

import asyncio
import os
from dotenv import load_dotenv
from app.specialists.gemini_adapter import GeminiAdapter

# Load environment variables
load_dotenv()


async def test_single_shot():
    """Test single-shot completion (stateless)"""
    print("\n" + "=" * 60)
    print("TEST 1: Single-Shot Completion")
    print("=" * 60)
    
    adapter = GeminiAdapter()
    
    prompt = "What are the four elements required to prove negligence in a personal injury case? Please be brief."
    print(f"\n📤 Prompt: {prompt}")
    
    response = await adapter.complete(prompt)
    print(f"\n🤖 Gemini Response:\n{response}")
    print("\n" + "-" * 60)


async def test_conversation_with_history():
    """Test multi-turn conversation with context"""
    print("\n" + "=" * 60)
    print("TEST 2: Multi-Turn Conversation (Stateful)")
    print("=" * 60)
    
    adapter = GeminiAdapter(
        system_instruction="You are a helpful legal research assistant specializing in personal injury law."
    )
    
    # Turn 1
    message1 = "What is negligence?"
    print(f"\n👤 User: {message1}")
    response1 = await adapter.add_to_conversation(message1)
    print(f"🤖 Gemini: {response1}")
    
    # Turn 2 - This should reference the previous context
    message2 = "Can you give me a specific example from case law?"
    print(f"\n👤 User: {message2}")
    response2 = await adapter.add_to_conversation(message2)
    print(f"🤖 Gemini: {response2}")
    
    # Turn 3 - Further following up
    message3 = "How does this apply to auto accidents?"
    print(f"\n👤 User: {message3}")
    response3 = await adapter.add_to_conversation(message3)
    print(f"🤖 Gemini: {response3}")
    
    print(f"\n📊 Total messages in conversation: {len(adapter.conversation_history)}")
    print("\n" + "-" * 60)


async def test_chat_method():
    """Test chat method with message history"""
    print("\n" + "=" * 60)
    print("TEST 3: Chat Method (Stateless with History)")
    print("=" * 60)
    
    adapter = GeminiAdapter(
        system_instruction="You are a client communication specialist for a law firm."
    )
    
    messages = [
        {"role": "user", "content": "How should I explain statute of limitations to a client?"},
        {"role": "assistant", "content": "The statute of limitations is the deadline for filing a lawsuit. It's important to explain it in simple terms to clients."},
        {"role": "user", "content": "What's the statute for personal injury in most states?"}
    ]
    
    print("\n📜 Message History:")
    for msg in messages:
        print(f"  {msg['role'].upper()}: {msg['content']}")
    
    print("\n🔄 Getting response...")
    response = await adapter.chat(messages)
    print(f"\n🤖 Gemini: {response}")
    print("\n" + "-" * 60)


async def test_system_instruction_impact():
    """Test how system instructions affect responses"""
    print("\n" + "=" * 60)
    print("TEST 4: System Instruction Impact")
    print("=" * 60)
    
    question = "Tell me about negligence in a car accident case."
    
    # Without system instruction
    print("\n🔸 WITHOUT System Instruction:")
    adapter1 = GeminiAdapter()
    response1 = await adapter1.complete(question)
    print(f"🤖 Response: {response1[:200]}...")
    
    # With legal researcher instruction
    print("\n🔸 WITH 'Legal Researcher' Instruction:")
    adapter2 = GeminiAdapter(
        system_instruction="You are a senior legal researcher. Provide technical, detailed legal analysis with citations."
    )
    response2 = await adapter2.complete(question)
    print(f"🤖 Response: {response2[:200]}...")
    
    # With client communication instruction
    print("\n🔸 WITH 'Client Communication' Instruction:")
    adapter3 = GeminiAdapter(
        system_instruction="You are drafting a message for a client. Use simple, empathetic language avoiding legal jargon."
    )
    response3 = await adapter3.complete(question)
    print(f"🤖 Response: {response3[:200]}...")
    
    print("\n" + "-" * 60)


async def test_legal_research_scenario():
    """Test a realistic legal research conversation"""
    print("\n" + "=" * 60)
    print("TEST 5: Realistic Legal Research Scenario")
    print("=" * 60)
    
    adapter = GeminiAdapter(
        system_instruction="""You are an experienced legal researcher specializing in personal injury law. 
        Provide clear, actionable analysis with specific legal principles and case citations when possible."""
    )
    
    # Simulate a real conversation
    conversation = [
        "A client was rear-ended at a red light. They have neck pain and missed 2 weeks of work. What legal theories apply?",
        "What evidence should we gather to strengthen the negligence claim?",
        "How do we calculate potential damages?",
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n🔹 Turn {i}:")
        print(f"👤 Attorney: {message}")
        response = await adapter.add_to_conversation(message)
        print(f"🤖 Research Assistant: {response}")
        print()
    
    print(f"📊 Conversation length: {len(adapter.conversation_history)} messages")
    print("\n" + "-" * 60)


async def test_client_communication_scenario():
    """Test client communication drafting"""
    print("\n" + "=" * 60)
    print("TEST 6: Client Communication Scenario")
    print("=" * 60)
    
    adapter = GeminiAdapter(
        system_instruction="""You are a compassionate legal assistant drafting client communications. 
        Use warm, empathetic language. Avoid legal jargon. Keep clients informed and reassured.""",
        temperature=0.7  # Slightly higher for more natural language
    )
    
    context = """Client John Doe was injured in a slip and fall at a grocery store. 
    He had surgery on his knee and is worried about medical bills. 
    We've sent a demand letter to the store's insurance company and are waiting for response."""
    
    print(f"\n📋 Context: {context}")
    
    message = f"Draft an email to John updating him on his case. Context: {context}"
    print(f"\n👤 Request: {message}")
    
    response = await adapter.complete(message)
    print(f"\n📧 Draft Email:\n{response}")
    print("\n" + "-" * 60)


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("🧪 GEMINI CONVERSATIONAL CAPABILITY TESTS")
    print("=" * 80)
    
    # Check for API key
    if not os.getenv("GOOGLE_AI_API_KEY"):
        print("\n❌ ERROR: GOOGLE_AI_API_KEY not found in environment variables")
        print("Please set your Gemini API key in .env file:")
        print("  GOOGLE_AI_API_KEY=your_api_key_here")
        return
    
    print("\n✅ Gemini API key found")
    
    try:
        # Run all tests
        await test_single_shot()
        await test_conversation_with_history()
        await test_chat_method()
        await test_system_instruction_impact()
        await test_legal_research_scenario()
        await test_client_communication_scenario()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\n💡 Key Takeaways:")
        print("  1. Use complete() for single-shot prompts")
        print("  2. Use add_to_conversation() for stateful conversations")
        print("  3. Use chat() for stateless multi-turn conversations")
        print("  4. System instructions dramatically improve response quality")
        print("  5. Temperature affects creativity (0.3 = focused, 0.7 = creative)")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

