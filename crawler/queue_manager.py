from collections import deque

class QueueManager:
    def __init__(self, start_urls=None):
        self.queue = deque(start_urls or [])
        self.visited = set()

    def enqueue(self, url):
        if url not in self.visited:
            self.queue.append(url)
            self.visited.add(url)

    def dequeue(self):
        return self.queue.popleft() if self.queue else None

    def is_empty(self):
        return len(self.queue) == 0

    # For compatibility with crawler_main.py
    def empty(self):
        return self.is_empty()

    def get(self):
        return self.dequeue()
