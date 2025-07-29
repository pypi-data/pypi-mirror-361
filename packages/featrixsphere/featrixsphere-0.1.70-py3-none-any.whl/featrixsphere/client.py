#!/usr/bin/env python3
"""
Featrix Sphere API Client

A simple Python client for testing the Featrix Sphere API endpoints,
with a focus on the new single predictor functionality.
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import gzip
import os
import random
import ssl
from urllib3.exceptions import SSLError as Urllib3SSLError
import base64
import hashlib
import numpy as np
import matplotlib.pyplot as plt


@dataclass
class SessionInfo:
    """Container for session information."""
    session_id: str
    session_type: str
    status: str
    jobs: Dict[str, Any]
    job_queue_positions: Dict[str, Any]


class PredictionBatch:
    """
    Cached prediction batch that allows instant lookups after initial batch processing.
    
    Usage:
        # First run - populate cache
        batch = client.predict_batch(session_id, records)
        
        # Second run - instant cache lookups
        for i in values1:
            for j in values2:
                record = {"param1": i, "param2": j}
                result = batch.predict(record)  # Instant!
    """
    
    def __init__(self, session_id: str, client: 'FeatrixSphereClient', target_column: str = None):
        self.session_id = session_id
        self.client = client
        self.target_column = target_column
        self._cache = {}  # record_hash -> prediction_result
        self._stats = {'hits': 0, 'misses': 0, 'populated': 0}
        
    def _hash_record(self, record: Dict[str, Any]) -> str:
        """Create a stable hash for a record to use as cache key."""
        # Sort keys for consistent hashing
        sorted_items = sorted(record.items())
        record_str = json.dumps(sorted_items, sort_keys=True)
        return hashlib.md5(record_str.encode()).hexdigest()
    
    def predict(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get prediction for a record from cache, or return cache miss info.
        
        Args:
            record: Record dictionary to predict
            
        Returns:
            Prediction result if cached, or cache miss information
        """
        record_hash = self._hash_record(record)
        
        if record_hash in self._cache:
            self._stats['hits'] += 1
            return self._cache[record_hash]
        else:
            self._stats['misses'] += 1
            return {
                'cache_miss': True,
                'record': record,
                'suggestion': 'Record not found in batch cache. Add to records list and recreate batch.'
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'populated_records': self._stats['populated'],
            'cache_hits': self._stats['hits'],
            'cache_misses': self._stats['misses'],
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }
    
    def _populate_cache(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Populate the cache with batch predictions."""
        if not records:
            return {'summary': {'total_records': 0, 'successful': 0, 'failed': 0}}
        
        print(f"🚀 Creating prediction batch for {len(records)} records...")
        
        # Use existing batch prediction system
        batch_results = self.client.predict_records(
            session_id=self.session_id,
            records=records,
            target_column=self.target_column,
            show_progress_bar=True
        )
        
        # Populate cache with results
        predictions = batch_results.get('predictions', [])
        successful = 0
        failed = 0
        
        for prediction in predictions:
            row_index = prediction.get('row_index', 0)
            if row_index < len(records):
                record = records[row_index]
                record_hash = self._hash_record(record)
                self._cache[record_hash] = prediction
                
                if prediction.get('prediction') is not None:
                    successful += 1
                else:
                    failed += 1
        
        self._stats['populated'] = len(self._cache)
        
        print(f"✅ Batch cache populated: {successful} successful, {failed} failed")
        print(f"💾 Cache ready for instant lookups with batch.predict(record)")
        
        return batch_results


class FeatrixSphereClient:
    """Client for interacting with the Featrix Sphere API."""
    
    def __init__(self, base_url: str = "https://sphere-api.featrix.com", 
                 default_max_retries: int = 5, 
                 default_timeout: int = 30,
                 retry_base_delay: float = 2.0,
                 retry_max_delay: float = 60.0):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API server
            default_max_retries: Default number of retries for failed requests
            default_timeout: Default timeout for requests in seconds
            retry_base_delay: Base delay for exponential backoff in seconds
            retry_max_delay: Maximum delay for exponential backoff in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        # Set a reasonable timeout
        self.session.timeout = default_timeout
        
        # Retry configuration
        self.default_max_retries = default_max_retries
        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay
        
        # Prediction queue and rate tracking
        self._prediction_queues = {}  # session_id -> list of queued records
        self._prediction_call_times = {}  # session_id -> list of recent call timestamps
        self._last_warning_time = {}  # session_id -> last warning timestamp
        self._rate_warning_threshold = 3  # calls per second
        self._warning_cooldown = 300  # 5 minutes in seconds
        
        # Prediction cache for predict_from_cache() functionality
        self._prediction_cache = {}  # session_id -> {record_hash: prediction_result}
        self._cache_mode = {}  # session_id -> 'populate' or 'fetch'
        self._cache_stats = {}  # session_id -> {hits: int, misses: int, populated: int}
    
    def _make_request(self, method: str, endpoint: str, max_retries: int = None, **kwargs) -> requests.Response:
        """
        Make an HTTP request with comprehensive error handling and retry logic.
        
        Retries on:
        - 500 Internal Server Error with connection patterns (server restarting)
        - 503 Service Unavailable
        - SSL/TLS errors  
        - Connection errors
        - Timeout errors
        - Other transient network errors
        """
        if max_retries is None:
            max_retries = self.default_max_retries
            
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
                
            except requests.exceptions.HTTPError as e:
                if e.response is not None:
                    status_code = e.response.status_code
                    response_text = e.response.text
                    
                    # Check for server restart patterns in 500 errors
                    is_server_restarting = False
                    if status_code == 500:
                        restart_patterns = [
                            'connection refused',
                            'failed to establish a new connection',
                            'httpconnectionpool',
                            'max retries exceeded',
                            'newconnectionerror',
                            'connection aborted',
                            'bad gateway',
                            'gateway timeout'
                        ]
                        response_lower = response_text.lower()
                        is_server_restarting = any(pattern in response_lower for pattern in restart_patterns)
                    
                    # Retry on 503 Service Unavailable or 500 with server restart patterns
                    if (status_code == 503 or (status_code == 500 and is_server_restarting)) and attempt < max_retries:
                        wait_time = self._calculate_backoff(attempt)
                        if status_code == 503:
                            print(f"503 Service Unavailable, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries + 1})")
                        else:
                            print(f"🔄 Server restarting (500 error), retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries + 1})")
                        time.sleep(wait_time)
                        continue
                
                # Re-raise for other status codes or final attempt
                print(f"API request failed: {method} {url}")
                print(f"HTTP Error: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response status: {e.response.status_code}")
                    print(f"Response body: {e.response.text[:500]}")
                raise
                    
            except (requests.exceptions.SSLError, ssl.SSLError, Urllib3SSLError) as e:
                # Retry on SSL/TLS errors (often transient)
                if attempt < max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    print(f"SSL/TLS error, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries + 1})")
                    print(f"SSL Error details: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"API request failed after {max_retries + 1} attempts: {method} {url}")
                    print(f"SSL Error: {e}")
                    raise
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # Retry on connection errors and timeouts
                if attempt < max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    error_type = "Connection" if isinstance(e, requests.exceptions.ConnectionError) else "Timeout"
                    print(f"{error_type} error, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries + 1})")
                    print(f"Error details: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"API request failed after {max_retries + 1} attempts: {method} {url}")
                    print(f"Connection/Timeout Error: {e}")
                    raise
                    
            except requests.exceptions.RequestException as e:
                # For other request exceptions, retry if they might be transient
                error_msg = str(e).lower()
                is_transient = any(keyword in error_msg for keyword in [
                    'temporary failure', 'name resolution', 'network', 'reset', 
                    'broken pipe', 'connection aborted', 'bad gateway', 'gateway timeout'
                ])
                
                if is_transient and attempt < max_retries:
                    wait_time = self._calculate_backoff(attempt)
                    print(f"Transient network error, retrying in {wait_time:.1f}s... (attempt {attempt + 1}/{max_retries + 1})")
                    print(f"Error details: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"API request failed: {method} {url}")
                    print(f"Request Error: {e}")
                    raise
    
    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff with jitter.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay time in seconds with jitter applied
        """
        # Exponential backoff: base_delay * (2 ^ attempt)
        delay = self.retry_base_delay * (2 ** attempt)
        
        # Cap at max_delay
        delay = min(delay, self.retry_max_delay)
        
        # Add jitter (±25% randomization)
        jitter = delay * 0.25 * (2 * random.random() - 1)
        
        return max(0.1, delay + jitter)  # Ensure minimum 0.1s delay
    
    def _track_prediction_call(self, session_id: str) -> bool:
        """
        Track prediction call rate and return True if warning should be shown.
        
        Args:
            session_id: Session ID to track
            
        Returns:
            True if rate warning should be displayed
        """
        current_time = time.time()
        
        # Initialize tracking for this session if needed
        if session_id not in self._prediction_call_times:
            self._prediction_call_times[session_id] = []
        
        # Add current call time
        self._prediction_call_times[session_id].append(current_time)
        
        # Keep only calls from the last second
        cutoff_time = current_time - 1.0
        self._prediction_call_times[session_id] = [
            t for t in self._prediction_call_times[session_id] if t > cutoff_time
        ]
        
        # Check if we're over the rate threshold
        call_count = len(self._prediction_call_times[session_id])
        if call_count > self._rate_warning_threshold:
            # Check if we should show warning (cooldown period)
            last_warning = self._last_warning_time.get(session_id, 0)
            if current_time - last_warning > self._warning_cooldown:
                self._last_warning_time[session_id] = current_time
                return True
        
        return False
    
    def _show_batching_warning(self, session_id: str, call_rate: float):
        """Show warning about using queue_batches for high-frequency predict() calls."""
        print("⚠️  " + "="*70)
        print("⚠️  HIGH-FREQUENCY PREDICTION DETECTED")
        print("⚠️  " + "="*70)
        print(f"📊 Current rate: {call_rate:.1f} predict() calls/second")
        print("🚀 For better performance, consider using queue_batches=True:")
        print()
        print("   # Instead of:")
        print("   for record in records:")
        print("       result = client.predict(session_id, record)")
        print()
        print("   # Use queued batching:")
        print("   for record in records:")
        print("       client.predict(session_id, record, queue_batches=True)")
        print("   results = client.flush_predict_queues(session_id)")
        print()
        print("💡 Benefits:")
        print("   • 5-20x faster for multiple predictions")
        print("   • Automatic batching with optimal chunk sizes")
        print("   • Maintains clean loop structure in your code")
        print("   • Reduces API overhead and server load")
        print()
        print("📚 See client documentation for more details.")
        print("⚠️  " + "="*70)
    
    def _add_to_prediction_queue(self, session_id: str, record: Dict[str, Any], 
                                target_column: str = None) -> str:
        """
        Add a record to the prediction queue.
        
        Args:
            session_id: Session ID
            record: Record to queue for prediction
            target_column: Target column for prediction
            
        Returns:
            Queue ID for this record
        """
        if session_id not in self._prediction_queues:
            self._prediction_queues[session_id] = []
        
        # Generate unique queue ID for this record
        queue_id = f"queue_{len(self._prediction_queues[session_id])}_{int(time.time()*1000)}"
        
        queued_record = {
            'queue_id': queue_id,
            'record': record,
            'target_column': target_column,
            'timestamp': time.time()
        }
        
        self._prediction_queues[session_id].append(queued_record)
        return queue_id
    
    def _get_json(self, endpoint: str, max_retries: int = None, **kwargs) -> Dict[str, Any]:
        """Make a GET request and return JSON response."""
        response = self._make_request("GET", endpoint, max_retries=max_retries, **kwargs)
        return response.json()
    
    def _post_json(self, endpoint: str, data: Dict[str, Any] = None, max_retries: int = None, **kwargs) -> Dict[str, Any]:
        """Make a POST request with JSON data and return JSON response."""
        if data is not None:
            kwargs['json'] = data
        response = self._make_request("POST", endpoint, max_retries=max_retries, **kwargs)
        return response.json()

    # =========================================================================
    # Session Management
    # =========================================================================
    
    def create_session(self, session_type: str = "sphere") -> SessionInfo:
        """
        Create a new session.
        
        Args:
            session_type: Type of session to create ('sphere', 'predictor', etc.)
            
        Returns:
            SessionInfo object with session details
        """
        print(f"Creating {session_type} session...")
        
        # Send empty JSON object to ensure proper content-type
        response_data = self._post_json("/compute/session", {})
        
        session_id = response_data.get('session_id')
        print(f"Created session: {session_id}")
        
        return SessionInfo(
            session_id=session_id,
            session_type=response_data.get('session_type', 'sphere'),
            status=response_data.get('status', 'unknown'),
            jobs={},
            job_queue_positions={}
        )
    
    def get_session_status(self, session_id: str, max_retries: int = None) -> SessionInfo:
        """
        Get detailed session status.
        
        Args:
            session_id: ID of the session
            max_retries: Override default retry count (useful during server restarts)
            
        Returns:
            SessionInfo object with current session details
        """
        # Use higher retry count for session endpoints during server restarts
        if max_retries is None:
            max_retries = max(8, self.default_max_retries)
            
        response_data = self._get_json(f"/compute/session/{session_id}", max_retries=max_retries)
        
        session = response_data.get('session', {})
        jobs = response_data.get('jobs', {})
        positions = response_data.get('job_queue_positions', {})
        
        return SessionInfo(
            session_id=session.get('session_id', session_id),
            session_type=session.get('session_type', 'unknown'),
            status=session.get('status', 'unknown'),
            jobs=jobs,
            job_queue_positions=positions
        )
    
    def get_session_models(self, session_id: str, max_retries: int = None) -> Dict[str, Any]:
        """
        Get available models and embedding spaces for a session.
        
        Args:
            session_id: ID of the session
            max_retries: Override default retry count (useful during server restarts)
            
        Returns:
            Dictionary containing available models, their metadata, and summary information
        """
        print(f"Getting available models for session {session_id}")
        
        # Use higher retry count for session endpoints during server restarts
        if max_retries is None:
            max_retries = max(8, self.default_max_retries)
            
        response_data = self._get_json(f"/compute/session/{session_id}/models", max_retries=max_retries)
        
        models = response_data.get('models', {})
        summary = response_data.get('summary', {})
        
        print(f"Available models: {summary.get('available_model_types', [])}")
        print(f"Training complete: {'✅' if summary.get('training_complete') else '❌'}")
        print(f"Prediction ready: {'✅' if summary.get('prediction_ready') else '❌'}")
        print(f"Similarity search ready: {'✅' if summary.get('similarity_search_ready') else '❌'}")
        print(f"Visualization ready: {'✅' if summary.get('visualization_ready') else '❌'}")
        
        return response_data
    
    def wait_for_session_completion(self, session_id: str, max_wait_time: int = 3600, 
                                   check_interval: int = 10) -> SessionInfo:
        """
        Wait for a session to complete, with smart progress display.
        
        Args:
            session_id: ID of the session to monitor
            max_wait_time: Maximum time to wait in seconds
            check_interval: How often to check status in seconds
            
        Returns:
            Final SessionInfo when session completes or times out
        """
        return self._wait_with_smart_display(session_id, max_wait_time, check_interval)
    
    def _is_notebook(self) -> bool:
        """Detect if running in a Jupyter notebook."""
        try:
            from IPython import get_ipython
            ipython = get_ipython()
            return ipython is not None and hasattr(ipython, 'kernel')
        except ImportError:
            return False
    
    def _has_rich(self) -> bool:
        """Check if rich library is available."""
        try:
            import rich
            return True
        except ImportError:
            return False
    
    def _wait_with_smart_display(self, session_id: str, max_wait_time: int, check_interval: int) -> SessionInfo:
        """Smart progress display that adapts to environment."""
        
        if self._is_notebook():
            return self._wait_with_notebook_display(session_id, max_wait_time, check_interval)
        elif self._has_rich():
            return self._wait_with_rich_display(session_id, max_wait_time, check_interval)
        else:
            return self._wait_with_simple_display(session_id, max_wait_time, check_interval)
    
    def _wait_with_notebook_display(self, session_id: str, max_wait_time: int, check_interval: int) -> SessionInfo:
        """Notebook-optimized display with clean updates."""
        try:
            from IPython.display import clear_output, display, HTML
            import time
            
            print(f"🚀 Monitoring session {session_id}")
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                session_info = self.get_session_status(session_id)
                
                # Clear previous output and show updated status
                clear_output(wait=True)
                
                elapsed = int(time.time() - start_time)
                mins, secs = divmod(elapsed, 60)
                
                html_content = f"""
                <h3>🚀 Session {session_id}</h3>
                <p><strong>Status:</strong> {session_info.status} | <strong>Elapsed:</strong> {mins:02d}:{secs:02d}</p>
                """
                
                if session_info.jobs:
                    html_content += "<h4>Jobs:</h4><ul>"
                    for job_id, job in session_info.jobs.items():
                        job_status = job.get('status', 'unknown')
                        progress = job.get('progress')
                        job_type = job.get('type', job_id.split('_')[0])
                        
                        if progress is not None:
                            progress_pct = progress * 100
                            progress_bar = "▓" * int(progress_pct / 5) + "░" * (20 - int(progress_pct / 5))
                            html_content += f"<li><strong>{job_type}:</strong> {job_status} [{progress_bar}] {progress_pct:.1f}%</li>"
                        else:
                            status_emoji = "✅" if job_status == "done" else "🔄" if job_status == "running" else "❌"
                            html_content += f"<li>{status_emoji} <strong>{job_type}:</strong> {job_status}</li>"
                    html_content += "</ul>"
                
                display(HTML(html_content))
                
                # Check completion
                if session_info.status in ['done', 'failed', 'cancelled']:
                    print(f"✅ Session completed with status: {session_info.status}")
                    return session_info
                
                if session_info.jobs:
                    terminal_states = {'done', 'failed', 'cancelled'}
                    all_jobs_terminal = all(job.get('status') in terminal_states for job in session_info.jobs.values())
                    if all_jobs_terminal:
                        job_summary = self._analyze_job_completion(session_info.jobs)
                        print(f"✅ All jobs completed. {job_summary}")
                        return session_info
                
                time.sleep(check_interval)
            
            print(f"⏰ Timeout after {max_wait_time} seconds")
            return self.get_session_status(session_id)
            
        except ImportError:
            # Fallback if IPython not available
            return self._wait_with_simple_display(session_id, max_wait_time, check_interval)
    
    def _wait_with_rich_display(self, session_id: str, max_wait_time: int, check_interval: int) -> SessionInfo:
        """Rich progress bars for beautiful terminal display."""
        try:
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
            from rich.live import Live
            from rich.table import Table
            from rich.panel import Panel
            from rich.text import Text
            import time
            
            start_time = time.time()
            job_tasks = {}  # Track progress tasks for each job
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                expand=True
            ) as progress:
                
                # Main session task
                session_task = progress.add_task(f"[bold green]Session {session_id}", total=100)
                
                while time.time() - start_time < max_wait_time:
                    session_info = self.get_session_status(session_id)
                    
                    # Update session progress
                    elapsed = time.time() - start_time
                    session_progress = min(elapsed / max_wait_time * 100, 99)
                    progress.update(session_task, completed=session_progress, 
                                  description=f"[bold green]Session {session_id} ({session_info.status})")
                    
                    # Update job progress
                    current_jobs = set(session_info.jobs.keys())
                    
                    # Add new jobs
                    for job_id, job in session_info.jobs.items():
                        if job_id not in job_tasks:
                            job_type = job.get('type', job_id.split('_')[0])
                            job_tasks[job_id] = progress.add_task(f"[cyan]{job_type}", total=100)
                        
                        # Update job progress
                        job_status = job.get('status', 'unknown')
                        raw_progress = job.get('progress', 0)
                        job_progress = 100 if job_status == 'done' else (raw_progress * 100 if raw_progress else 0)
                        
                        progress.update(job_tasks[job_id], completed=job_progress,
                                      description=f"[cyan]{job.get('type', job_id.split('_')[0])} ({job_status})")
                    
                    # Check completion
                    if session_info.status in ['done', 'failed', 'cancelled']:
                        progress.update(session_task, completed=100, 
                                      description=f"[bold green]Session {session_id} ✅ {session_info.status}")
                        break
                    
                    if session_info.jobs:
                        terminal_states = {'done', 'failed', 'cancelled'}
                        all_jobs_terminal = all(job.get('status') in terminal_states for job in session_info.jobs.values())
                        if all_jobs_terminal:
                            progress.update(session_task, completed=100,
                                          description=f"[bold green]Session {session_id} ✅ completed")
                            break
                    
                    time.sleep(check_interval)
                
                # Final summary
                session_info = self.get_session_status(session_id)
                if session_info.jobs:
                    job_summary = self._analyze_job_completion(session_info.jobs)
                    progress.console.print(f"\n[bold green]✅ {job_summary}")
                
                return session_info
                
        except ImportError:
            # Fallback if rich not available
            return self._wait_with_simple_display(session_id, max_wait_time, check_interval)
    
    def _wait_with_simple_display(self, session_id: str, max_wait_time: int, check_interval: int) -> SessionInfo:
        """Simple display with line overwriting for basic terminals."""
        import sys
        import time
        
        print(f"🚀 Waiting for session {session_id} to complete...")
        start_time = time.time()
        last_num_lines = 0
        
        while time.time() - start_time < max_wait_time:
            session_info = self.get_session_status(session_id)
            
            # Clear previous lines if terminal supports it
            if sys.stdout.isatty() and last_num_lines > 0:
                for _ in range(last_num_lines):
                    sys.stdout.write('\033[F')  # Move cursor up
                    sys.stdout.write('\033[2K')  # Clear line
            
            # Build status display
            elapsed = int(time.time() - start_time)
            mins, secs = divmod(elapsed, 60)
            
            lines = []
            lines.append(f"📊 Session {session_id} | Status: {session_info.status} | Elapsed: {mins:02d}:{secs:02d}")
            
            if session_info.jobs:
                for job_id, job in session_info.jobs.items():
                    job_status = job.get('status', 'unknown')
                    progress = job.get('progress')
                    job_type = job.get('type', job_id.split('_')[0])
                    
                    if progress is not None:
                        # Fix percentage issue: show 100% when job is done
                        progress_pct = 100.0 if job_status == 'done' else (progress * 100)
                        progress_bar = "█" * int(progress_pct / 5) + "░" * (20 - int(progress_pct / 5))
                        lines.append(f"  {job_type}: {job_status} [{progress_bar}] {progress_pct:.1f}%")
                    else:
                        status_emoji = "✅" if job_status == "done" else "🔄" if job_status == "running" else "❌"
                        lines.append(f"  {status_emoji} {job_type}: {job_status}")
            
            # Print all lines
            for line in lines:
                print(line)
            
            last_num_lines = len(lines)
            
            # Check completion
            if session_info.status in ['done', 'failed', 'cancelled']:
                print(f"\n✅ Session completed with status: {session_info.status}")
                return session_info
            
            if session_info.jobs:
                terminal_states = {'done', 'failed', 'cancelled'}
                all_jobs_terminal = all(job.get('status') in terminal_states for job in session_info.jobs.values())
                if all_jobs_terminal:
                    job_summary = self._analyze_job_completion(session_info.jobs)
                    print(f"\n✅ All jobs completed. {job_summary}")
                    return session_info
            
            time.sleep(check_interval)
        
        print(f"\n⏰ Timeout waiting for session completion after {max_wait_time} seconds")
        return self.get_session_status(session_id)

    def _analyze_job_completion(self, jobs: Dict[str, Any]) -> str:
        """
        Analyze job completion status and provide detailed summary.
        
        Args:
            jobs: Dictionary of job information
            
        Returns:
            Formatted string describing job completion status
        """
        done_jobs = []
        failed_jobs = []
        cancelled_jobs = []
        
        for job_id, job in jobs.items():
            status = job.get('status', 'unknown')
            job_type = job.get('type', 'unknown')
            
            if status == 'done':
                done_jobs.append(f"{job_type} ({job_id})")
            elif status == 'failed':
                error_info = ""
                # Look for error information in various possible fields
                if 'error' in job:
                    error_info = f" - Error: {job['error']}"
                elif 'message' in job:
                    error_info = f" - Message: {job['message']}"
                failed_jobs.append(f"{job_type} ({job_id}){error_info}")
            elif status == 'cancelled':
                cancelled_jobs.append(f"{job_type} ({job_id})")
        
        # Build summary message
        summary_parts = []
        if done_jobs:
            summary_parts.append(f"✅ {len(done_jobs)} succeeded: {', '.join(done_jobs)}")
        if failed_jobs:
            summary_parts.append(f"❌ {len(failed_jobs)} failed: {', '.join(failed_jobs)}")
        if cancelled_jobs:
            summary_parts.append(f"🚫 {len(cancelled_jobs)} cancelled: {', '.join(cancelled_jobs)}")
        
        return " | ".join(summary_parts) if summary_parts else "No jobs found"

    def create_embedding_space(self, name: str, s3_training_dataset: str, s3_validation_dataset: str) -> SessionInfo:
        """
        Create a new embedding space from S3 training and validation datasets.
        
        Args:
            name: Name for the embedding space
            s3_training_dataset: S3 URL for training dataset (must start with 's3://')
            s3_validation_dataset: S3 URL for validation dataset (must start with 's3://')
            
        Returns:
            SessionInfo for the newly created embedding space session
            
        Raises:
            ValueError: If S3 URLs are invalid
        """
        # Validate S3 URLs
        if not s3_training_dataset.startswith('s3://'):
            raise ValueError("s3_training_dataset must be a valid S3 URL (s3://...)")
        if not s3_validation_dataset.startswith('s3://'):
            raise ValueError("s3_validation_dataset must be a valid S3 URL (s3://...)")
        
        print(f"Creating embedding space '{name}' from S3 datasets...")
        print(f"  Training: {s3_training_dataset}")
        print(f"  Validation: {s3_validation_dataset}")
        
        data = {
            "name": name,
            "s3_file_data_set_training": s3_training_dataset,
            "s3_file_data_set_validation": s3_validation_dataset
        }
        
        response_data = self._post_json("/compute/create-embedding-space", data)
        
        session_id = response_data.get('session_id')
        print(f"Embedding space session created: {session_id}")
        
        return SessionInfo(
            session_id=session_id,
            session_type=response_data.get('session_type', 'embedding_space'),
            status=response_data.get('status', 'ready'),
            jobs={},
            job_queue_positions={}
        )

    # =========================================================================
    # File Upload
    # =========================================================================
    
    def upload_file_and_create_session(self, file_path: Path) -> SessionInfo:
        """
        Upload a CSV file and create a new session.
        
        Args:
            file_path: Path to the CSV file to upload
            
        Returns:
            SessionInfo for the newly created session
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"Uploading file: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'text/csv')}
            response = self._make_request("POST", "/compute/upload_with_new_session/", files=files)
        
        response_data = response.json()
        session_id = response_data.get('session_id')
        
        print(f"File uploaded, session created: {session_id}")
        
        # Check for and display warnings
        warnings = response_data.get('warnings', [])
        if warnings:
            print("\n" + "="*60)
            print("⚠️  UPLOAD WARNINGS")
            print("="*60)
            for warning in warnings:
                print(warning)
            print("="*60 + "\n")
        
        return SessionInfo(
            session_id=session_id,
            session_type=response_data.get('session_type', 'sphere'),
            status=response_data.get('status', 'ready'),
            jobs={},
            job_queue_positions={}
        )

    def upload_df_and_create_session(self, df=None, filename: str = "data.csv", file_path: str = None, 
                                    column_overrides: Dict[str, str] = None, string_list_delimiter: str = "|") -> SessionInfo:
        """
        Upload a pandas DataFrame or CSV file and create a new session.
        
        Args:
            df: pandas DataFrame to upload (optional if file_path is provided)
            filename: Name to give the uploaded file (default: "data.csv")
            file_path: Path to CSV file to upload (optional if df is provided)
            column_overrides: Dict mapping column names to types ("scalar", "set", "string", "string_list")
            string_list_delimiter: Delimiter for string_list columns (default: "|")
            
        Returns:
            SessionInfo for the newly created session
        """
        import pandas as pd
        import io
        import gzip
        import os
        
        # Validate inputs
        if df is None and file_path is None:
            raise ValueError("Either df or file_path must be provided")
        if df is not None and file_path is not None:
            raise ValueError("Provide either df or file_path, not both")
        
        # Handle file path input
        if file_path:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Check if it's a CSV file
            if not file_path.lower().endswith(('.csv', '.csv.gz')):
                raise ValueError("File must be a CSV file (with .csv or .csv.gz extension)")
            
            print(f"Uploading file: {file_path}")
            
            # Read the file content
            if file_path.endswith('.gz'):
                # Already gzipped
                with gzip.open(file_path, 'rb') as f:
                    file_content = f.read()
                upload_filename = os.path.basename(file_path)
                content_type = 'application/gzip'
            else:
                # Read CSV and compress it
                with open(file_path, 'rb') as f:
                    csv_content = f.read()
                
                # Compress the content
                print("Compressing CSV file...")
                compressed_buffer = io.BytesIO()
                with gzip.GzipFile(fileobj=compressed_buffer, mode='wb') as gz:
                    gz.write(csv_content)
                file_content = compressed_buffer.getvalue()
                upload_filename = os.path.basename(file_path) + '.gz'
                content_type = 'application/gzip'
                
                original_size = len(csv_content)
                compressed_size = len(file_content)
                compression_ratio = (1 - compressed_size / original_size) * 100
                print(f"Compressed from {original_size:,} to {compressed_size:,} bytes ({compression_ratio:.1f}% reduction)")
        
        # Handle DataFrame input
        else:
            if not isinstance(df, pd.DataFrame):
                raise TypeError("df must be a pandas DataFrame")
            
            print(f"Uploading DataFrame ({len(df)} rows, {len(df.columns)} columns)")
            
            # Convert DataFrame to CSV and compress
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue().encode('utf-8')
            
            # Compress the CSV data
            print("Compressing DataFrame...")
            compressed_buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=compressed_buffer, mode='wb') as gz:
                gz.write(csv_data)
            file_content = compressed_buffer.getvalue()
            upload_filename = filename if filename.endswith('.gz') else filename + '.gz'
            content_type = 'application/gzip'
            
            original_size = len(csv_data)
            compressed_size = len(file_content)
            compression_ratio = (1 - compressed_size / original_size) * 100
            print(f"Compressed from {original_size:,} to {compressed_size:,} bytes ({compression_ratio:.1f}% reduction)")
        
        # Upload the compressed file with optional column overrides
        files = {'file': (upload_filename, file_content, content_type)}
        
        # Add column overrides and string_list_delimiter as form data if provided
        data = {}
        if column_overrides:
            import json
            data['column_overrides'] = json.dumps(column_overrides)
            print(f"Column overrides: {column_overrides}")
        if string_list_delimiter != "|":  # Only send if non-default
            data['string_list_delimiter'] = string_list_delimiter
            print(f"String list delimiter: '{string_list_delimiter}'")
            
        response = self._make_request("POST", "/compute/upload_with_new_session/", files=files, data=data)
        
        response_data = response.json()
        session_id = response_data.get('session_id')
        
        print(f"Upload complete, session created: {session_id}")
        
        # Check for and display warnings
        warnings = response_data.get('warnings', [])
        if warnings:
            print("\n" + "="*60)
            print("⚠️  UPLOAD WARNINGS")
            print("="*60)
            for warning in warnings:
                print(warning)
            print("="*60 + "\n")
        
        return SessionInfo(
            session_id=session_id,
            session_type=response_data.get('session_type', 'sphere'),
            status=response_data.get('status', 'ready'),
            jobs={},
            job_queue_positions={}
        )
        


    # =========================================================================
    # Single Predictor Functionality
    # =========================================================================
    
    def predict(self, session_id: str, record: Dict[str, Any], target_column: str = None, 
               max_retries: int = None, queue_batches: bool = False) -> Dict[str, Any]:
        """
        Make a single prediction for a record.
        
        Args:
            session_id: ID of session with trained predictor
            record: Record dictionary (without target column)
            target_column: Specific target column predictor to use (required if multiple predictors exist)
            max_retries: Number of retries for errors (default: uses client default)
            queue_batches: If True, queue this prediction for batch processing instead of immediate API call
            
        Returns:
            Prediction result dictionary if queue_batches=False, or queue ID if queue_batches=True
        """
        # Track prediction call rate and show warning if needed
        if not queue_batches:
            should_warn = self._track_prediction_call(session_id)
            if should_warn:
                call_count = len(self._prediction_call_times.get(session_id, []))
                self._show_batching_warning(session_id, call_count)
        
        # If queueing is enabled, add to queue and return queue ID
        if queue_batches:
            queue_id = self._add_to_prediction_queue(session_id, record, target_column)
            return {"queued": True, "queue_id": queue_id}
        
        # Validate and get target column name
        validated_target_column = self._validate_and_get_target_column(session_id, target_column)
        
        # Clean NaN/Inf values and remove target column
        cleaned_record = self._clean_numpy_values(record)
        cleaned_records = self._remove_target_columns(session_id, [cleaned_record], target_column)
        final_record = cleaned_records[0] if cleaned_records else cleaned_record
        
        # Add target column info to request so server knows which predictor to use
        request_payload = {
            "query_record": final_record,
            "target_column": validated_target_column
        }
        
        response_data = self._post_json(f"/compute/session/{session_id}/predict", request_payload, max_retries=max_retries)
        return response_data
    
    def get_training_metrics(self, session_id: str, max_retries: int = None) -> Dict[str, Any]:
        """
        Get training metrics for a session's single predictor.
        
        Args:
            session_id: ID of session with trained single predictor
            max_retries: Override default retry count (useful during server restarts)
            
        Returns:
            Training metrics including loss history, validation metrics, etc.
        """
        # Use higher retry count for session endpoints during server restarts
        if max_retries is None:
            max_retries = max(8, self.default_max_retries)
            
        response_data = self._get_json(f"/compute/session/{session_id}/training_metrics", max_retries=max_retries)
        return response_data

    def train_single_predictor(self, session_id: str, target_column: str, target_column_type: str, 
                              epochs: int = 50, batch_size: int = 256, learning_rate: float = 0.001) -> Dict[str, Any]:
        """
        Add single predictor training to an existing session that has a trained embedding space.
        
        Args:
            session_id: ID of session with trained embedding space
            target_column: Name of the target column to predict
            target_column_type: Type of target column ("set" or "scalar")
            epochs: Number of training epochs (default: 50)
            batch_size: Training batch size (default: 256)
            learning_rate: Learning rate for training (default: 0.001)
            
        Returns:
            Response with training start confirmation
        """
        data = {
            "target_column": target_column,
            "target_column_type": target_column_type,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate
        }
        
        response_data = self._post_json(f"/compute/session/{session_id}/train_predictor", data)
        return response_data

    # =========================================================================
    # JSON Tables Batch Prediction
    # =========================================================================
    
    def predict_table(self, session_id: str, table_data: Dict[str, Any], max_retries: int = None) -> Dict[str, Any]:
        """
        Make batch predictions using JSON Tables format.
        
        Args:
            session_id: ID of session with trained predictor
            table_data: Data in JSON Tables format, or list of records, or dict with 'table'/'records'
            max_retries: Number of retries for errors (default: uses client default, recommend higher for batch)
            
        Returns:
            Batch prediction results in JSON Tables format
            
        Raises:
            PredictorNotFoundError: If no single predictor has been trained for this session
        """
        # Use higher default for batch operations if not specified
        if max_retries is None:
            max_retries = max(5, self.default_max_retries)
        
        try:
            response_data = self._post_json(f"/compute/session/{session_id}/predict_table", table_data, max_retries=max_retries)
            return response_data
        except Exception as e:
            # Enhanced error handling for common prediction issues
            if "404" in str(e) and "Single predictor not found" in str(e):
                self._raise_predictor_not_found_error(session_id, "predict_table")
            else:
                raise
    
    def predict_records(self, session_id: str, records: List[Dict[str, Any]], 
                       target_column: str = None, batch_size: int = 2500, use_async: bool = False, 
                       show_progress_bar: bool = True) -> Dict[str, Any]:
        """
        Make batch predictions on a list of records with automatic client-side batching.
        
        Args:
            session_id: ID of session with trained predictor
            records: List of record dictionaries
            target_column: Specific target column predictor to use (required if multiple predictors exist)
            batch_size: Number of records to send per API call (default: 2500)
            use_async: Force async processing for large datasets (default: False - async disabled due to pickle issues)
            show_progress_bar: Whether to show progress bar for async jobs (default: True)
            
        Returns:
            Batch prediction results (may include job_id for async processing)
            
        Raises:
            ValueError: If target_column is invalid or multiple predictors exist without specification
        """
        # Clean NaN/Inf values before sending
        cleaned_records = self._clean_numpy_values(records)
        
        # Remove target column that would interfere with prediction
        cleaned_records = self._remove_target_columns(session_id, cleaned_records, target_column)
        
        # Determine if we should use async processing
        ASYNC_THRESHOLD = 1000
        total_records = len(cleaned_records)
        
        # DISABLED: Async processing disabled by default due to pickle loading issues
        # If dataset is large and use_async is explicitly True
        if use_async is True and total_records >= ASYNC_THRESHOLD:
            print(f"🚀 Large dataset detected ({total_records} records) - attempting async processing...")
            print("⚠️  WARNING: Async processing may hang due to known pickle issues. Use use_async=False for reliable processing.")
            
            # Try async processing first
            from jsontables import JSONTablesEncoder
            table_data = JSONTablesEncoder.from_records(cleaned_records)
            
            try:
                result = self.predict_table(session_id, table_data)
                
                # Check if server returned an async job
                if result.get('async') and result.get('job_id'):
                    print(f"✅ Async job submitted: {result['job_id']}")
                    print(f"📊 Polling URL: {result.get('polling_url', 'Not provided')}")
                    
                    # Show progress bar by default unless disabled
                    if show_progress_bar:
                        print("\n🚀 Starting job watcher...")
                        return self.watch_prediction_job(session_id, result['job_id'])
                    else:
                        print(f"\n📋 Job submitted. Use client.watch_prediction_job('{session_id}', '{result['job_id']}') to monitor progress.")
                        return result
                else:
                    # Server handled it synchronously, return results
                    return result
                    
            except Exception as e:
                if "404" in str(e) and "Single predictor not found" in str(e):
                    self._raise_predictor_not_found_error(session_id, "predict_records")
                else:
                    print(f"⚠️  Async processing failed, falling back to client-side batching: {e}")
                    # Fall through to client-side batching
        
        # Always use client-side batching for reliable processing
        if total_records >= ASYNC_THRESHOLD:
            print(f"📦 Large dataset detected ({total_records} records) - using reliable synchronous batching...")
            print(f"💡 Processing in chunks of {batch_size} for optimal performance and stability")
        
        # Client-side batching for small datasets or when async is disabled/fails
        if total_records <= batch_size:
            # Small dataset - send all at once
            from jsontables import JSONTablesEncoder
            table_data = JSONTablesEncoder.from_records(cleaned_records)
            
            try:
                return self.predict_table(session_id, table_data)
            except Exception as e:
                if "404" in str(e) and "Single predictor not found" in str(e):
                    self._raise_predictor_not_found_error(session_id, "predict_records")
                else:
                    raise
        
        # Large dataset - use client-side batching
        print(f"📦 Processing {total_records} records in batches of {batch_size}...")
        
        all_predictions = []
        successful_predictions = 0
        failed_predictions = 0
        errors = []
        
        from jsontables import JSONTablesEncoder
        
        # Process in chunks
        for i in range(0, total_records, batch_size):
            chunk_end = min(i + batch_size, total_records)
            chunk_records = cleaned_records[i:chunk_end]
            chunk_size = len(chunk_records)
            
            print(f"  Processing records {i+1}-{chunk_end} ({chunk_size} records)...")
            
            try:
                # Convert chunk to JSON Tables format
                table_data = JSONTablesEncoder.from_records(chunk_records)
                
                # Make prediction
                chunk_result = self.predict_table(session_id, table_data)
                chunk_predictions = chunk_result.get('predictions', [])
                
                # Adjust row indices to match original dataset
                for pred in chunk_predictions:
                    if 'row_index' in pred:
                        pred['row_index'] += i  # Offset by chunk start
                
                all_predictions.extend(chunk_predictions)
                successful_predictions += chunk_result.get('successful_predictions', 0)
                failed_predictions += chunk_result.get('failed_predictions', 0)
                
                if chunk_result.get('errors'):
                    errors.extend(chunk_result['errors'])
                
            except Exception as e:
                if "404" in str(e) and "Single predictor not found" in str(e):
                    self._raise_predictor_not_found_error(session_id, "predict_records")
                else:
                    print(f"    ❌ Chunk {i//batch_size + 1} failed: {e}")
                    
                    # Add failed predictions for this chunk
                    for j in range(chunk_size):
                        all_predictions.append({
                            "row_index": i + j,
                            "prediction_id": None,
                            "prediction": None,
                            "error": str(e)
                        })
                    failed_predictions += chunk_size
                    errors.append(f"Chunk {i//batch_size + 1} (records {i+1}-{chunk_end}): {str(e)}")
        
        print(f"✅ Completed: {successful_predictions} successful, {failed_predictions} failed")
        
        return {
            'predictions': all_predictions,
            'summary': {
                'total_records': total_records,
                'successful_predictions': successful_predictions,
                'failed_predictions': failed_predictions,
                'errors': errors,
                'batched': True,
                'batch_size': batch_size,
                'chunks_processed': (total_records + batch_size - 1) // batch_size
            }
        }
    
    def poll_prediction_job(self, session_id: str, job_id: str, max_wait_time: int = 3600, 
                           check_interval: int = 10) -> Dict[str, Any]:
        """
        Poll a Celery prediction job until completion.
        
        Args:
            session_id: Session ID
            job_id: Celery job ID from async prediction
            max_wait_time: Maximum time to wait in seconds (default: 1 hour)
            check_interval: How often to check status in seconds (default: 10s)
            
        Returns:
            Final job results or status information
        """
        import time
        
        print(f"🔄 Polling prediction job {job_id}...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = self._get_json(f"/compute/session/{session_id}/prediction_job/{job_id}")
                
                status = response.get('status')
                print(f"📊 Status: {status}")
                
                if status == 'completed':
                    print("✅ Prediction job completed successfully!")
                    return response
                elif status == 'failed':
                    print("❌ Prediction job failed!")
                    return response
                elif status == 'running':
                    current = response.get('current', 0)
                    total = response.get('total', 0)
                    message = response.get('message', 'Processing...')
                    
                    if total > 0:
                        progress = response.get('progress_percent', 0)
                        print(f"  🚀 {message} ({current}/{total} - {progress}%)")
                    else:
                        print(f"  🚀 {message}")
                elif status == 'pending':
                    print("  ⏳ Job is waiting to be processed...")
                else:
                    print(f"  ❓ Unknown status: {status}")
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"❌ Error checking job status: {e}")
                return {'status': 'error', 'error': str(e)}
        
        print(f"⏰ Timeout after {max_wait_time} seconds")
        return {'status': 'timeout', 'message': f'Job did not complete within {max_wait_time} seconds'}
    
    def watch_prediction_job(self, session_id: str, job_id: str, max_wait_time: int = 3600, 
                            check_interval: int = 5) -> Dict[str, Any]:
        """
        Watch a prediction job with beautiful progress display (similar to training jobs).
        
        Args:
            session_id: Session ID
            job_id: Celery job ID from async prediction
            max_wait_time: Maximum time to wait in seconds (default: 1 hour)
            check_interval: How often to check status in seconds (default: 5s)
            
        Returns:
            Final job results with predictions
        """
        # Use the same smart display logic as training job watching
        if self._is_notebook():
            return self._watch_prediction_job_notebook(session_id, job_id, max_wait_time, check_interval)
        elif self._has_rich():
            return self._watch_prediction_job_rich(session_id, job_id, max_wait_time, check_interval)
        else:
            return self._watch_prediction_job_simple(session_id, job_id, max_wait_time, check_interval)
    
    def _watch_prediction_job_notebook(self, session_id: str, job_id: str, max_wait_time: int, check_interval: int) -> Dict[str, Any]:
        """Watch prediction job with Jupyter notebook display."""
        try:
            from IPython.display import clear_output, display, HTML
            import time
            
            print(f"🔄 Monitoring prediction job {job_id}")
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                try:
                    response = self._get_json(f"/compute/session/{session_id}/prediction_job/{job_id}")
                    
                    # Clear previous output and show updated status
                    clear_output(wait=True)
                    
                    elapsed = int(time.time() - start_time)
                    mins, secs = divmod(elapsed, 60)
                    
                    status = response.get('status')
                    
                    html_content = f"""
                    <h3>🔄 Prediction Job {job_id[:8]}...</h3>
                    <p><strong>Status:</strong> {status} | <strong>Elapsed:</strong> {mins:02d}:{secs:02d}</p>
                    """
                    
                    if status == 'running':
                        current = response.get('current', 0)
                        total = response.get('total', 0)
                        message = response.get('message', 'Processing...')
                        
                        if total > 0:
                            progress_pct = (current / total) * 100
                            progress_bar = "▓" * int(progress_pct / 5) + "░" * (20 - int(progress_pct / 5))
                            html_content += f"""
                            <p><strong>Progress:</strong> {current:,}/{total:,} records ({progress_pct:.1f}%)</p>
                            <p><code>[{progress_bar}]</code></p>
                            <p><em>{message}</em></p>
                            """
                        else:
                            html_content += f"<p><em>{message}</em></p>"
                    
                    display(HTML(html_content))
                    
                    # Check completion
                    if status == 'completed':
                        print(f"✅ Prediction job completed successfully!")
                        return response
                    elif status == 'failed':
                        print(f"❌ Prediction job failed!")
                        return response
                    
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"❌ Error checking job status: {e}")
                    return {'status': 'error', 'error': str(e)}
            
            print(f"⏰ Timeout after {max_wait_time} seconds")
            return {'status': 'timeout', 'message': f'Job did not complete within {max_wait_time} seconds'}
            
        except ImportError:
            # Fallback if IPython not available
            return self._watch_prediction_job_simple(session_id, job_id, max_wait_time, check_interval)
    
    def _watch_prediction_job_rich(self, session_id: str, job_id: str, max_wait_time: int, check_interval: int) -> Dict[str, Any]:
        """Watch prediction job with Rich progress bars."""
        try:
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
            from rich.console import Console
            import time
            
            console = Console()
            start_time = time.time()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                expand=True
            ) as progress:
                
                # Main prediction task
                task = progress.add_task(f"[bold green]Prediction Job {job_id[:8]}...", total=100)
                
                while time.time() - start_time < max_wait_time:
                    try:
                        response = self._get_json(f"/compute/session/{session_id}/prediction_job/{job_id}")
                        
                        status = response.get('status')
                        
                        if status == 'running':
                            current = response.get('current', 0)
                            total = response.get('total', 0)
                            message = response.get('message', 'Processing...')
                            
                            if total > 0:
                                progress_pct = (current / total) * 100
                                progress.update(task, completed=progress_pct,
                                              description=f"[bold green]Processing {current:,}/{total:,} records")
                            else:
                                progress.update(task, description=f"[bold green]{message}")
                        
                        elif status == 'pending':
                            progress.update(task, description="[bold yellow]Waiting to start...")
                        
                        elif status == 'completed':
                            progress.update(task, completed=100,
                                          description="[bold green]✅ Prediction job completed!")
                            console.print("🎉 [bold green]Success![/bold green] Predictions are ready.")
                            return response
                        
                        elif status == 'failed':
                            progress.update(task, description="[bold red]❌ Prediction job failed!")
                            console.print("💥 [bold red]Failed![/bold red] Check error details.")
                            return response
                        
                        time.sleep(check_interval)
                        
                    except Exception as e:
                        console.print(f"[bold red]❌ Error checking job status: {e}[/bold red]")
                        return {'status': 'error', 'error': str(e)}
                
                console.print(f"[bold yellow]⏰ Timeout after {max_wait_time} seconds[/bold yellow]")
                return {'status': 'timeout', 'message': f'Job did not complete within {max_wait_time} seconds'}
                
        except ImportError:
            # Fallback if rich not available
            return self._watch_prediction_job_simple(session_id, job_id, max_wait_time, check_interval)
    
    def _watch_prediction_job_simple(self, session_id: str, job_id: str, max_wait_time: int, check_interval: int) -> Dict[str, Any]:
        """Watch prediction job with simple terminal display."""
        import sys
        import time
        
        print(f"🔄 Watching prediction job {job_id}")
        start_time = time.time()
        last_num_lines = 0
        
        while time.time() - start_time < max_wait_time:
            try:
                response = self._get_json(f"/compute/session/{session_id}/prediction_job/{job_id}")
                
                # Clear previous lines if terminal supports it
                if sys.stdout.isatty() and last_num_lines > 0:
                    for _ in range(last_num_lines):
                        sys.stdout.write('\033[F')  # Move cursor up
                        sys.stdout.write('\033[2K')  # Clear line
                
                # Build status display
                elapsed = int(time.time() - start_time)
                mins, secs = divmod(elapsed, 60)
                
                status = response.get('status')
                
                lines = []
                lines.append(f"🔄 Prediction Job {job_id[:8]}... | Status: {status} | Elapsed: {mins:02d}:{secs:02d}")
                
                if status == 'running':
                    current = response.get('current', 0)
                    total = response.get('total', 0)
                    message = response.get('message', 'Processing...')
                    
                    if total > 0:
                        progress_pct = (current / total) * 100
                        progress_bar = "█" * int(progress_pct / 5) + "░" * (20 - int(progress_pct / 5))
                        lines.append(f"  Progress: {current:,}/{total:,} records ({progress_pct:.1f}%)")
                        lines.append(f"  [{progress_bar}]")
                    
                    lines.append(f"  {message}")
                
                elif status == 'pending':
                    lines.append("  ⏳ Waiting for worker to start processing...")
                
                # Print all lines
                for line in lines:
                    print(line)
                
                last_num_lines = len(lines)
                
                # Check completion
                if status == 'completed':
                    print(f"\n✅ Prediction job completed successfully!")
                    return response
                elif status == 'failed':
                    print(f"\n❌ Prediction job failed!")
                    return response
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"\n❌ Error checking job status: {e}")
                return {'status': 'error', 'error': str(e)}
        
        print(f"\n⏰ Timeout after {max_wait_time} seconds")
        return {'status': 'timeout', 'message': f'Job did not complete within {max_wait_time} seconds'}
    
    def predict_df(self, session_id: str, df, target_column: str = None, show_progress_bar: bool = True) -> Dict[str, Any]:
        """
        Make batch predictions on a pandas DataFrame.
        
        Args:
            session_id: ID of session with trained predictor
            df: Pandas DataFrame
            target_column: Specific target column predictor to use (required if multiple predictors exist)
            show_progress_bar: Whether to show progress bar for async jobs (default: True)
            
        Returns:
            Batch prediction results
            
        Raises:
            ValueError: If target_column is invalid or multiple predictors exist without specification
        """
        # Convert DataFrame to records and clean NaN/Inf values
        records = df.to_dict(orient='records')
        return self.predict_records(session_id, records, target_column=target_column, show_progress_bar=show_progress_bar)
    
    def _raise_predictor_not_found_error(self, session_id: str, method_name: str):
        """
        Raise a helpful error message when a single predictor is not found.
        
        Args:
            session_id: ID of the session
            method_name: Name of the method that was called
        """
        # Try to get session status to provide better guidance
        try:
            status = self.get_session_status(session_id)
            has_embedding = any('train_es' in job_id or 'embedding' in job.get('type', '') 
                              for job_id, job in status.jobs.items())
            has_predictor = any('train_single_predictor' in job_id or 'single_predictor' in job.get('type', '') 
                               for job_id, job in status.jobs.items())
            
            if not has_embedding:
                error_msg = f"""
