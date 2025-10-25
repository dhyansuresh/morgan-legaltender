import asyncio

from app.specialists.client_communication import ClientCommunicator, MockCommAdapter


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_client_communicator_happy_path():
    cc = ClientCommunicator(llm_adapter=MockCommAdapter())
    context = "I was in a car crash, neck and back pain, had MRI, other driver ran a red light."
    out = run_async(cc.draft("Jane", "status update", context))
    assert "draft_message" in out
    assert isinstance(out["draft_message"], str)
    assert out["subject"] is not None
    assert isinstance(out["suggested_followups"], list)


def test_client_communicator_empty_context():
    cc = ClientCommunicator(llm_adapter=MockCommAdapter())
    out = run_async(cc.draft(None, None, ""))
    assert "draft_message" in out and isinstance(out["draft_message"], str)
    assert out["subject"] == "Update from Your Legal Team"