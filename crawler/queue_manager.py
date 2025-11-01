from collections import deque

class QueueManager:
    def __init__(self):
        self.queue = deque()
        self.visited = set()

    def enqueue(self, url):
        if url not in self.visited:
            self.queue.append(url)

    def dequeue(self):
        return self.queue.popleft() if self.queue else None

    def is_empty(self):
        return not self.queue

    def seen(self, url):
        self.visited.add(url)
