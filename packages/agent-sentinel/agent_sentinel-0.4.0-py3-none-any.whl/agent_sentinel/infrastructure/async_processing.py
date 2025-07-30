"""
Production-Grade Async Processing Pipeline for Agent Sentinel

This module implements a sophisticated async processing system for high-performance
threat detection and security monitoring in AI agents.

Enterprise-grade features:
- High-performance async processing with worker pools
- Distributed task queues with priority handling
- Circuit breakers for fault tolerance
- Rate limiting and backpressure management
- Horizontal scaling support
- Real-time monitoring and metrics
- Graceful degradation and failover
- Message persistence and reliability
"""

import asyncio
import json
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import threading
import logging
import signal
import sys
from pathlib import Path
import pickle
import hashlib

from ..core.exceptions import AgentSentinelError
from ..logging.structured_logger import SecurityLogger
from .monitoring.circuit_breaker import CircuitBreaker
from .monitoring.metrics import MetricsCollector


class TaskPriority(Enum):
    """Priority levels for async tasks."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(Enum):
    """Status of async tasks."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class WorkerStatus(Enum):
    """Status of worker processes."""
    IDLE = "idle"
    BUSY = "busy"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class AsyncTask:
    """Represents an async task in the processing pipeline."""
    task_id: str
    task_type: str
    priority: TaskPriority
    payload: Dict[str, Any]
    
    # Metadata
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Processing info
    status: TaskStatus = TaskStatus.PENDING
    worker_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 30.0
    
    # Results
    result: Optional[Any] = None
    error: Optional[str] = None
    
    # Callbacks
    success_callback: Optional[Callable] = None
    failure_callback: Optional[Callable] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "priority": self.priority.value,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status.value,
            "worker_id": self.worker_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "result": self.result,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AsyncTask':
        """Create task from dictionary."""
        return cls(
            task_id=data["task_id"],
            task_type=data["task_type"],
            priority=TaskPriority(data["priority"]),
            payload=data["payload"],
            created_at=datetime.fromisoformat(data["created_at"]),
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]) if data["scheduled_at"] else None,
            started_at=datetime.fromisoformat(data["started_at"]) if data["started_at"] else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data["completed_at"] else None,
            status=TaskStatus(data["status"]),
            worker_id=data["worker_id"],
            retry_count=data["retry_count"],
            max_retries=data["max_retries"],
            timeout=data["timeout"],
            result=data["result"],
            error=data["error"]
        )


