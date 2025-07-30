#!/usr/bin/env python3
"""
Multi-threading example using publishsub library
Demonstrates thread-safe event handling across multiple threads
"""

import publishsub as pubsub
import threading
import time
import random
import queue

class TaskManager:
    def __init__(self):
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.active_workers = 0
        self.task_queue = queue.Queue()
        self.results = []
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Setup task management event handlers"""
        pubsub.subscribe("worker_start", self.on_worker_start)
        pubsub.subscribe("worker_stop", self.on_worker_stop)
        pubsub.subscribe("task_start", self.on_task_start)
        pubsub.subscribe("task_complete", self.on_task_complete)
        pubsub.subscribe("task_error", self.on_task_error)
        pubsub.subscribe("progress_update", self.on_progress_update)
    
    def on_worker_start(self, data):
        self.active_workers += 1
        worker_id = data['worker_id']
        print(f"🟢 Worker {worker_id} started (Active: {self.active_workers})")
    
    def on_worker_stop(self, data):
        self.active_workers -= 1
        worker_id = data['worker_id']
        tasks_completed = data.get('tasks_completed', 0)
        print(f"🔴 Worker {worker_id} stopped after {tasks_completed} tasks (Active: {self.active_workers})")
    
    def on_task_start(self, data):
        task_id = data['task_id']
        worker_id = data['worker_id']
        print(f"⚙️  Task {task_id} started by worker {worker_id}")
    
    def on_task_complete(self, data):
        self.completed_tasks += 1
        task_id = data['task_id']
        worker_id = data['worker_id']
        result = data.get('result')
        duration = data.get('duration', 0)
        
        self.results.append({
            'task_id': task_id,
            'worker_id': worker_id,
            'result': result,
            'duration': duration
        })
        
        print(f"✅ Task {task_id} completed by worker {worker_id} in {duration:.2f}s")
        print(f"   Result: {result}")
        print(f"   Total completed: {self.completed_tasks}")
    
    def on_task_error(self, data):
        self.failed_tasks += 1
        task_id = data['task_id']
        worker_id = data['worker_id']
        error = data['error']
        
        print(f"❌ Task {task_id} failed in worker {worker_id}: {error}")
        print(f"   Total failed: {self.failed_tasks}")
    
    def on_progress_update(self, data):
        task_id = data['task_id']
        worker_id = data['worker_id']
        progress = data['progress']
        
        print(f"📊 Task {task_id} progress: {progress}% (Worker {worker_id})")
    
    def get_stats(self):
        return {
            'completed': self.completed_tasks,
            'failed': self.failed_tasks,
            'active_workers': self.active_workers,
            'total_results': len(self.results)
        }

class Worker(threading.Thread):
    def __init__(self, worker_id, task_list):
        super().__init__()
        self.worker_id = worker_id
        self.task_list = task_list
        self.tasks_completed = 0
        self.running = True
    
    def run(self):
        """Worker thread main loop"""
        pubsub.publish("worker_start", {"worker_id": self.worker_id})
        
        try:
            for task in self.task_list:
                if not self.running:
                    break
                
                self.process_task(task)
                self.tasks_completed += 1
                
                # Small delay between tasks
                time.sleep(random.uniform(0.1, 0.3))
        
        except Exception as e:
            print(f"💥 Worker {self.worker_id} crashed: {e}")
        
        finally:
            pubsub.publish("worker_stop", {
                "worker_id": self.worker_id,
                "tasks_completed": self.tasks_completed
            })
    
    def process_task(self, task):
        """Process a single task"""
        task_id = task['id']
        task_type = task['type']
        task_data = task.get('data', {})
        
        pubsub.publish("task_start", {
            "task_id": task_id,
            "worker_id": self.worker_id
        })
        
        try:
            start_time = time.time()
            
            # Simulate different types of work
            if task_type == "calculation":
                result = self.do_calculation(task_data)
            elif task_type == "data_processing":
                result = self.process_data(task_data)
            elif task_type == "network_request":
                result = self.simulate_network_request(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            duration = time.time() - start_time
            
            # Publish successful completion
            pubsub.publish("task_complete", {
                "task_id": task_id,
                "worker_id": self.worker_id,
                "result": result,
                "duration": duration
            })
            
        except Exception as e:
            # Publish error
            pubsub.publish("task_error", {
                "task_id": task_id,
                "worker_id": self.worker_id,
                "error": str(e)
            })
    
    def do_calculation(self, data):
        """Simulate mathematical calculation"""
        numbers = data.get('numbers', [1, 2, 3, 4, 5])
        operation = data.get('operation', 'sum')
        
        # Simulate progress updates
        for i in range(0, 101, 25):
            pubsub.publish("progress_update", {
                "task_id": data.get('task_id'),
                "worker_id": self.worker_id,
                "progress": i
            })
            time.sleep(0.1)
        
        if operation == 'sum':
            return sum(numbers)
        elif operation == 'product':
            result = 1
            for num in numbers:
                result *= num
            return result
        elif operation == 'average':
            return sum(numbers) / len(numbers)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def process_data(self, data):
        """Simulate data processing"""
        items = data.get('items', [])
        processing_type = data.get('type', 'count')
        
        time.sleep(random.uniform(0.2, 0.8))  # Simulate processing time
        
        if processing_type == 'count':
            return len(items)
        elif processing_type == 'filter':
            return [item for item in items if item % 2 == 0]
        elif processing_type == 'transform':
            return [item * 2 for item in items]
        else:
            raise ValueError(f"Unknown processing type: {processing_type}")
    
    def simulate_network_request(self, data):
        """Simulate network request"""
        url = data.get('url', 'https://api.example.com')
        method = data.get('method', 'GET')
        
        # Simulate network delay
        delay = random.uniform(0.3, 1.5)
        time.sleep(delay)
        
        # Simulate occasional failures
        if random.random() < 0.1:  # 10% failure rate
            raise Exception(f"Network timeout for {url}")
        
        return {
            'url': url,
            'method': method,
            'status': 200,
            'response_time': delay,
            'data': f"Response from {url}"
        }
    
    def stop(self):
        """Stop the worker"""
        self.running = False

def create_sample_tasks():
    """Create sample tasks for workers"""
    tasks = []
    
    # Calculation tasks
    for i in range(5):
        tasks.append({
            'id': f"calc_{i}",
            'type': 'calculation',
            'data': {
                'numbers': [random.randint(1, 100) for _ in range(10)],
                'operation': random.choice(['sum', 'product', 'average'])
            }
        })
    
    # Data processing tasks
    for i in range(3):
        tasks.append({
            'id': f"data_{i}",
            'type': 'data_processing',
            'data': {
                'items': [random.randint(1, 50) for _ in range(20)],
                'type': random.choice(['count', 'filter', 'transform'])
            }
        })
    
    # Network tasks
    for i in range(4):
        tasks.append({
            'id': f"net_{i}",
            'type': 'network_request',
            'data': {
                'url': f'https://api.service{i}.com/data',
                'method': random.choice(['GET', 'POST'])
            }
        })
    
    return tasks

def simulate_multithreaded_processing():
    """Simulate multithreaded task processing"""
    print("=== Multi-threaded Processing with publishsub ===\n")
    
    # Create task manager
    task_manager = TaskManager()
    
    # Create sample tasks
    all_tasks = create_sample_tasks()
    print(f"📋 Created {len(all_tasks)} tasks")
    
    # Distribute tasks among workers
    num_workers = 3
    tasks_per_worker = len(all_tasks) // num_workers
    
    workers = []
    for i in range(num_workers):
        start_idx = i * tasks_per_worker
        end_idx = start_idx + tasks_per_worker
        if i == num_workers - 1:  # Last worker gets remaining tasks
            end_idx = len(all_tasks)
        
        worker_tasks = all_tasks[start_idx:end_idx]
        worker = Worker(f"W{i+1}", worker_tasks)
        workers.append(worker)
        print(f"👷 Worker W{i+1} assigned {len(worker_tasks)} tasks")
    
    print(f"\n🚀 Starting {num_workers} workers...")
    print("=" * 50)
    
    # Start all workers
    for worker in workers:
        worker.start()
    
    # Wait for all workers to complete
    for worker in workers:
        worker.join()
    
    print("\n" + "=" * 50)
    print("🏁 All workers completed!")
    
    # Show final statistics
    stats = task_manager.get_stats()
    print(f"\n📊 Final Statistics:")
    print(f"   ✅ Completed tasks: {stats['completed']}")
    print(f"   ❌ Failed tasks: {stats['failed']}")
    print(f"   🔴 Active workers: {stats['active_workers']}")
    print(f"   📈 Total results: {stats['total_results']}")
    
    # Show some results
    if task_manager.results:
        print(f"\n🎯 Sample Results:")
        for result in task_manager.results[:3]:  # Show first 3 results
            print(f"   Task {result['task_id']}: {result['result']} ({result['duration']:.2f}s)")
    
    print("\n=== Multi-threaded Processing Complete ===")

if __name__ == "__main__":
    simulate_multithreaded_processing()