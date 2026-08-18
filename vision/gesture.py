from collections import deque, Counter
from time import monotonic

class GestureController:
    def __init__(self, buffer_size=5, confidence=0.8, cooldown=3):
        self.history = deque(maxlen=buffer_size)
        self.confidence = confidence
        self.cooldown = cooldown
        self.last_action = 0

    def update(self, gesture, confidence):
        if confidence < self.confidence:
            return None

        self.history.append(gesture)

        if len(self.history) < self.history.maxlen:
            return None

        stable = Counter(self.history).most_common(1)[0][0]

        now = monotonic()

        if now - self.last_action < self.cooldown:
            return None

        self.last_action = now
        return stable