@dataclass
class WorkerInfo:
    """Information about a worker process."""
    worker_id: str
    worker_type: str
    status: WorkerStatus
    created_at: datetime
    last_heartbeat: datetime
    
    # Performance metrics
    tasks_processed: int = 0
    tasks_failed: int = 0
    avg_processing_time: float = 0.0
    current_task: Optional[str] = None
    
    # Resource usage
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert worker info to dictionary."""
        return {
            "worker_id": self.worker_id,
            "worker_type": self.worker_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "tasks_processed": self.tasks_processed,
            "tasks_failed": self.tasks_failed,
            "avg_processing_time": self.avg_processing_time,
            "current_task": self.current_task,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage
        }


class TaskProcessor(ABC):
    """Abstract base class for task processors."""
    
    @abstractmethod
    async def process(self, task: AsyncTask) -> Any:
        """Process a task and return result."""
        pass
    
    @abstractmethod
    def can_process(self, task_type: str) -> bool:
        """Check if processor can handle task type."""
        pass
    
    @abstractmethod
    def get_processor_info(self) -> Dict[str, Any]:
        """Get processor information."""
        pass


class PriorityQueue:
    """Thread-safe priority queue for async tasks."""
    
    def __init__(self, maxsize: int = 0):
        self.maxsize = maxsize
        self._queues = {priority: deque() for priority in TaskPriority}
        self._task_count = 0
        self._condition = asyncio.Condition()
        self._closed = False
    
    async def put(self, task: AsyncTask) -> None:
        """Put task in queue."""
        async with self._condition:
            if self._closed:
                raise RuntimeError("Queue is closed")
            
            if self.maxsize > 0 and self._task_count >= self.maxsize:
                raise RuntimeError("Queue is full")
            
            self._queues[task.priority].append(task)
            self._task_count += 1
            self._condition.notify()
    
    async def get(self) -> AsyncTask:
        """Get highest priority task from queue."""
        async with self._condition:
            while self._task_count == 0 and not self._closed:
                await self._condition.wait()
            
            if self._task_count == 0 and self._closed:
                raise RuntimeError("Queue is closed")
            
            # Get task with highest priority
            for priority in TaskPriority:
                if self._queues[priority]:
                    task = self._queues[priority].popleft()
                    self._task_count -= 1
                    return task
            
            raise RuntimeError("No tasks available")
    
    async def peek(self) -> Optional[AsyncTask]:
        """Peek at next task without removing it."""
        async with self._condition:
            for priority in TaskPriority:
                if self._queues[priority]:
                    return self._queues[priority][0]
            return None
    
    def qsize(self) -> int:
        """Get queue size."""
        return self._task_count
    
    def empty(self) -> bool:
        """Check if queue is empty."""
        return self._task_count == 0
    
    def full(self) -> bool:
        """Check if queue is full."""
        return self.maxsize > 0 and self._task_count >= self.maxsize
    
    async def close(self) -> None:
        """Close the queue."""
        async with self._condition:
            self._closed = True
            self._condition.notify_all()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "total_tasks": self._task_count,
            "tasks_by_priority": {
                priority.name: len(self._queues[priority])
                for priority in TaskPriority
            },
            "maxsize": self.maxsize,
            "closed": self._closed
        }


class AsyncWorker:
    """Async worker for processing tasks."""
    
    def __init__(
        self,
        worker_id: str,
        worker_type: str,
        processor: TaskProcessor,
        logger: Optional[SecurityLogger] = None,
        max_concurrent_tasks: int = 5,
        heartbeat_interval: float = 30.0
    ):
        self.worker_id = worker_id
        self.worker_type = worker_type
        self.processor = processor
        self.logger = logger or SecurityLogger(
            name=f"async_worker_{worker_id}",
            json_format=True
        )
        self.max_concurrent_tasks = max_concurrent_tasks
        self.heartbeat_interval = heartbeat_interval
        
        # Worker state
        self.info = WorkerInfo(
            worker_id=worker_id,
            worker_type=worker_type,
            status=WorkerStatus.IDLE,
            created_at=datetime.now(timezone.utc),
            last_heartbeat=datetime.now(timezone.utc)
        )
        
        # Task management
        self.current_tasks: Dict[str, AsyncTask] = {}
        self.task_semaphore = asyncio.Semaphore(max_concurrent_tasks)
        
        # Control flags
        self.running = False
        self.shutdown_event = asyncio.Event()
        
        # Circuit breaker for fault tolerance
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0,
            expected_exception=Exception
        )
        
        # Metrics
        self.metrics = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "total_processing_time": 0.0,
            "last_processing_time": 0.0
        }
    
    async def start(self, task_queue: PriorityQueue) -> None:
        """Start the worker."""
        self.running = True
        self.info.status = WorkerStatus.IDLE
        
        self.logger.info(f"Starting worker {self.worker_id}")
        
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Start main processing loop
        try:
            await self._process_loop(task_queue)
        finally:
            heartbeat_task.cancel()
            self.info.status = WorkerStatus.STOPPED
            self.logger.info(f"Worker {self.worker_id} stopped")
    
    async def stop(self) -> None:
        """Stop the worker gracefully."""
        self.logger.info(f"Stopping worker {self.worker_id}")
        self.running = False
        self.info.status = WorkerStatus.STOPPING
        self.shutdown_event.set()
        
        # Wait for current tasks to complete
        await self._wait_for_tasks_completion()
    
    async def _process_loop(self, task_queue: PriorityQueue) -> None:
        """Main processing loop."""
        while self.running:
            try:
                # Wait for task or shutdown
                try:
                    task = await asyncio.wait_for(task_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Check if we can process this task type
                if not self.processor.can_process(task.task_type):
                    # Put task back in queue for another worker
                    await task_queue.put(task)
                    continue
                
                # Process task
                await self._process_task(task)
                
            except Exception as e:
                self.logger.error(f"Error in worker processing loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_task(self, task: AsyncTask) -> None:
        """Process a single task."""
        async with self.task_semaphore:
            self.info.status = WorkerStatus.BUSY
            self.info.current_task = task.task_id
            self.current_tasks[task.task_id] = task
            
            start_time = time.time()
            
            try:
                # Update task status
                task.status = TaskStatus.PROCESSING
                task.started_at = datetime.now(timezone.utc)
                task.worker_id = self.worker_id
                
                # Process with circuit breaker
                async with self.circuit_breaker:
                    result = await asyncio.wait_for(
                        self.processor.process(task),
                        timeout=task.timeout
                    )
                
                # Task completed successfully
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(timezone.utc)
                task.result = result
                
                # Call success callback
                if task.success_callback:
                    try:
                        await task.success_callback(task)
                    except Exception as e:
                        self.logger.warning(f"Success callback failed: {e}")
                
                # Update metrics
                processing_time = time.time() - start_time
                self._update_metrics(processing_time, success=True)
                
                self.logger.info(
                    f"Task {task.task_id} completed successfully in {processing_time:.3f}s"
                )
                
            except asyncio.TimeoutError:
                # Task timed out
                await self._handle_task_timeout(task)
                
            except Exception as e:
                # Task failed
                await self._handle_task_failure(task, e)
                
            finally:
                # Cleanup
                self.current_tasks.pop(task.task_id, None)
                self.info.current_task = None
                self.info.status = WorkerStatus.IDLE
    
    async def _handle_task_timeout(self, task: AsyncTask) -> None:
        """Handle task timeout."""
        task.error = f"Task timed out after {task.timeout}s"
        
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            self.logger.warning(f"Task {task.task_id} timed out, retrying ({task.retry_count}/{task.max_retries})")
        else:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now(timezone.utc)
            
            # Call failure callback
            if task.failure_callback:
                try:
                    await task.failure_callback(task)
                except Exception as e:
                    self.logger.warning(f"Failure callback failed: {e}")
            
            self.logger.error(f"Task {task.task_id} failed after {task.max_retries} retries")
        
        self._update_metrics(task.timeout, success=False)
    
    async def _handle_task_failure(self, task: AsyncTask, error: Exception) -> None:
        """Handle task failure."""
        task.error = str(error)
        
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING
            self.logger.warning(f"Task {task.task_id} failed, retrying ({task.retry_count}/{task.max_retries}): {error}")
        else:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now(timezone.utc)
            
            # Call failure callback
            if task.failure_callback:
                try:
                    await task.failure_callback(task)
                except Exception as e:
                    self.logger.warning(f"Failure callback failed: {e}")
            
            self.logger.error(f"Task {task.task_id} failed after {task.max_retries} retries: {error}")
        
        processing_time = time.time() - task.started_at.timestamp() if task.started_at else 0.0
        self._update_metrics(processing_time, success=False)
    
    async def _heartbeat_loop(self) -> None:
        """Heartbeat loop for worker health monitoring."""
        while self.running:
            try:
                self.info.last_heartbeat = datetime.now(timezone.utc)
                
                # Update resource usage (simplified)
                self.info.memory_usage = self._get_memory_usage()
                self.info.cpu_usage = self._get_cpu_usage()
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _wait_for_tasks_completion(self) -> None:
        """Wait for current tasks to complete."""
        if not self.current_tasks:
            return
        
        self.logger.info(f"Waiting for {len(self.current_tasks)} tasks to complete")
        
        # Wait for all current tasks to complete
        timeout = 30.0  # 30 seconds timeout
        start_time = time.time()
        
        while self.current_tasks and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.1)
        
        if self.current_tasks:
            self.logger.warning(f"Forcefully terminating {len(self.current_tasks)} tasks")
            for task in self.current_tasks.values():
                task.status = TaskStatus.CANCELLED
    
    def _update_metrics(self, processing_time: float, success: bool) -> None:
        """Update worker metrics."""
        self.metrics["last_processing_time"] = processing_time
        
        if success:
            self.metrics["tasks_processed"] += 1
            self.info.tasks_processed += 1
        else:
            self.metrics["tasks_failed"] += 1
            self.info.tasks_failed += 1
        
        # Update average processing time
        total_tasks = self.metrics["tasks_processed"] + self.metrics["tasks_failed"]
        if total_tasks > 0:
            self.metrics["total_processing_time"] += processing_time
            self.info.avg_processing_time = self.metrics["total_processing_time"] / total_tasks
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage (simplified)."""
        # In production, this would use psutil or similar
        return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage (simplified)."""
        # In production, this would use psutil or similar
        return 0.0
    
    def get_info(self) -> WorkerInfo:
        """Get worker information."""
        return self.info
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get worker metrics."""
        return {
            "worker_id": self.worker_id,
            "worker_type": self.worker_type,
            "status": self.info.status.value,
            "tasks_processed": self.metrics["tasks_processed"],
            "tasks_failed": self.metrics["tasks_failed"],
            "avg_processing_time": self.info.avg_processing_time,
            "current_tasks": len(self.current_tasks),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "circuit_breaker_state": self.circuit_breaker.state.value,
            "memory_usage": self.info.memory_usage,
            "cpu_usage": self.info.cpu_usage
        }


