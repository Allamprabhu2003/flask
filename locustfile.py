# from locust import HttpUser, TaskSet, task


# class UserBehavior(TaskSet):
#     @task
#     def my_task(self):
#         self.client.get("/")

# class WebsiteUser(HttpUser):
#     tasks = [UserBehavior]
#     host = "http://127.0.0.1:5000"  # Replace with your target host"  # Replace with your target host


from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task
    def recognize_image(self):
        class_id = 1  # Replace with a valid class_id
        with open('path_to_your_image.jpg', 'rb') as f:
            files = {'image': f}
            response = self.client.post(f"/recognize_image/{class_id}", files=files)
            if response.status_code != 200:
                response.failure(f"Failed to recognize image: {response.text}")

    @task
    def recognize(self):
        class_id = 1  # Replace with a valid class_id
        response = self.client.get(f"/recognize/{class_id}")
        if response.status_code != 200:
            response.failure(f"Failed to load recognize page: {response.text}")

    @task
    def video_feed(self):
        class_id = 1  # Replace with a valid class_id
        response = self.client.get(f"/video_feed/{class_id}", stream=True)
        if response.status_code != 200:
            response.failure(f"Failed to load video feed: {response.text}")

    @task
    def change_video_source(self):
        class_id = 1  # Replace with a valid class_id
        data = {'video_source': 'webcam'}
        response = self.client.post(f"/change_video_source/{class_id}", data=data)
        if response.status_code != 200:
            response.failure(f"Failed to change video source: {response.text}")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
