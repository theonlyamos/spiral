from typing import Optional
import asyncio

class Task:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.task = None

    async def start(self):
        self.task = asyncio.create_task(self.func(*self.args, **self.kwargs))

    async def join(self):
        if self.task:
            await self.task
        else:
            print("Task not started yet")

    async def cancel(self):
        if self.task:
            self.task.cancel()
        else:
            print("Task not started yet")

class Agent:
    
    # existing Agent code

    task: Optional[Task] = None

    def start_task(self, func, *args, **kwargs):
        self.task = Task(func, *args, **kwargs)

    async def run_task(self):
        if self.task:
            await self.task.start()
        else:
            print("No task set")

    async def stop_task(self):
        if self.task:
            await self.task.cancel()
        else:
            print("No task running")

    async def wait_task(self):
        if self.task:
            await self.task.join()
        else:
            print("No task set")
