import time

from cloudpilot.load_tester import simulate_workload
from locust import User, between, task


class LoadTestUser(User):
    wait_time = between(1, 3)

    @task
    def generate_workload(self):
        # Generate a 1-second workload with intensity 2 using the 'normal' pattern.
        events = simulate_workload(duration=1, intensity=2, pattern="normal")
        for event in events:
            print(f"Simulated event at {event:.2f} sec")
            time.sleep(0.1)
