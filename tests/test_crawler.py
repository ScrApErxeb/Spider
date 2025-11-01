from crawler.queue_manager import QueueManager

def test_queue_manager():
    q = QueueManager()
    q.enqueue("url1")
    assert not q.is_empty()
    assert q.dequeue() == "url1"
