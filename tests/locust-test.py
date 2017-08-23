from locust import HttpLocust, TaskSet, task

class CamelotLoadTest(TaskSet):
    @task(1)
    def index(self):
        self.client.get("admin")

class User(HttpLocust):
    task_set = CamelotLoadTest
    min_wait = 5000
    max_wait = 15000