❌ No trained model found for session {session_id}

🔍 ISSUE: This session doesn't have a trained embedding space yet.

🛠️  SOLUTION: Wait for training to complete, or start training:
   1. Check session status: client.get_session_status('{session_id}')
   2. Wait for completion: client.wait_for_session_completion('{session_id}')

📊 Current session jobs: {len(status.jobs)} jobs, status: {status.status}
"""
            elif not has_predictor:
                error_msg = f"""
❌ No single predictor found for session {session_id}

🔍 ISSUE: This session has a trained embedding space but no single predictor.

🛠️  SOLUTION: Train a single predictor first:
   client.train_single_predictor('{session_id}', 'target_column_name', 'set')
   
   Replace 'target_column_name' with your actual target column.
   Use 'set' for classification or 'scalar' for regression.

📊 Session has embedding space but needs predictor training.
"""
            else:
                error_msg = f"""
❌ Single predictor not ready for session {session_id}

🔍 ISSUE: Predictor training may still be in progress or failed.

🛠️  SOLUTION: Check training status:
   1. Check status: client.get_session_status('{session_id}')
   2. Check training metrics: client.get_training_metrics('{session_id}')
   3. Wait for completion if still training

📊 Found predictor job but prediction failed - training may be incomplete.
"""
                
        except Exception:
            # Fallback error message if we can't get session info
            error_msg = f"""
