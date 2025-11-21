class InMemoryTaskStore:
    def __init__(self):
        self.tasks = {}
        
    def add_task(self, task_id, task_data):
        self.tasks[task_id] = task_data
        
    def get_task(self, task_id):
        return self.tasks.get(task_id)