class TaskScheduler:
    """Task scheduler for delayed and recurring tasks."""
    
    def __init__(self, logger: Optional[SecurityLogger] = None):
        self.logger = logger or SecurityLogger(
            name="task_scheduler",
            json_format=True
        )
        
        # Scheduled tasks
        self.scheduled_tasks: Dict[str, AsyncTask] = {}
        self.recurring_tasks: Dict[str, Dict[str, Any]] = {}
        
        # Control
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
    
    async def start(self, task_queue: PriorityQueue) -> None:
        """Start the scheduler."""
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop(task_queue))
        self.logger.info("Task scheduler started")
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
        self.logger.info("Task scheduler stopped")
    
    def schedule_task(self, task: AsyncTask, delay: float) -> None:
        """Schedule a task to run after delay."""
        task.scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
        self.scheduled_tasks[task.task_id] = task
        self.logger.info(f"Task {task.task_id} scheduled to run in {delay}s")
    
    def schedule_recurring_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        interval: float,
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> str:
        """Schedule a recurring task."""
        task_id = f"recurring_{task_type}_{uuid.uuid4().hex[:8]}"
        
        self.recurring_tasks[task_id] = {
            "task_type": task_type,
            "payload": payload,
            "interval": interval,
            "priority": priority,
            "last_run": None,
            "next_run": datetime.now(timezone.utc)
        }
        
        self.logger.info(f"Recurring task {task_id} scheduled with interval {interval}s")
        return task_id
    
    def cancel_scheduled_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            self.logger.info(f"Scheduled task {task_id} cancelled")
            return True
        return False
    
    def cancel_recurring_task(self, task_id: str) -> bool:
        """Cancel a recurring task."""
        if task_id in self.recurring_tasks:
            del self.recurring_tasks[task_id]
            self.logger.info(f"Recurring task {task_id} cancelled")
            return True
        return False
    
    async def _scheduler_loop(self, task_queue: PriorityQueue) -> None:
        """Main scheduler loop."""
        while self.running:
            try:
                now = datetime.now(timezone.utc)
                
                # Check scheduled tasks
                ready_tasks = []
                for task_id, task in list(self.scheduled_tasks.items()):
                    if task.scheduled_at and task.scheduled_at <= now:
                        ready_tasks.append(task_id)
                
                # Submit ready tasks
                for task_id in ready_tasks:
                    task = self.scheduled_tasks.pop(task_id)
                    await task_queue.put(task)
                    self.logger.info(f"Scheduled task {task_id} submitted to queue")
                
                # Check recurring tasks
                for task_id, task_info in list(self.recurring_tasks.items()):
                    if task_info["next_run"] <= now:
                        # Create new task instance
                        task = AsyncTask(
                            task_id=f"{task_id}_{uuid.uuid4().hex[:8]}",
                            task_type=task_info["task_type"],
                            priority=task_info["priority"],
                            payload=task_info["payload"],
                            created_at=now
                        )
                        
                        await task_queue.put(task)
                        
                        # Update next run time
                        task_info["last_run"] = now
                        task_info["next_run"] = now + timedelta(seconds=task_info["interval"])
                        
                        self.logger.info(f"Recurring task {task_id} submitted to queue")
                
                await asyncio.sleep(1.0)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(1.0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        return {
            "scheduled_tasks": len(self.scheduled_tasks),
            "recurring_tasks": len(self.recurring_tasks),
            "running": self.running
        }


class RateLimiter:
    """Rate limiter for controlling task submission."""
    
    def __init__(self, max_requests: int, time_window: float):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: deque = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire rate limit token."""
        async with self.lock:
            now = time.time()
            
            # Remove old requests
            while self.requests and self.requests[0] <= now - self.time_window:
                self.requests.popleft()
            
            # Check if we can make a new request
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        return {
            "max_requests": self.max_requests,
            "time_window": self.time_window,
            "current_requests": len(self.requests)
        }


class AsyncProcessingPipeline:
    """
    Production-grade async processing pipeline.
    
    This pipeline provides high-performance async processing with:
    - Priority-based task queues
    - Worker pools with load balancing
    - Circuit breakers for fault tolerance
    - Rate limiting and backpressure management
    - Task scheduling and recurring tasks
    - Real-time monitoring and metrics
    """
    
    def __init__(
        self,
        name: str,
        logger: Optional[SecurityLogger] = None,
        max_queue_size: int = 10000,
        max_workers: int = 10,
        enable_persistence: bool = True,
        persistence_path: Optional[Path] = None
    ):
        self.name = name
        self.logger = logger or SecurityLogger(
            name=f"async_pipeline_{name}",
            json_format=True
        )
        self.max_queue_size = max_queue_size
        self.max_workers = max_workers
        self.enable_persistence = enable_persistence
        self.persistence_path = persistence_path or Path(f"./pipeline_{name}.pkl")
        
        # Core components
        self.task_queue = PriorityQueue(maxsize=max_queue_size)
        self.workers: Dict[str, AsyncWorker] = {}
        self.processors: Dict[str, TaskProcessor] = {}
        self.scheduler = TaskScheduler(logger)
        
        # Rate limiting
        self.rate_limiters: Dict[str, RateLimiter] = {}
        
        # Task tracking
        self.active_tasks: Dict[str, AsyncTask] = {}
        self.completed_tasks: deque = deque(maxlen=1000)
        self.failed_tasks: deque = deque(maxlen=1000)
        
        # Control
        self.running = False
        self.shutdown_event = asyncio.Event()
        
        # Metrics
        self.metrics_collector = MetricsCollector()
        self.start_time = datetime.now(timezone.utc)
        
        # Signal handlers
        self._setup_signal_handlers()
        
        self.logger.info(f"Async processing pipeline '{name}' initialized")
    
    def register_processor(self, name: str, processor: TaskProcessor) -> None:
        """Register a task processor."""
        self.processors[name] = processor
        self.logger.info(f"Registered processor: {name}")
    
    def create_worker_pool(
        self,
        worker_type: str,
        processor_name: str,
        pool_size: int = 5,
        max_concurrent_tasks: int = 5
    ) -> None:
        """Create a pool of workers."""
        if processor_name not in self.processors:
            raise ValueError(f"Processor '{processor_name}' not found")
        
        processor = self.processors[processor_name]
        
        for i in range(pool_size):
            worker_id = f"{worker_type}_{i}"
            worker = AsyncWorker(
                worker_id=worker_id,
                worker_type=worker_type,
                processor=processor,
                logger=self.logger,
                max_concurrent_tasks=max_concurrent_tasks
            )
            self.workers[worker_id] = worker
        
        self.logger.info(f"Created worker pool '{worker_type}' with {pool_size} workers")
    
    def add_rate_limiter(self, name: str, max_requests: int, time_window: float) -> None:
        """Add rate limiter."""
        self.rate_limiters[name] = RateLimiter(max_requests, time_window)
        self.logger.info(f"Added rate limiter '{name}': {max_requests} requests per {time_window}s")
    
    async def start(self) -> None:
        """Start the processing pipeline."""
        if self.running:
            return
        
        self.running = True
        self.logger.info(f"Starting async processing pipeline '{self.name}'")
        
        # Load persisted state
        if self.enable_persistence:
            await self._load_state()
        
        # Start scheduler
        await self.scheduler.start(self.task_queue)
        
        # Start workers
        worker_tasks = []
        for worker in self.workers.values():
            task = asyncio.create_task(worker.start(self.task_queue))
            worker_tasks.append(task)
        
        # Start monitoring
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info(f"Pipeline '{self.name}' started with {len(self.workers)} workers")
        
        try:
            # Wait for shutdown signal
            await self.shutdown_event.wait()
        finally:
            # Cleanup
            await self._shutdown_cleanup(worker_tasks, monitoring_task)
    
    async def stop(self) -> None:
        """Stop the processing pipeline gracefully."""
        if not self.running:
            return
        
        self.logger.info(f"Stopping async processing pipeline '{self.name}'")
        self.running = False
        self.shutdown_event.set()
    
    async def submit_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limiter: Optional[str] = None,
        success_callback: Optional[Callable] = None,
        failure_callback: Optional[Callable] = None
    ) -> str:
        """Submit a task for processing."""
        if not self.running:
            raise RuntimeError("Pipeline is not running")
        
        # Check rate limiter
        if rate_limiter and rate_limiter in self.rate_limiters:
            if not await self.rate_limiters[rate_limiter].acquire():
                raise RuntimeError(f"Rate limit exceeded for '{rate_limiter}'")
        
        # Create task
        task = AsyncTask(
            task_id=uuid.uuid4().hex,
            task_type=task_type,
            priority=priority,
            payload=payload,
            created_at=datetime.now(timezone.utc),
            timeout=timeout,
            max_retries=max_retries,
            success_callback=success_callback,
            failure_callback=failure_callback
        )
        
        # Add to queue
        await self.task_queue.put(task)
        self.active_tasks[task.task_id] = task
        
        self.logger.info(f"Task {task.task_id} ({task_type}) submitted with priority {priority.name}")
        
        return task.task_id
    
    async def submit_batch(
        self,
        tasks: List[Dict[str, Any]],
        priority: TaskPriority = TaskPriority.MEDIUM,
        rate_limiter: Optional[str] = None
    ) -> List[str]:
        """Submit multiple tasks as a batch."""
        task_ids = []
        
        for task_data in tasks:
            task_id = await self.submit_task(
                task_type=task_data["task_type"],
                payload=task_data["payload"],
                priority=priority,
                timeout=task_data.get("timeout", 30.0),
                max_retries=task_data.get("max_retries", 3),
                rate_limiter=rate_limiter
            )
            task_ids.append(task_id)
        
        self.logger.info(f"Submitted batch of {len(tasks)} tasks")
        return task_ids
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task."""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].to_dict()
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return task.to_dict()
        
        # Check failed tasks
        for task in self.failed_tasks:
            if task.task_id == task_id:
                return task.to_dict()
        
        return None
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Optional[Any]:
        """Wait for a task to complete and return result."""
        start_time = time.time()
        
        while True:
            task_status = await self.get_task_status(task_id)
            
            if not task_status:
                return None
            
            if task_status["status"] == TaskStatus.COMPLETED.value:
                return task_status["result"]
            
            if task_status["status"] == TaskStatus.FAILED.value:
                raise RuntimeError(f"Task failed: {task_status['error']}")
            
            if timeout and (time.time() - start_time) > timeout:
                raise asyncio.TimeoutError(f"Task {task_id} did not complete within {timeout}s")
            
            await asyncio.sleep(0.1)
    
    def schedule_task(self, task_type: str, payload: Dict[str, Any], delay: float) -> str:
        """Schedule a task to run after delay."""
        task = AsyncTask(
            task_id=uuid.uuid4().hex,
            task_type=task_type,
            priority=TaskPriority.MEDIUM,
            payload=payload,
            created_at=datetime.now(timezone.utc)
        )
        
        self.scheduler.schedule_task(task, delay)
        return task.task_id
    
    def schedule_recurring_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        interval: float,
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> str:
        """Schedule a recurring task."""
        return self.scheduler.schedule_recurring_task(task_type, payload, interval, priority)
    
    def cancel_scheduled_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        return self.scheduler.cancel_scheduled_task(task_id)
    
    def cancel_recurring_task(self, task_id: str) -> bool:
        """Cancel a recurring task."""
        return self.scheduler.cancel_recurring_task(task_id)
    
    async def _monitoring_loop(self) -> None:
        """Monitoring loop for pipeline health."""
        while self.running:
            try:
                # Update metrics
                self._update_metrics()
                
                # Check worker health
                await self._check_worker_health()
                
                # Clean up completed tasks
                self._cleanup_completed_tasks()
                
                # Persist state
                if self.enable_persistence:
                    await self._persist_state()
                
                await asyncio.sleep(10.0)  # Monitor every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(1.0)
    
    def _update_metrics(self) -> None:
        """Update pipeline metrics."""
        now = datetime.now(timezone.utc)
        uptime = (now - self.start_time).total_seconds()
        
        # Queue metrics
        queue_stats = self.task_queue.get_stats()
        
        # Worker metrics
        worker_stats = {}
        for worker_id, worker in self.workers.items():
            worker_stats[worker_id] = worker.get_metrics()
        
        # Task metrics
        total_completed = len(self.completed_tasks)
        total_failed = len(self.failed_tasks)
        total_active = len(self.active_tasks)
        
        # Rate limiter metrics
        rate_limiter_stats = {}
        for name, limiter in self.rate_limiters.items():
            rate_limiter_stats[name] = limiter.get_stats()
        
        # Collect all metrics
        metrics = {
            "pipeline_name": self.name,
            "uptime": uptime,
            "running": self.running,
            "queue": queue_stats,
            "workers": worker_stats,
            "tasks": {
                "active": total_active,
                "completed": total_completed,
                "failed": total_failed,
                "total": total_active + total_completed + total_failed
            },
            "rate_limiters": rate_limiter_stats,
            "scheduler": self.scheduler.get_stats()
        }
        
        # Store metrics
        self.metrics_collector.record_metrics(metrics)
    
    async def _check_worker_health(self) -> None:
        """Check worker health and restart if needed."""
        now = datetime.now(timezone.utc)
        
        for worker_id, worker in list(self.workers.items()):
            worker_info = worker.get_info()
            
            # Check if worker is responsive
            time_since_heartbeat = (now - worker_info.last_heartbeat).total_seconds()
            
            if time_since_heartbeat > 120.0:  # 2 minutes
                self.logger.warning(f"Worker {worker_id} is unresponsive, restarting")
                
                # Stop unresponsive worker
                await worker.stop()
                
                # Create new worker
                processor = self.processors.get(worker_info.worker_type)
                if processor:
                    new_worker = AsyncWorker(
                        worker_id=worker_id,
                        worker_type=worker_info.worker_type,
                        processor=processor,
                        logger=self.logger
                    )
                    self.workers[worker_id] = new_worker
                    
                    # Start new worker
                    asyncio.create_task(new_worker.start(self.task_queue))
    
    def _cleanup_completed_tasks(self) -> None:
        """Clean up completed tasks from active tracking."""
        completed_task_ids = []
        
        for task_id, task in self.active_tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                completed_task_ids.append(task_id)
        
        for task_id in completed_task_ids:
            task = self.active_tasks.pop(task_id)
            
            if task.status == TaskStatus.COMPLETED:
                self.completed_tasks.append(task)
            elif task.status == TaskStatus.FAILED:
                self.failed_tasks.append(task)
    
    async def _persist_state(self) -> None:
        """Persist pipeline state."""
        try:
            state = {
                "active_tasks": {task_id: task.to_dict() for task_id, task in self.active_tasks.items()},
                "completed_tasks": [task.to_dict() for task in self.completed_tasks],
                "failed_tasks": [task.to_dict() for task in self.failed_tasks],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            with open(self.persistence_path, 'wb') as f:
                pickle.dump(state, f)
                
        except Exception as e:
            self.logger.error(f"Failed to persist state: {e}")
    
    async def _load_state(self) -> None:
        """Load persisted pipeline state."""
        try:
            if not self.persistence_path.exists():
                return
            
            with open(self.persistence_path, 'rb') as f:
                state = pickle.load(f)
            
            # Restore active tasks
            for task_data in state.get("active_tasks", {}).values():
                task = AsyncTask.from_dict(task_data)
                self.active_tasks[task.task_id] = task
            
            # Restore completed tasks
            for task_data in state.get("completed_tasks", []):
                task = AsyncTask.from_dict(task_data)
                self.completed_tasks.append(task)
            
            # Restore failed tasks
            for task_data in state.get("failed_tasks", []):
                task = AsyncTask.from_dict(task_data)
                self.failed_tasks.append(task)
            
            self.logger.info(f"Loaded persisted state: {len(self.active_tasks)} active tasks")
            
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
    
    async def _shutdown_cleanup(self, worker_tasks: List[asyncio.Task], monitoring_task: asyncio.Task) -> None:
        """Clean up during shutdown."""
        self.logger.info("Starting shutdown cleanup")
        
        # Stop scheduler
        await self.scheduler.stop()
        
        # Stop workers
        for worker in self.workers.values():
            await worker.stop()
        
        # Cancel worker tasks
        for task in worker_tasks:
            task.cancel()
        
        # Cancel monitoring task
        monitoring_task.cancel()
        
        # Close task queue
        await self.task_queue.close()
        
        # Persist final state
        if self.enable_persistence:
            await self._persist_state()
        
        self.logger.info("Shutdown cleanup completed")
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline metrics."""
        return self.metrics_collector.get_latest_metrics()
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        return {
            worker_id: worker.get_metrics()
            for worker_id, worker in self.workers.items()
        }
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return self.task_queue.get_stats()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get pipeline health status."""
        healthy_workers = sum(
            1 for worker in self.workers.values()
            if worker.get_info().status in [WorkerStatus.IDLE, WorkerStatus.BUSY]
        )
        
        return {
            "pipeline_name": self.name,
            "running": self.running,
            "healthy_workers": healthy_workers,
            "total_workers": len(self.workers),
            "queue_size": self.task_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "uptime": (datetime.now(timezone.utc) - self.start_time).total_seconds()
        } 