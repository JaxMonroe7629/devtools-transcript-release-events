from devtools_event_service import ToolEvent, decide


def test_release_publish_becomes_queue_transition():
    event = ToolEvent(kind="release", summary="tag v2", action="publish")
    assert decide(event) == "release queued"

