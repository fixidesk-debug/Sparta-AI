from locust import HttpUser, task, between

class SpartaUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def health(self):
        self.client.get('/api/health')

    @task(1)
    def upload_and_process(self):
        with open('test-data/sample.csv', 'rb') as f:
            files = {'file': ('sample.csv', f)}
            res = self.client.post('/api/upload', files=files)
            if res.status_code != 200:
                res.failure('Upload failed')
