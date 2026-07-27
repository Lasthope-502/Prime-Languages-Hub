import time

class CircuitBreaker:
    """
    3 states:
    - CLOSED: sab normal, requests jaa rahi hain
    - OPEN: bohot fails hue, ab thori dair requests skip karo
    - HALF_OPEN: thori dair baad ek test request bhejo, dekho theek hua ya nahi
    """

    def __init__(self, failure_threshold=3, recovery_timeout=10):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            print(f"[CIRCUIT BREAKER] OPEN — too many failures, pausing calls temporarily")

    def can_attempt(self) -> bool:
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            # Recovery timeout guzar gaya? tou ek chance do (HALF_OPEN)
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                print(f"[CIRCUIT BREAKER] HALF_OPEN — testing if engine recovered")
                return True
            return False  # abhi bhi OPEN hai, skip karo

        if self.state == "HALF_OPEN":
            return True

        return False