"""
Nexus Warmup Engine — Load Testing Suite
Uses Locust for production-grade performance testing.

Run with: locust -f tests/load_test.py --host http://localhost:8000
Dashboard: http://localhost:8089
"""
from locust import HttpUser, task, between, events
import json
import time


class NexusUser(HttpUser):
    """Simulates a real Nexus user interacting with the API."""
    wait_time = between(1, 3)
    
    def on_start(self):
        """Register and login on startup."""
        ts = str(int(time.time() * 1000))
        self.email = f"loadtest_{ts}@nexus.test"
        self.password = "LoadTest123!"
        
        # Register
        self.client.post("/api/v1/auth/register", json={
            "email": self.email,
            "password": self.password,
            "full_name": f"Load Tester {ts}"
        })
        
        # Login
        resp = self.client.post("/api/v1/auth/login", json={
            "email": self.email,
            "password": self.password,
        })
        
        if resp.status_code == 200:
            data = resp.json()
            self.token = data.get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = ""
            self.headers = {}
    
    @task(5)
    def check_health(self):
        """High frequency — quick health check."""
        self.client.get("/api/v1/health")
    
    @task(3)
    def deep_health(self):
        """Medium frequency — deep health with DB query."""
        self.client.get("/api/v1/health/deep")
    
    @task(3)
    def get_warmup_status(self):
        """Medium frequency — fetch warmup dashboard data."""
        if self.token:
            self.client.get("/api/v1/warmup/status", headers=self.headers)
    
    @task(2)
    def list_accounts(self):
        """Lower frequency — list email accounts."""
        if self.token:
            self.client.get("/api/v1/accounts", headers=self.headers)
    
    @task(1)
    def get_metrics(self):
        """Low frequency — metrics scrape."""
        self.client.get("/api/v1/health/metrics")


class NexusAdmin(HttpUser):
    """
    Simulates an admin user hitting heavier endpoints.
    Represents ~10% of traffic.
    """
    wait_time = between(3, 8)
    weight = 1  # Lower weight = less instances
    
    @task
    def deep_health_check(self):
        self.client.get("/api/v1/health/deep")
    
    @task
    def metrics_scrape(self):
        self.client.get("/api/v1/health/metrics")