❌ Single predictor not found for session {session_id}

🔍 ISSUE: No trained single predictor available for predictions.

🛠️  SOLUTIONS:
   1. Train a single predictor:
      client.train_single_predictor('{session_id}', 'target_column', 'set')
   
   2. Check if training is still in progress:
      client.get_session_status('{session_id}')
   
   3. Create a new session if this one is corrupted:
      session = client.upload_df_and_create_session(df=your_data)
      client.train_single_predictor(session.session_id, 'target_column', 'set')

💡 TIP: Use 'set' for classification, 'scalar' for regression.
"""
        
        # Create a custom exception class for better error handling
        class PredictorNotFoundError(Exception):
            def __init__(self, message):
                super().__init__(message)
                self.session_id = session_id
                self.method_name = method_name
        
        raise PredictorNotFoundError(error_msg.strip())
    
    def _get_available_predictors(self, session_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all available predictors for a session from the server.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Dictionary mapping target_column -> predictor_info
        """
        try:
            # First try to get predictor info from session models endpoint
            response_data = self._get_json(f"/compute/session/{session_id}/models")
            models = response_data.get('models', {})
            
            predictors = {}
            
            # Check for single predictor (old format)
            single_predictor = models.get('single_predictor', {})
            if single_predictor.get('available'):
                # Need to load the actual predictor to get target column
                try:
                    session_data = self._get_json(f"/compute/session/{session_id}", max_retries=8)
                    session = session_data.get('session', {})
                    
                    # Check if we have target column info in training metrics
                    training_metrics = models.get('training_metrics', {})
                    if training_metrics.get('available'):
                        metrics_data = self.get_training_metrics(session_id)
                        target_column = metrics_data.get('training_metrics', {}).get('target_column')
                        if target_column:
                            predictors[target_column] = {
                                'path': single_predictor.get('path'),
                                'target_column': target_column,
                                'available': True,
                                'type': 'single_predictor'
                            }
                except Exception as e:
                    print(f"Warning: Could not extract target column from single predictor: {e}")
            
            # Check for multiple predictors (new format)
            # Look at session info to get single_predictors array
            try:
                session_data = self._get_json(f"/compute/session/{session_id}", max_retries=8)
                session = session_data.get('session', {})
                
                # New format: single_predictors array
                single_predictors_paths = session.get('single_predictors', [])
                if single_predictors_paths:
                    # Try to get target column info from training metrics
                    training_metrics = models.get('training_metrics', {})
                    if training_metrics.get('available'):
                        try:
                            metrics_data = self.get_training_metrics(session_id)
                            target_column = metrics_data.get('training_metrics', {}).get('target_column')
                            if target_column and target_column not in predictors:
                                # For now, assume all predictors in the array predict the same target
                                # (this can be enhanced later when we have per-predictor metadata)
                                predictors[target_column] = {
                                    'paths': single_predictors_paths,
                                    'target_column': target_column,
                                    'available': True,
                                    'type': 'multiple_predictors',
                                    'count': len(single_predictors_paths)
                                }
                        except Exception as e:
                            print(f"Warning: Could not extract target column from training metrics: {e}")
                
                # Fallback: check old format single_predictor field
                single_predictor_path = session.get('single_predictor')
                if single_predictor_path and not predictors:
                    # Try to get target column from training metrics
                    try:
                        training_metrics = models.get('training_metrics', {})
                        if training_metrics.get('available'):
                            metrics_data = self.get_training_metrics(session_id)
                            target_column = metrics_data.get('training_metrics', {}).get('target_column')
                            if target_column:
                                predictors[target_column] = {
                                    'path': single_predictor_path,
                                    'target_column': target_column,
                                    'available': True,
                                    'type': 'single_predictor_legacy'
                                }
                    except Exception as e:
                        print(f"Warning: Could not extract target column from legacy predictor: {e}")
                        
            except Exception as e:
                print(f"Warning: Could not get session data: {e}")
            
            return predictors
            
        except Exception as e:
            print(f"Warning: Could not fetch predictors from server: {e}")
            return {}
    
    def _validate_and_get_target_column(self, session_id: str, target_column: str = None) -> str:
        """
        Validate that a predictor exists for the target column and return the column name.
        
        Args:
            session_id: ID of the session
            target_column: Specific target column to validate, or None for auto-detect
            
        Returns:
            Validated target column name
            
        Raises:
            ValueError: If target_column is invalid or multiple predictors exist without specification
        """
        available_predictors = self._get_available_predictors(session_id)
        
        if not available_predictors:
            raise ValueError(f"No trained predictors found for session {session_id}")
        
        if target_column is None:
            # Auto-detect: only valid if there's exactly one predictor
            if len(available_predictors) == 1:
                return list(available_predictors.keys())[0]
            else:
                available_columns = list(available_predictors.keys())
                raise ValueError(
                    f"Multiple predictors found for session {session_id}: {available_columns}. "
                    f"Please specify target_column parameter."
                )
        else:
            # Validate specified target column
            if target_column not in available_predictors:
                available_columns = list(available_predictors.keys())
                raise ValueError(
                    f"No trained predictor found for target column '{target_column}' in session {session_id}. "
                    f"Available predictors: {available_columns}"
                )
            return target_column
    
    def _remove_target_columns(self, session_id: str, records: List[Dict[str, Any]], target_column: str = None) -> List[Dict[str, Any]]:
        """
        Remove target column from prediction records to avoid model conflicts.
        Validates that the predictor exists and removes the appropriate target column.
        
        Args:
            session_id: ID of the session
            records: List of record dictionaries
            target_column: Specific target column to remove, or None for auto-detect
            
        Returns:
            Cleaned records with target column removed
        """
        if not records:
            return records
            
        # Validate and get the target column name
        try:
            validated_target_column = self._validate_and_get_target_column(session_id, target_column)
        except ValueError as e:
            # Re-raise validation errors
            raise e
        
        if validated_target_column in records[0]:
            print(f"⚠️  Warning: Removing target column '{validated_target_column}' from prediction data")
            print(f"   This column would interfere with model predictions.")
            
            # Remove target column from all records
            cleaned_records = []
            for record in records:
                cleaned_record = {k: v for k, v in record.items() if k != validated_target_column}
                cleaned_records.append(cleaned_record)
            return cleaned_records
        
        return records
    
    def _clean_numpy_values(self, data):
        """
        Recursively clean NaN, Inf, and other non-JSON-serializable values from data.
        Converts them to None which is JSON serializable.
        
        Args:
            data: Data structure to clean (dict, list, or primitive)
            
        Returns:
            Cleaned data structure
        """
        import math
        import numpy as np
        
        if isinstance(data, dict):
            return {k: self._clean_numpy_values(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._clean_numpy_values(v) for v in data]
        elif isinstance(data, (float, np.floating)):
            if math.isnan(data) or math.isinf(data):
                return None
            return float(data)  # Convert numpy floats to Python floats
        elif isinstance(data, (int, np.integer)):
            return int(data)  # Convert numpy ints to Python ints
        elif isinstance(data, (bool, np.bool_)):
            return bool(data)  # Convert numpy bools to Python bools
        elif isinstance(data, np.ndarray):
            return self._clean_numpy_values(data.tolist())  # Convert arrays to lists
        elif data is None or isinstance(data, (str, bool)):
            return data
        else:
            # Handle other numpy types or unknown types
            try:
                # Try to convert to a basic Python type
                if hasattr(data, 'item'):  # numpy scalar
                    value = data.item()
                    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                        return None
                    return value
                else:
                    return data
            except:
                # If all else fails, convert to string
                return str(data)
    
    def predict_csv_file(self, session_id: str, file_path: Path) -> Dict[str, Any]:
        """
        Make batch predictions on a CSV file.
        
        Args:
            session_id: ID of session with trained predictor
            file_path: Path to CSV file
            
        Returns:
            Batch prediction results
        """
        import pandas as pd
        from jsontables import JSONTablesEncoder
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        df = pd.read_csv(file_path)
        
        # Convert to JSON Tables format
        table_data = JSONTablesEncoder.from_dataframe(df)
        
        return self.predict_table(session_id, table_data)

    def run_predictions(self, session_id: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run predictions on provided records. Clean and fast for production use.
        
        Args:
            session_id: ID of session with trained predictor
            records: List of record dictionaries
            
        Returns:
            Dictionary with prediction results
        """
        # Make batch predictions
        batch_results = self.predict_records(session_id, records)
        predictions = batch_results['predictions']
        
        # Process predictions into clean format
        results = []
        for pred in predictions:
            if pred['prediction']:
                record_idx = pred['row_index']
                prediction = pred['prediction']
                predicted_class = max(prediction, key=prediction.get)
                confidence = prediction[predicted_class]
                
                results.append({
                    'record_index': record_idx,
                    'predicted_class': predicted_class,
                    'confidence': confidence,
                    'full_prediction': prediction,
                    'error': batch_results.get('error', None),
                    'full_prediction': pred
                })
        
        return {
            'predictions': results,
            'total_records': len(records),
            'successful_predictions': len(results),
            'failed_predictions': len(records) - len(results)
        }

    def update_prediction_label(self, prediction_id: str, user_label: str) -> Dict[str, Any]:
        """
        Update the label for a prediction to enable retraining.
        
        Args:
            prediction_id: UUID of the prediction to update
            user_label: Correct label provided by user
            
        Returns:
            Update confirmation with prediction details
        """
        data = {
            "prediction_id": prediction_id,
            "user_label": user_label
        }
        response_data = self._post_json(f"/compute/prediction/{prediction_id}/update_label", data)
        return response_data
    
    def get_session_predictions(self, session_id: str, corrected_only: bool = False, limit: int = 100) -> Dict[str, Any]:
        """
        Get predictions for a session, optionally filtered for corrected ones.
        
        Args:
            session_id: ID of session
            corrected_only: Only return predictions with user corrections
            limit: Maximum number of predictions to return
            
        Returns:
            List of predictions with metadata
        """
        params = {
            "corrected_only": corrected_only,
            "limit": limit
        }
        response_data = self._get_json(f"/compute/session/{session_id}/predictions", params=params)
        return response_data
    
    def create_retraining_batch(self, session_id: str) -> Dict[str, Any]:
        """
        Create a retraining batch from corrected predictions.
        
        Args:
            session_id: ID of session with corrected predictions
            
        Returns:
            Retraining batch information
        """
        response_data = self._post_json(f"/compute/session/{session_id}/create_retraining_batch", {})
        return response_data

    def evaluate_predictions(self, session_id: str, records: List[Dict[str, Any]], 
                           actual_values: List[str], target_column: str = None) -> Dict[str, Any]:
        """
        Evaluate predictions with accuracy calculation. Use this for testing/validation.
        
        Args:
            session_id: ID of session with trained predictor
            records: List of record dictionaries
            actual_values: List of actual target values for accuracy calculation
            target_column: Name of target column (for display purposes)
            
        Returns:
            Dictionary with prediction results and accuracy metrics
        """
        # Get predictions
        pred_results = self.run_predictions(session_id, records)
        
        # Calculate accuracy
        correct_predictions = 0
        total_predictions = 0
        confidence_scores = []
        
        for pred in pred_results['predictions']:
            record_idx = pred['record_index']
            if record_idx < len(actual_values):
                predicted_class = pred['predicted_class']
                actual = str(actual_values[record_idx])
                confidence = pred['confidence']
                
                confidence_scores.append(confidence)
                total_predictions += 1
                
                if predicted_class == actual:
                    correct_predictions += 1
        
        # Add accuracy metrics
        if total_predictions > 0:
            accuracy = correct_predictions / total_predictions
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            
            pred_results['accuracy_metrics'] = {
                'accuracy': accuracy,
                'correct_predictions': correct_predictions,
                'total_predictions': total_predictions,
                'average_confidence': avg_confidence,
                'target_column': target_column
            }
        
        return pred_results

    def run_csv_predictions(self, session_id: str, csv_file: str, target_column: str = None,
                           sample_size: int = None, remove_target: bool = True) -> Dict[str, Any]:
        """
        Run predictions on a CSV file with automatic accuracy calculation.
        
        Args:
            session_id: ID of session with trained predictor
            csv_file: Path to CSV file
            target_column: Name of target column (for accuracy calculation)
            sample_size: Number of records to test (None = all records)
            remove_target: Whether to remove target column from prediction input
            
        Returns:
            Dictionary with prediction results and accuracy metrics
        """
        import pandas as pd
        
        # Load CSV
        df = pd.read_csv(csv_file)
        
        # Handle target column
        actual_values = None
        if target_column and target_column in df.columns:
            actual_values = df[target_column].tolist()
            if remove_target:
                prediction_df = df.drop(target_column, axis=1)
            else:
                prediction_df = df
        else:
            prediction_df = df
        
        # Take sample ONLY if explicitly requested
        if sample_size and sample_size < len(prediction_df):
            sample_df = prediction_df.head(sample_size)
            if actual_values:
                actual_values = actual_values[:sample_size]
        else:
            sample_df = prediction_df
        
        # Convert to records
        records = sample_df.to_dict('records')
        
        # Run predictions with accuracy calculation
        return self.evaluate_predictions(
            session_id=session_id,
            records=records,
            actual_values=actual_values,
            target_column=target_column
        )

    def run_comprehensive_test(self, session_id: str, test_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a comprehensive test of the single predictor including individual and batch predictions.
        
        Args:
            session_id: ID of session with trained predictor
            test_data: Optional dict with 'csv_file', 'target_column', 'sample_size', 'test_records'
            
        Returns:
            Comprehensive test results
        """
        print("🧪 " + "="*60)
        print("🧪 COMPREHENSIVE SINGLE PREDICTOR TEST")
        print("🧪 " + "="*60)
        
        results = {
            'session_id': session_id,
            'individual_tests': [],
            'batch_test': None,
            'training_metrics': None,
            'session_models': None
        }
        
        # 1. Check session models
        print("\n1. 📦 Checking available models...")
        try:
            models_info = self.get_session_models(session_id)
            results['session_models'] = models_info
        except Exception as e:
            print(f"Error checking models: {e}")
        
        # 2. Get training metrics
        print("\n2. 📊 Getting training metrics...")
        try:
            metrics = self.get_training_metrics(session_id)
            results['training_metrics'] = metrics
            
            training_metrics = metrics['training_metrics']
            print(f"Target column: {training_metrics.get('target_column')}")
            print(f"Target type: {training_metrics.get('target_column_type')}")
            print(f"Training epochs: {len(training_metrics.get('training_info', []))}")
        except Exception as e:
            print(f"Error getting training metrics: {e}")
        
        # 3. Individual prediction tests
        print("\n3. 🎯 Testing individual predictions...")
        
        # Default test records if none provided
        default_test_records = [
            {"domain": "shell.com", "snippet": "fuel card rewards program", "keyword": "fuel card"},
            {"domain": "exxon.com", "snippet": "gas station locator and fuel cards", "keyword": "gas station"},
            {"domain": "amazon.com", "snippet": "buy books online", "keyword": "books"},
            {"domain": "bp.com", "snippet": "fleet fuel cards for business", "keyword": "fleet cards"},
        ]
        
        test_records = test_data.get('test_records', default_test_records) if test_data else default_test_records
        
        for i, record in enumerate(test_records):
            try:
                result = self.predict(session_id, record)
                prediction = result['prediction']
                
                # Get predicted class and confidence
                predicted_class = max(prediction, key=prediction.get)
                confidence = prediction[predicted_class]
                
                test_result = {
                    'record': record,
                    'prediction': prediction,
                    'predicted_class': predicted_class,
                    'confidence': confidence,
                    'success': True
                }
                
                results['individual_tests'].append(test_result)
                print(f"✅ Record {i+1}: {predicted_class} ({confidence*100:.1f}%)")
                
            except Exception as e:
                test_result = {
                    'record': record,
                    'error': str(e),
                    'success': False
                }
                results['individual_tests'].append(test_result)
                print(f"❌ Record {i+1}: Error - {e}")
        
        # 4. Batch prediction test
        print("\n4. 📊 Testing batch predictions...")
        
        if test_data and test_data.get('csv_file'):
            try:
                batch_results = self.run_csv_predictions(
                    session_id=session_id,
                    csv_file=test_data['csv_file'],
                    target_column=test_data.get('target_column'),
                    sample_size=test_data.get('sample_size', 100)
                )
                results['batch_test'] = batch_results
                
                # Summary
                if batch_results.get('accuracy_metrics'):
                    acc = batch_results['accuracy_metrics']
                    print(f"✅ Batch test completed: {acc['accuracy']*100:.2f}% accuracy")
                else:
                    print(f"✅ Batch test completed: {batch_results['successful_predictions']} predictions")
                    
            except Exception as e:
                print(f"❌ Batch test failed: {e}")
                results['batch_test'] = {'error': str(e)}
        else:
            print("📝 No CSV file provided for batch testing")
        
        # 5. Summary
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        
        individual_success = sum(1 for t in results['individual_tests'] if t['success'])
        print(f"Individual predictions: {individual_success}/{len(results['individual_tests'])} successful")
        
        if results['batch_test'] and 'accuracy_metrics' in results['batch_test']:
            acc = results['batch_test']['accuracy_metrics']
            print(f"Batch prediction accuracy: {acc['accuracy']*100:.2f}%")
            print(f"Average confidence: {acc['average_confidence']*100:.2f}%")
        
        if results['training_metrics']:
            tm = results['training_metrics']['training_metrics']
            print(f"Model trained on: {tm.get('target_column')} ({tm.get('target_column_type')})")
        
        print("\n🎉 Comprehensive test completed!")
        
        return results

    # =========================================================================
    # Other API Endpoints
    # =========================================================================
    
    def encode_records(self, session_id: str, query_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encode records using the embedding space.
        
        Args:
            session_id: ID of session with trained embedding space
            query_record: Record to encode
            
        Returns:
            Encoded vector representation
        """
        data = {"query_record": query_record}
        response_data = self._post_json(f"/compute/session/{session_id}/encode_records", data)
        return response_data
    
    def similarity_search(self, session_id: str, query_record: Dict[str, Any], k: int = 5) -> Dict[str, Any]:
        """
        Find similar records using vector similarity search.
        
        Args:
            session_id: ID of session with trained embedding space and vector DB
            query_record: Record to find similarities for
            k: Number of similar records to return
            
        Returns:
            List of similar records with distances
        """
        data = {"query_record": query_record}
        response_data = self._post_json(f"/compute/session/{session_id}/similarity_search", data)
        return response_data
    
    def get_projections(self, session_id: str) -> Dict[str, Any]:
        """
        Get 2D projections for visualization.
        
        Args:
            session_id: ID of session with generated projections
            
        Returns:
            Projection data for visualization
        """
        response_data = self._get_json(f"/compute/session/{session_id}/projections")
        return response_data

    def flush_predict_queues(self, session_id: str, show_progress: bool = True) -> Dict[str, Any]:
        """
        Process all queued predictions for a session using efficient batching.
        
        Args:
            session_id: ID of session with queued predictions
            show_progress: Whether to show progress for batch processing
            
        Returns:
            Dictionary with prediction results mapped by queue_id
        """
        if session_id not in self._prediction_queues or not self._prediction_queues[session_id]:
            return {"results": {}, "summary": {"total_queued": 0, "successful": 0, "failed": 0}}
        
        queued_records = self._prediction_queues[session_id]
        total_queued = len(queued_records)
        
        if show_progress:
            print(f"🚀 Processing {total_queued} queued predictions for session {session_id}...")
        
        # Extract records and metadata
        records_to_predict = []
        queue_metadata = {}
        
        for queued_item in queued_records:
            queue_id = queued_item['queue_id']
            record = queued_item['record']
            target_column = queued_item['target_column']
            
            records_to_predict.append(record)
            queue_metadata[len(records_to_predict) - 1] = {
                'queue_id': queue_id,
                'target_column': target_column
            }
        
        # Use existing batch prediction system
        try:
            # Get the target column for batch processing (use first record's target column)
            batch_target_column = None
            if queue_metadata:
                batch_target_column = list(queue_metadata.values())[0]['target_column']
            
            # Process using existing batch system
            batch_results = self.predict_records(
                session_id=session_id,
                records=records_to_predict,
                target_column=batch_target_column,
                show_progress_bar=show_progress
            )
            
            # Map batch results back to queue IDs
            results = {}
            successful = 0
            failed = 0
            
            predictions = batch_results.get('predictions', [])
            for prediction in predictions:
                row_index = prediction.get('row_index', 0)
                if row_index in queue_metadata:
                    queue_id = queue_metadata[row_index]['queue_id']
                    results[queue_id] = prediction
                    
                    if prediction.get('prediction') is not None:
                        successful += 1
                    else:
                        failed += 1
            
            # Clear the queue for this session
            self._prediction_queues[session_id] = []
            
            if show_progress:
                print(f"✅ Queue processing complete: {successful} successful, {failed} failed")
            
            return {
                "results": results,
                "summary": {
                    "total_queued": total_queued,
                    "successful": successful,
                    "failed": failed,
                    "batch_summary": batch_results.get('summary', {})
                }
            }
            
        except Exception as e:
            # Clear queue even on error to prevent stuck state
            self._prediction_queues[session_id] = []
            raise Exception(f"Error processing prediction queue: {str(e)}")
    
    def get_queue_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get status of prediction queue for a session.
        
        Args:
            session_id: Session ID to check
            
        Returns:
            Dictionary with queue status information
        """
        queue = self._prediction_queues.get(session_id, [])
        if not queue:
            return {"queued_count": 0, "queue_empty": True}
        
        # Calculate queue statistics
        oldest_timestamp = min(item['timestamp'] for item in queue)
        newest_timestamp = max(item['timestamp'] for item in queue)
        queue_age = time.time() - oldest_timestamp
        
        return {
            "queued_count": len(queue),
            "queue_empty": False,
            "oldest_queued_age_seconds": queue_age,
            "queue_time_span_seconds": newest_timestamp - oldest_timestamp,
            "queue_ids": [item['queue_id'] for item in queue[:10]]  # First 10 IDs
        }
    
    def clear_predict_queues(self, session_id: str = None) -> Dict[str, int]:
        """
        Clear prediction queues without processing them.
        
        Args:
            session_id: Specific session to clear, or None to clear all
            
        Returns:
            Dictionary with count of cleared items per session
        """
        cleared_counts = {}
        
        if session_id:
            # Clear specific session
            count = len(self._prediction_queues.get(session_id, []))
            self._prediction_queues[session_id] = []
            cleared_counts[session_id] = count
        else:
            # Clear all sessions
            for sid, queue in self._prediction_queues.items():
                cleared_counts[sid] = len(queue)
            self._prediction_queues.clear()
        
        return cleared_counts

    def predict_batch(self, session_id: str, records: List[Dict[str, Any]], 
                     target_column: str = None) -> PredictionBatch:
        """
        Create a prediction batch for instant cached lookups.
        
        Perfect for parameter sweeps, grid searches, and exploring prediction surfaces.
        Run your loops twice with identical code - first populates cache, second gets instant results.
        
        Args:
            session_id: ID of session with trained predictor
            records: List of all records you'll want to predict on
            target_column: Specific target column predictor to use
            
        Returns:
            PredictionBatch object with instant predict() method
            
        Example:
            # Generate all combinations you'll need
            records = []
            for i in range(10):
                for j in range(10):
                    records.append({"param1": i, "param2": j})
            
            # First run - populate cache with batch processing
            batch = client.predict_batch(session_id, records)
            
            # Second run - same loops but instant cache lookups
            results = []
            for i in range(10):
                for j in range(10):
                    record = {"param1": i, "param2": j}
                    result = batch.predict(record)  # Instant!
                    results.append(result)
        """
        # Create batch object
        batch = PredictionBatch(session_id, self, target_column)
        
        # Populate cache with batch predictions
        batch._populate_cache(records)
        
        return batch

    def predict_grid(self, session_id: str, degrees_of_freedom: int, 
                    grid_shape: tuple = None, target_column: str = None) -> 'PredictionGrid':
        """
        Create a prediction grid for exploring parameter surfaces with automatic visualization.
        
        Perfect for 1D curves, 2D heatmaps, and 3D surfaces with built-in plotting functions.
        
        Args:
            session_id: ID of session with trained predictor
            degrees_of_freedom: Number of dimensions (1, 2, or 3)
            grid_shape: Custom grid shape tuple (default: auto-sized)
            target_column: Specific target column predictor to use
            
        Returns:
            PredictionGrid object with predict() and plotting methods
            
        Example:
            # 2D parameter sweep with automatic plotting
            grid = client.predict_grid(session_id, degrees_of_freedom=2)
            grid.set_axis_labels(["Spend", "Campaign Type"])
            grid.set_axis_values(0, [100, 250, 500])
            grid.set_axis_values(1, ["search", "display", "social"])
            
            for i, spend in enumerate([100, 250, 500]):
                for j, campaign in enumerate(["search", "display", "social"]):
                    record = {"spend": spend, "campaign_type": campaign}
                    grid.predict(record, grid_position=(i, j))
            
            # Automatic visualization
            grid.plot_heatmap()  # 2D heatmap
            grid.plot_3d()       # 3D surface
            
            # Find optimal parameters
            optimal_pos = grid.get_optimal_position()
            print(f"Optimal parameters at grid position: {optimal_pos}")
        """
        return PredictionGrid(session_id, self, degrees_of_freedom, grid_shape, target_column)


class PredictionGrid:
    """
    Grid-based prediction batch with automatic matrix building and visualization.
    
    Perfect for exploring prediction surfaces across 1-3 dimensions with automatic plotting.
    Collects all predictions and batches them for efficiency.
    
    Usage:
        # 2D parameter sweep with automatic plotting
        grid = client.predict_grid(session_id, degrees_of_freedom=2)
        
        # Fill grid (records are collected, not predicted yet)
        for i, spend in enumerate([100, 250, 500]):
            for j, campaign in enumerate(["search", "display"]):
                record = {"spend": spend, "campaign_type": campaign}
                grid.predict(record, grid_position=(i, j))
        
        # Process all predictions in one batch
        grid.process_batch()
        
        # Now plot results
        grid.plot_heatmap()  # Automatic heatmap
        grid.plot_3d()       # 3D surface plot
    """
    
    def __init__(self, session_id: str, client: 'FeatrixSphereClient', degrees_of_freedom: int, 
                 grid_shape: tuple = None, target_column: str = None):
        self.session_id = session_id
        self.client = client
        self.degrees_of_freedom = degrees_of_freedom
        self.target_column = target_column
        
        # Initialize grid matrix based on degrees of freedom
        if grid_shape:
            self.grid_shape = grid_shape
        else:
            # Default grid sizes
            default_sizes = {1: (20,), 2: (10, 10), 3: (8, 8, 8)}
            self.grid_shape = default_sizes.get(degrees_of_freedom, (10,) * degrees_of_freedom)
        
        # Initialize matrices for different data types
        self._prediction_matrix = {}  # class_name -> matrix
        self._confidence_matrix = None
        self._filled_positions = set()
        
        # Batch collection system
        self._pending_records = {}  # grid_position -> record
        self._position_to_index = {}  # grid_position -> batch_index
        self._batch_processed = False
        
        # Metadata for plotting
        self._axis_labels = [f"Param {i+1}" for i in range(degrees_of_freedom)]
        self._axis_values = [[] for _ in range(degrees_of_freedom)]
        self._colormap = 'viridis'
        
        # Statistics
        self._stats = {'predictions': 0, 'batched': 0, 'errors': 0}
        
    def predict(self, record: Dict[str, Any], grid_position: tuple) -> Dict[str, str]:
        """
        Add record to grid for batch processing.
        
        Args:
            record: Record to predict
            grid_position: Tuple of grid coordinates (i,) for 1D, (i,j) for 2D, (i,j,k) for 3D
            
        Returns:
            Status message about queuing for batch processing
        """
        if len(grid_position) != self.degrees_of_freedom:
            raise ValueError(f"Grid position must have {self.degrees_of_freedom} dimensions, got {len(grid_position)}")
        
        # Check bounds
        for i, pos in enumerate(grid_position):
            if pos >= self.grid_shape[i]:
                raise ValueError(f"Grid position {pos} exceeds dimension {i} size {self.grid_shape[i]}")
        
        # Store record for batch processing
        self._pending_records[grid_position] = record
        
        return {
            "status": "queued_for_batch",
            "grid_position": grid_position,
            "total_queued": len(self._pending_records),
            "message": f"Record queued at position {grid_position}. Call process_batch() to run predictions."
        }
    
    def process_batch(self, show_progress: bool = True) -> Dict[str, Any]:
        """
        Process all queued records in a single batch prediction.
        
        Args:
            show_progress: Whether to show progress during batch processing
            
        Returns:
            Batch processing results
        """
        if not self._pending_records:
            return {"message": "No records to process", "processed": 0}
        
        if self._batch_processed:
            return {"message": "Batch already processed", "processed": len(self._filled_positions)}
        
        # Convert grid records to list for batch processing
        records_list = []
        position_mapping = {}
        
        for grid_pos, record in self._pending_records.items():
            batch_index = len(records_list)
            records_list.append(record)
            position_mapping[batch_index] = grid_pos
            self._position_to_index[grid_pos] = batch_index
        
        if show_progress:
            print(f"🚀 Processing {len(records_list)} grid positions in batch...")
        
        # Use existing batch prediction system
        try:
            batch_results = self.client.predict_records(
                session_id=self.session_id,
                records=records_list,
                target_column=self.target_column,
                show_progress_bar=show_progress
            )
            
            # Process results and populate matrices
            predictions = batch_results.get('predictions', [])
            successful = 0
            failed = 0
            
            for prediction in predictions:
                row_index = prediction.get('row_index', 0)
                if row_index in position_mapping:
                    grid_pos = position_mapping[row_index]
                    
                    if 'prediction' in prediction and prediction['prediction']:
                        prediction_probs = prediction['prediction']
                        
                        # Initialize matrices if first successful prediction
                        if not self._prediction_matrix:
                            self._initialize_matrices(prediction_probs.keys())
                        
                        # Store prediction results in matrices
                        for class_name, probability in prediction_probs.items():
                            self._prediction_matrix[class_name][grid_pos] = probability
                        
                        # Store confidence (highest probability)
                        max_class = max(prediction_probs, key=prediction_probs.get)
                        confidence = prediction_probs[max_class]
                        self._confidence_matrix[grid_pos] = confidence
                        
                        # Mark position as filled
                        self._filled_positions.add(grid_pos)
                        successful += 1
                    else:
                        failed += 1
                        self._stats['errors'] += 1
            
            self._stats['predictions'] = successful
            self._stats['batched'] = len(records_list)
            self._batch_processed = True
            
            # Clear pending records
            self._pending_records.clear()
            
            if show_progress:
                print(f"✅ Batch processing complete: {successful} successful, {failed} failed")
                print(f"📊 Grid filled: {len(self._filled_positions)} positions")
            
            return {
                "processed": len(records_list),
                "successful": successful,
                "failed": failed,
                "batch_results": batch_results
            }
            
        except Exception as e:
            self._stats['errors'] += len(records_list)
            raise Exception(f"Error processing grid batch: {str(e)}")
    
    def _initialize_matrices(self, class_names: list):
        """Initialize prediction matrices for each class."""
        import numpy as np
        
        for class_name in class_names:
            self._prediction_matrix[class_name] = np.full(self.grid_shape, np.nan)
        
        self._confidence_matrix = np.full(self.grid_shape, np.nan)
    
    def set_axis_labels(self, labels: list):
        """Set custom labels for axes."""
        if len(labels) != self.degrees_of_freedom:
            raise ValueError(f"Must provide {self.degrees_of_freedom} labels")
        self._axis_labels = labels
    
    def set_axis_values(self, axis_index: int, values: list):
        """Set actual values for an axis (for proper tick labels)."""
        if axis_index >= self.degrees_of_freedom:
            raise ValueError(f"Axis index {axis_index} exceeds degrees of freedom {self.degrees_of_freedom}")
        self._axis_values[axis_index] = values
    
    def plot_heatmap(self, class_name: str = None, figsize: tuple = (10, 8), title: str = None):
        """
        Plot 2D heatmap of prediction probabilities.
        
        Args:
            class_name: Specific class to plot (default: highest probability class)
            figsize: Figure size
            title: Custom title
        """
        if self.degrees_of_freedom != 2:
            raise ValueError("Heatmap plotting only supports 2D grids")
        
        if not self._batch_processed:
            raise ValueError("Must call process_batch() first")
        
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            raise ImportError("matplotlib required for plotting. Install with: pip install matplotlib")
        
        if not self._prediction_matrix:
            raise ValueError("No predictions processed yet. Call process_batch() first.")
        
        # Choose class to plot
        if class_name is None:
            # Use the class with highest average probability
            avg_probs = {}
            for cls, matrix in self._prediction_matrix.items():
                avg_probs[cls] = np.nanmean(matrix)
            class_name = max(avg_probs, key=avg_probs.get)
        
        matrix = self._prediction_matrix[class_name]
        
        # Create plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Transpose matrix for correct matplotlib display orientation
        # matplotlib imshow: first dimension = Y-axis (vertical), second = X-axis (horizontal)
        # So we need to transpose to get axis 0 on X-axis and axis 1 on Y-axis
        display_matrix = matrix.T
        
        # Plot heatmap with transposed matrix
        im = ax.imshow(display_matrix, cmap=self._colormap, aspect='auto', origin='lower')
        
        # Set labels (axis 0 = X-axis, axis 1 = Y-axis after transpose)
        ax.set_xlabel(self._axis_labels[0])
        ax.set_ylabel(self._axis_labels[1])
        
        # Set tick labels if axis values provided (adjusted for transpose)
        if self._axis_values[0]:
            ax.set_xticks(range(len(self._axis_values[0])))
            ax.set_xticklabels(self._axis_values[0])
        if self._axis_values[1]:
            ax.set_yticks(range(len(self._axis_values[1])))
            ax.set_yticklabels(self._axis_values[1])
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label(f'Probability of {class_name}')
        
        # Set title
        if title is None:
            title = f'Prediction Heatmap: {class_name}'
        ax.set_title(title)
        
        plt.tight_layout()
        return fig, ax
    
    def plot_3d(self, class_name: str = None, figsize: tuple = (12, 9), title: str = None,
                 value_filter: tuple = None, opacity: float = 0.8, show_wireframe: bool = False):
        """
        Plot 3D surface of prediction probabilities with filtering and opacity controls.
        
        Args:
            class_name: Specific class to plot (default: highest probability class)
            figsize: Figure size
            title: Custom title
            value_filter: Tuple (min_value, max_value) to filter displayed predictions
            opacity: Surface opacity (0.0 = transparent, 1.0 = opaque)
            show_wireframe: Whether to show wireframe overlay for better shape visibility
        """
        if self.degrees_of_freedom != 2:
            raise ValueError("3D surface plotting only supports 2D grids")
        
        if not self._batch_processed:
            raise ValueError("Must call process_batch() first")
        
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from mpl_toolkits.mplot3d import Axes3D
        except ImportError:
            raise ImportError("matplotlib required for plotting. Install with: pip install matplotlib")
        
        if not self._prediction_matrix:
            raise ValueError("No predictions processed yet. Call process_batch() first.")
        
        # Choose class to plot
        if class_name is None:
            avg_probs = {}
            for cls, matrix in self._prediction_matrix.items():
                avg_probs[cls] = np.nanmean(matrix)
            class_name = max(avg_probs, key=avg_probs.get)
        
        matrix = self._prediction_matrix[class_name].copy()
        
        # Apply value filter if specified
        if value_filter is not None:
            min_val, max_val = value_filter
            # Mask values outside the filter range
            mask = (matrix < min_val) | (matrix > max_val)
            matrix[mask] = np.nan
        
        # Create meshgrid with proper axis orientation
        x = np.arange(matrix.shape[0])  # axis 0
        y = np.arange(matrix.shape[1])  # axis 1
        X, Y = np.meshgrid(x, y, indexing='ij')
        
        # Create 3D plot
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot surface with specified opacity
        surf = ax.plot_surface(X, Y, matrix, cmap=self._colormap, alpha=opacity)
        
        # Add wireframe if requested (helps see shape)
        if show_wireframe:
            ax.plot_wireframe(X, Y, matrix, alpha=0.3, color='black', linewidth=0.5)
        
        # Set labels (axis 0 = X-axis, axis 1 = Y-axis)
        ax.set_xlabel(self._axis_labels[0])
        ax.set_ylabel(self._axis_labels[1])
        ax.set_zlabel(f'Probability of {class_name}')
        
        # Set tick labels if axis values provided
        if self._axis_values[0]:
            ax.set_xticks(range(len(self._axis_values[0])))
            ax.set_xticklabels(self._axis_values[0])
        if self._axis_values[1]:
            ax.set_yticks(range(len(self._axis_values[1])))
            ax.set_yticklabels(self._axis_values[1])
        
        # Add colorbar
        cbar = fig.colorbar(surf, ax=ax, shrink=0.5)
        cbar.set_label(f'Probability of {class_name}')
        
        # Set title with filter info
        if title is None:
            title = f'3D Prediction Surface: {class_name}'
            if value_filter:
                title += f' (filtered: {value_filter[0]:.3f}-{value_filter[1]:.3f})'
        ax.set_title(title)
        
        return fig, ax
    
    def plot_3d_interactive(self, class_name: str = None, figsize: tuple = (12, 9)):
        """
        Create interactive 3D plot with sliders for filtering and opacity control.
        
        Perfect for Jupyter notebooks - provides sliders to explore the prediction surface.
        
        Args:
            class_name: Specific class to plot (default: highest probability class)
            figsize: Figure size
            
        Returns:
            Interactive widget (in Jupyter) or regular plot (elsewhere)
        """
        if self.degrees_of_freedom != 2:
            raise ValueError("Interactive 3D plotting only supports 2D grids")
        
        if not self._batch_processed:
            raise ValueError("Must call process_batch() first")
        
        # Check if we're in a Jupyter environment
        try:
            from IPython.display import display
            from ipywidgets import interact, FloatSlider, FloatRangeSlider, Checkbox
            import numpy as np
            jupyter_available = True
        except ImportError:
            print("⚠️ Interactive widgets require Jupyter and ipywidgets")
            print("   Install with: pip install ipywidgets")
            print("   Falling back to static 3D plot...")
            return self.plot_3d(class_name=class_name, figsize=figsize)
        
        if not self._prediction_matrix:
            raise ValueError("No predictions processed yet. Call process_batch() first.")
        
        # Choose class to plot
        if class_name is None:
            avg_probs = {}
            for cls, matrix in self._prediction_matrix.items():
                avg_probs[cls] = np.nanmean(matrix)
            class_name = max(avg_probs, key=avg_probs.get)
        
        matrix = self._prediction_matrix[class_name]
        
        # Get value range for sliders
        min_val = float(np.nanmin(matrix))
        max_val = float(np.nanmax(matrix))
        value_range = max_val - min_val
        
        print(f"🎛️ Interactive 3D Surface Explorer: {class_name}")
        print(f"   Value range: {min_val:.4f} to {max_val:.4f}")
        print("   Use sliders below to filter and adjust opacity")
        
        # Create interactive plot function
        def update_plot(value_range=(min_val, max_val), opacity=0.8, wireframe=False):
            """Update the 3D plot based on slider values."""
            import matplotlib.pyplot as plt
            plt.close('all')  # Close previous plots
            
            fig, ax = self.plot_3d(
                class_name=class_name,
                figsize=figsize,
                value_filter=value_range,
                opacity=opacity,
                show_wireframe=wireframe
            )
            
            # Show current filter stats
            filtered_matrix = matrix.copy()
            mask = (filtered_matrix < value_range[0]) | (filtered_matrix > value_range[1])
            filtered_matrix[mask] = np.nan
            
            visible_count = np.sum(~np.isnan(filtered_matrix))
            total_count = np.sum(~np.isnan(matrix))
            visible_percent = (visible_count / total_count) * 100 if total_count > 0 else 0
            
            print(f"📊 Showing {visible_count}/{total_count} points ({visible_percent:.1f}%)")
            plt.show()
        
        # Create interactive widgets
        value_slider = FloatRangeSlider(
            value=(min_val, max_val),
            min=min_val,
            max=max_val,
            step=value_range / 100,
            description='Value Filter:',
            continuous_update=False,
            style={'description_width': 'initial'}
        )
        
        opacity_slider = FloatSlider(
            value=0.8,
            min=0.1,
            max=1.0,
            step=0.1,
            description='Opacity:',
            continuous_update=False,
            style={'description_width': 'initial'}
        )
        
        wireframe_checkbox = Checkbox(
            value=False,
            description='Show Wireframe',
            style={'description_width': 'initial'}
        )
        
        # Create interactive widget
        return interact(
            update_plot,
            value_range=value_slider,
            opacity=opacity_slider,
            wireframe=wireframe_checkbox
        )
    
    def plot_1d(self, class_name: str = None, figsize: tuple = (10, 6), title: str = None):
        """
        Plot 1D line plot of prediction probabilities.
        
        Args:
            class_name: Specific class to plot (default: highest probability class)
            figsize: Figure size
            title: Custom title
        """
        if self.degrees_of_freedom != 1:
            raise ValueError("1D plotting only supports 1D grids")
        
        if not self._batch_processed:
            raise ValueError("Must call process_batch() first")
        
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            raise ImportError("matplotlib required for plotting. Install with: pip install matplotlib")
        
        if not self._prediction_matrix:
            raise ValueError("No predictions processed yet. Call process_batch() first.")
        
        # Choose class to plot
        if class_name is None:
            avg_probs = {}
            for cls, matrix in self._prediction_matrix.items():
                avg_probs[cls] = np.nanmean(matrix)
            class_name = max(avg_probs, key=avg_probs.get)
        
        matrix = self._prediction_matrix[class_name]
        
        # Create plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # X values
        x = self._axis_values[0] if self._axis_values[0] else range(len(matrix))
        
        # Plot line
        ax.plot(x, matrix, marker='o', linewidth=2, markersize=6)
        
        # Set labels
        ax.set_xlabel(self._axis_labels[0])
        ax.set_ylabel(f'Probability of {class_name}')
        
        # Set title
        if title is None:
            title = f'Prediction Curve: {class_name}'
        ax.set_title(title)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return fig, ax
    
    def get_optimal_position(self, class_name: str = None) -> tuple:
        """
        Find grid position with highest probability for a class.
        
        Args:
            class_name: Class to optimize for (default: highest average probability)
            
        Returns:
            Grid position tuple with highest probability
        """
        import numpy as np
        
        if not self._batch_processed:
            raise ValueError("Must call process_batch() first")
        
        if not self._prediction_matrix:
            raise ValueError("No predictions processed yet. Call process_batch() first.")
        
        if class_name is None:
            avg_probs = {}
            for cls, matrix in self._prediction_matrix.items():
                avg_probs[cls] = np.nanmean(matrix)
            class_name = max(avg_probs, key=avg_probs.get)
        
        matrix = self._prediction_matrix[class_name]
        optimal_idx = np.unravel_index(np.nanargmax(matrix), matrix.shape)
        
        return optimal_idx
    
    def get_stats(self) -> Dict[str, Any]:
        """Get grid statistics."""
        import numpy as np
        
        total_positions = int(np.prod(self.grid_shape))
        filled_ratio = len(self._filled_positions) / total_positions if total_positions > 0 else 0
        
        return {
            'grid_shape': self.grid_shape,
            'degrees_of_freedom': self.degrees_of_freedom,
            'total_positions': total_positions,
            'filled_positions': len(self._filled_positions),
            'fill_ratio': filled_ratio,
            'pending_records': len(self._pending_records),
            'batch_processed': self._batch_processed,
            'predictions_made': self._stats['predictions'],
            'errors': self._stats['errors'],
            'available_classes': list(self._prediction_matrix.keys()) if self._prediction_matrix else []
        }
    
    def export_data(self) -> Dict[str, Any]:
        """Export grid data for external analysis."""
        import numpy as np
        
        if not self._batch_processed:
            raise ValueError("Must call process_batch() first")
        
        return {
            'prediction_matrices': {cls: matrix.tolist() for cls, matrix in self._prediction_matrix.items()},
            'confidence_matrix': self._confidence_matrix.tolist() if self._confidence_matrix is not None else None,
            'grid_shape': self.grid_shape,
            'axis_labels': self._axis_labels,
            'axis_values': self._axis_values,
            'filled_positions': list(self._filled_positions),
            'stats': self.get_stats()
        }


def main():
    """Example usage of the API client."""
    
    # Initialize client
    client = FeatrixSphereClient("https://sphere-api.featrix.com")
    
    print("=== Featrix Sphere API Client Test ===\n")
    
    try:
        # Example 1: Create a session and check status
        print("1. Creating a new session...")
        session_info = client.create_session("sphere")
        print(f"Session created: {session_info.session_id}\n")
        
        # Example 2: Check session status
        print("2. Checking session status...")
        current_status = client.get_session_status(session_info.session_id)
        print(f"Current status: {current_status.status}\n")
        
        # Example 3: Upload a file (if test data exists)
        test_file = Path("featrix_data/test.csv")
        if test_file.exists():
            print("3. Uploading test file...")
            upload_session = client.upload_file_and_create_session(test_file)
            print(f"Upload session: {upload_session.session_id}\n")
        else:
            print("3. Skipping file upload (test.csv not found)\n")
        
        print("API client test completed successfully!")
        
    except Exception as e:
        print(f"Error during API client test: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 