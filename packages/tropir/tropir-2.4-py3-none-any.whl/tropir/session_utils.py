import threading
import uuid
import os # Import os for environment variables
import logging # Import logging
import functools
from contextlib import contextmanager
import requests # Added for monkey-patching
import httpx # Added for httpx patching
from urllib.parse import urlparse # Added for URL parsing
import inspect # Added for checking async functions
import json # Added for JSON parsing and printing
import asyncio # Added for async operations
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import pickle  # For serializing session context in process pool
import weakref  # For weak references to prevent memory leaks
import atexit   # For cleanup on process exit
import time
import collections.abc
import sys  # Added for frame inspection
import traceback  # Added for stack traces
import copy  # Added for deep copying variables
from typing import Any, Dict, Optional, Union  # Added for type hints
import subprocess  # Added for git commands
import platform  # Added for system info
import pkg_resources  # Added for package versions

def _trigger_auto_evaluation(session_id: str, user_id: str = None):
    """
    Trigger automatic evaluation for a completed session.
    
    Args:
        session_id: The session ID that just completed
        user_id: User ID (will be looked up from API key if not provided)
    """
    try:
        # Import the evaluator runner
        import sys
        import os
        api_path = os.path.join(os.getcwd(), 'api')
        if api_path not in sys.path:
            sys.path.append(api_path)
        
        # Load environment variables from the api directory
        from dotenv import load_dotenv
        load_dotenv(os.path.join(api_path, '.env'))
        
        from utils.evaluator_runner import auto_evaluate_session
        from utils.database import supabase
        
        # Get user ID if not provided
        if not user_id:
            user_id = _get_user_id_from_api_key()
        
        if not user_id:
            logging.debug(f"⚠️ Tropir: Could not determine user ID for auto-evaluation of session {session_id}")
            return
        
        # Get session data from pipeline traces
        trace_result = supabase.table('pipeline_traces').select('text_flow').eq('session_id', session_id).limit(1).execute()
        
        if not trace_result.data:
            logging.debug(f"⚠️ Tropir: No session data found for auto-evaluation of session {session_id}")
            return
        
        session_data = trace_result.data[0].get('text_flow', {})
        
        if not session_data:
            logging.debug(f"⚠️ Tropir: Empty session data for auto-evaluation of session {session_id}")
            return
        
        # Run evaluations asynchronously to avoid blocking session completion
        import threading
        
        def run_evaluations():
            try:
                summary = auto_evaluate_session(session_id, user_id, session_data)
                logging.info(f"✅ Tropir: Auto-evaluation completed for session {session_id} - {summary['successful']} successful, {summary['failed']} failed")
            except Exception as e:
                logging.error(f"⚠️ Tropir: Auto-evaluation failed for session {session_id}: {e}")
        
        eval_thread = threading.Thread(target=run_evaluations, daemon=True)
        eval_thread.start()
        
        logging.debug(f"🔄 Tropir: Started auto-evaluation thread for session {session_id}")
        
    except Exception as e:
        logging.debug(f"⚠️ Tropir: Auto-evaluation trigger failed for session {session_id}: {e}")

# Define thread-local storage
_thread_local = threading.local()

# This will allow us to maintain session continuity between threads
_global_sessions_by_name = {}
_global_session_managers = {}

# Global parent thread tracker
_parent_thread_sessions = {}

# Async context tracking by task
_async_task_sessions = {}

# Task creation tracking to handle nested tasks
_async_task_parents = {}

# Track sessions by event loop to handle multiple event loops
_loop_sessions = {}

# Global store for span metadata (keyed by session_id)
_global_span_metadata = {}

# Add a lock for thread-safe operations
_session_lock = threading.RLock()

# Process-specific session ID
_process_session_id = os.getpid()

# Global span storage per session
_session_spans = {}

# NEW: Global store for LLM call tracking
_llm_call_context = {}
_current_llm_call_id = threading.local()

# NEW: Global prompt tracking for parameter passing
_prompt_metadata = {}  # Maps prompt values to their metadata
_prompt_value_to_id = {}  # Maps prompt text to prompt ID for reverse lookup

class Span:
    """
    Span class for session metadata annotation.
    Provides add(key, value) method for arbitrary metadata collection.
    """
    
    def __init__(self, session_id: str, session_name: str = None):
        self.session_id = session_id
        self.session_name = session_name
        self.metadata = {}
        self._key_counters = {}
        
    def add(self, key: str, value: Any) -> None:
        """
        Add metadata to the session span and send it to the metadata endpoint.
        
        Args:
            key: The metadata key (becomes the step name/title)
            value: The metadata value (any JSON-serializable type)
        """
        original_key = key
        
        # Handle reserved key 'tropir_prompts'
        if key == "tropir_prompts":
            logging.warning(f"Key 'tropir_prompts' is reserved. Adding suffix.")
            key = "tropir_prompts_1"
        
        # Handle duplicate keys with auto-suffixing
        if key in self.metadata:
            if original_key not in self._key_counters:
                self._key_counters[original_key] = 1
            self._key_counters[original_key] += 1
            key = f"{original_key}_{self._key_counters[original_key]}"
        
        # Store the metadata
        self.metadata[key] = value
        
        # Update the pipeline trace immediately
        self._update_pipeline_trace()
        
        # Send metadata to endpoint (like old add_step functionality)
        self._send_metadata_step(key, value)
        
        logging.debug(f"Span: Added metadata key '{key}' for session {self.session_id}")
    
    def _send_metadata_step(self, step_name: str, data: Any):
        """
        Send metadata step to the endpoint to create a metadata log entry.
        Based on the old add_step functionality.
        
        Args:
            step_name: The step name (becomes the title of the metadata card)
            data: The metadata to send
        """
        # Prepare the payload
        payload = {
            "session_id": self.session_id,
            "metadata": data
        }
        
        if self.session_name:
            payload["session_name"] = self.session_name
            
        if step_name:
            payload["step_name"] = step_name
        
        # Determine the endpoint
        endpoint = os.environ.get("TROPIR_METADATA_ENDPOINT", get_default_metadata_endpoint())
        
        # Setup headers with Tropir headers
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add Tropir headers (including API key for target hosts)
        _add_tropir_headers(headers, endpoint)
        
        # Check if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            is_async = True
        except RuntimeError:
            is_async = False
        
        # Handle synchronous case
        if not is_async:
            try:
                # Use the patched requests library to send the metadata
                # Create and prepare a Request object to properly use the patched send
                req = requests.Request('POST', endpoint, json=payload, headers=headers)
                prepared_req = req.prepare()
                
                logging.info(f"Tropir Span: Sending metadata step (sync) to {endpoint}. Payload: {json.dumps(payload)}")
                
                # Use a session to send (will use the patched send method)
                with requests.Session() as s:
                    response = s.send(prepared_req)
                
                if response.status_code >= 400:
                    logging.warning(f"Failed to send metadata: {response.status_code} - {response.text}")
                else:
                    logging.debug(f"Successfully sent metadata step '{step_name}' for session {self.session_name or 'unnamed'}")
                    
                return response
            except Exception as e:
                logging.warning(f"Error sending metadata step '{step_name}': {str(e)}")
                return None
        
        # Handle asynchronous case
        else:
            # Create a future that will call httpx in a thread to avoid blocking
            async def _async_send():
                try:
                    # Create an httpx request to use the patched send method
                    async with httpx.AsyncClient() as client:
                        # httpx.Request will be processed by the patched send method
                        logging.info(f"Tropir Span: Sending metadata step (async) to {endpoint}. Payload: {json.dumps(payload)}")
                        request = httpx.Request('POST', endpoint, json=payload, headers=headers)
                        response = await client.send(request)
                        
                        if response.status_code >= 400:
                            logging.warning(f"Failed to send metadata: {response.status_code} - {response.text}")
                        else:
                            logging.debug(f"Successfully sent metadata step '{step_name}' for session {self.session_name or 'unnamed'}")
                            
                        return response
                except Exception as e:
                    logging.warning(f"Error sending metadata step '{step_name}': {str(e)}")
                    return None
            
            # Start the async task but don't wait for it
            asyncio.create_task(_async_send())
    
    def _update_pipeline_trace(self):
        """Update the pipeline trace with current metadata"""
        try:
            # Import database here to avoid circular imports
            import sys
            import os
            api_path = os.path.join(os.getcwd(), '../tropir/api')
            if api_path not in sys.path:
                sys.path.append(api_path)
            
            # Load environment variables from the api directory
            from dotenv import load_dotenv
            load_dotenv(os.path.join(api_path, '.env'))
            
            from utils.database import supabase
            
            # Get current metadata and merge with span metadata
            response = supabase.table('pipeline_traces').select('metadata').eq('session_id', self.session_id).limit(1).execute()
            
            current_metadata = {}
            if response.data:
                current_metadata = response.data[0].get('metadata', {})
                # Merge span metadata into metadata column
                updated_metadata = {**current_metadata, **self.metadata}
                
                # Update the pipeline trace with new metadata column
                update_response = supabase.table('pipeline_traces').update({
                    'metadata': updated_metadata,
                    'last_update': 'now()'
                }).eq('session_id', self.session_id).execute()
                
                logging.debug(f"Updated existing pipeline trace with {len(self.metadata)} metadata items for session {self.session_id}")
            else:
                # Store metadata globally for later pickup when trace is created
                global _global_span_metadata
                _global_span_metadata[self.session_id] = self.metadata.copy()
                
                # Also store in a temporary file for cross-process access
                try:
                    import tempfile
                    import json
                    temp_dir = tempfile.gettempdir()
                    metadata_file = os.path.join(temp_dir, f"tropir_metadata_{self.session_id}.json")
                    with open(metadata_file, 'w') as f:
                        json.dump(self.metadata, f)
                    logging.debug(f"Stored {len(self.metadata)} metadata items for session {self.session_id} (global + file)")
                except Exception as file_error:
                    logging.debug(f"Could not store metadata to file: {file_error}")
                    logging.debug(f"Stored {len(self.metadata)} metadata items globally for session {self.session_id}")
            
        except Exception as e:
            logging.debug(f"Could not update pipeline trace for span metadata: {e}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get all metadata from this span"""
        return self.metadata.copy()

def get_stored_span_metadata(session_id: str, cleanup: bool = True) -> Dict[str, Any]:
    """
    Get any stored span metadata for a session ID.
    This is used when creating pipeline traces to pick up metadata
    that was added before the trace existed.
    
    Args:
        session_id: The session ID to get metadata for
        cleanup: Whether to clean up the stored metadata after retrieval
        
    Returns:
        Dictionary of stored metadata, empty dict if none
    """
    global _global_span_metadata
    # First try global store (same process)
    metadata = _global_span_metadata.get(session_id, {})
    
    # If not found globally, try file-based store (cross-process)
    if not metadata:
        try:
            import tempfile
            import json
            import os
            temp_dir = tempfile.gettempdir()
            metadata_file = os.path.join(temp_dir, f"tropir_metadata_{session_id}.json")
            
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                # Clean up file if requested
                if cleanup:
                    os.remove(metadata_file)
                    
        except Exception as e:
            logging.debug(f"Error reading metadata file: {e}")
    
    # Clean up global store if requested
    if cleanup and session_id in _global_span_metadata:
        del _global_span_metadata[session_id]
    
    return metadata

def get_current_span() -> Optional[Span]:
    """
    Get the current span for the active session.
    
    Returns:
        Span object for the current session, or None if no active session
    """
    session_id = get_session_id()
    if not session_id:
        return None
    
    # Return existing span or create a new one
    if session_id not in _session_spans:
        session_name = get_session_name()
        _session_spans[session_id] = Span(session_id, session_name)
    
    return _session_spans[session_id]

def ensure_pipeline_trace_exists(session_id: str = None, user_id: str = None) -> bool:
    """
    Ensure a pipeline trace exists for the current session.
    This forces immediate creation of the trace with any pending metadata.
    
    Args:
        session_id: Optional session ID (uses current if not provided)
        user_id: Optional user ID (looks up from API key if not provided)
    
    Returns:
        bool: True if trace exists or was created, False otherwise
    """
    if not session_id:
        session_id = get_session_id()
    
    if not session_id:
        logging.warning("No session ID available for trace creation")
        return False
    
    if not user_id:
        user_id = _get_user_id_from_api_key()
    
    if not user_id:
        logging.warning("No user ID available for trace creation")
        return False
    
    try:
        # Import database here to avoid circular imports
        import sys
        import os
        api_path = os.path.join(os.getcwd(), '../tropir/api')
        if api_path not in sys.path:
            sys.path.append(api_path)
        
        from dotenv import load_dotenv
        load_dotenv(os.path.join(api_path, '.env'))
        
        from utils.database import supabase
        from datetime import datetime
        
        # Check if trace already exists
        trace_response = supabase.table('pipeline_traces').select("session_id").eq("session_id", session_id).eq("user_id", user_id).limit(1).execute()
        
        if trace_response.data:
            logging.debug(f"Pipeline trace already exists for session {session_id}")
            
            # Update with any pending metadata
            if session_id in _session_spans:
                span = _session_spans[session_id]
                if span.metadata:
                    # Get current metadata and merge
                    meta_response = supabase.table('pipeline_traces').select('metadata').eq('session_id', session_id).limit(1).execute()
                    current_metadata = meta_response.data[0].get('metadata', {}) if meta_response.data else {}
                    updated_metadata = {**current_metadata, **span.metadata}
                    
                    # Update the trace
                    supabase.table('pipeline_traces').update({
                        'metadata': updated_metadata,
                        'last_update': datetime.utcnow().isoformat() + "Z"
                    }).eq('session_id', session_id).execute()
                    
                    logging.debug(f"Updated existing trace with {len(span.metadata)} metadata items")
            
            return True
        
        # Create new trace
        session_name = get_session_name()
        now_iso = datetime.utcnow().isoformat() + "Z"
        
        # Get any stored metadata
        stored_metadata = get_stored_span_metadata(session_id, cleanup=False)
        
        # Also get metadata from current span if it exists
        if session_id in _session_spans:
            span = _session_spans[session_id]
            if span.metadata:
                stored_metadata = {**stored_metadata, **span.metadata}
        
        trace_data = {
            "session_id": session_id,
            "user_id": user_id,
            "start_time": now_iso,
            "last_update": now_iso,
            "status": "active",
            "log_ids": [],
            "template_sequence": [],
            "text_flow": [],
            "name": session_name,
            "metadata": stored_metadata
        }
        
        try:
            response = supabase.table('pipeline_traces').insert(trace_data).execute()
            
            # Clean up stored metadata now that it's in the database
            get_stored_span_metadata(session_id, cleanup=True)
            
            logging.info(f"✅ Created pipeline trace for session {session_id} with {len(stored_metadata)} metadata items")
            return True
        except Exception as e:
            # Handle race condition - if trace already exists, update it with metadata
            if "duplicate key" in str(e).lower() or "23505" in str(e):
                logging.info(f"🔄 Race condition detected - updating existing trace with metadata for session {session_id}")
                try:
                    # Get current trace and merge metadata
                    existing_response = supabase.table('pipeline_traces').select('metadata').eq('session_id', session_id).limit(1).execute()
                    current_metadata = {}
                    if existing_response.data:
                        current_metadata = existing_response.data[0].get('metadata', {})
                    
                    # Merge with new metadata
                    merged_metadata = {**current_metadata, **stored_metadata}
                    
                    # Update the trace
                    supabase.table('pipeline_traces').update({
                        'metadata': merged_metadata,
                        'last_update': datetime.utcnow().isoformat() + "Z"
                    }).eq('session_id', session_id).execute()
                    
                    # Clean up stored metadata now that it's merged
                    get_stored_span_metadata(session_id, cleanup=True)
                    
                    logging.info(f"✅ Updated existing pipeline trace with metadata for session {session_id}")
                    return True
                except Exception as update_error:
                    logging.error(f"Failed to update existing trace with metadata: {update_error}")
                    return False
            else:
                logging.error(f"Failed to create pipeline trace: {e}")
                return False
        
    except Exception as e:
        logging.error(f"Failed to ensure pipeline trace exists: {e}")
        import traceback
        traceback.print_exc()
        return False

# === TROPIR SDK LITE INTEGRATION ===
# Global state for rerun mode and automatic variable tracking
_rerun_mode = None
_state_variables = {}
_prompts = {}
_session_execution_data = {}  # Store captured variables and prompts per session
_variable_tracker = {}  # Track variable access patterns
_prompt_registry = {}  # Registry of all prompts used
_execution_context = {}  # Store execution context per session
_rerun_session_id = None  # New session ID for rerun results
_original_session_id = None  # Original session being rerun

def _check_rerun_mode():
    """Check environment and enter rerun mode if needed"""
    global _rerun_mode, _state_variables, _prompts, _rerun_session_id, _original_session_id
    
    # Always check current environment variables (don't cache)
    rerun_env = os.environ.get("TROPIR_RERUN_MODE")
    if rerun_env == "true":
        # Only update if rerun mode changed or variables changed
        current_session_id = os.environ.get("TROPIR_RERUN_SESSION_ID")
        current_original_id = os.environ.get("TROPIR_ORIGINAL_SESSION_ID")
        
        # Update rerun mode and session IDs
        _rerun_mode = True
        _rerun_session_id = current_session_id
        _original_session_id = current_original_id
        
        logging.info(f"🔄 Tropir: In rerun mode - new session: {_rerun_session_id}, original: {_original_session_id}")
        
        # Parse state variables (always reparse to catch updates)
        try:
            state_json = os.environ.get("TROPIR_STATE_VARIABLES", "{}")
            new_state_variables = json.loads(state_json)
            
            # Only log if variables actually changed
            if new_state_variables != _state_variables:
                _state_variables = new_state_variables
                logging.info(f"📥 Tropir: Loaded {len(_state_variables)} state variables for rerun")
                if _state_variables:
                    logging.info(f"📊 Tropir: State variables: {list(_state_variables.keys())}")
        except Exception as e:
            logging.warning(f"⚠️ Tropir: Failed to parse state variables: {e}")
            _state_variables = {}
        
        # Parse prompts (always reparse to catch updates)
        try:
            prompts_json = os.environ.get("TROPIR_PROMPTS", "{}")
            new_prompts = json.loads(prompts_json)
            
            # Only log if prompts actually changed
            if new_prompts != _prompts:
                _prompts = new_prompts
                logging.info(f"📥 Tropir: Loaded {len(_prompts)} prompts for rerun")
                if _prompts:
                    logging.info(f"📝 Tropir: Prompts: {list(_prompts.keys())}")
        except Exception as e:
            logging.warning(f"⚠️ Tropir: Failed to parse prompts: {e}")
            _prompts = {}
    else:
        # Only update if not already in normal mode
        if _rerun_mode is not False:
            _rerun_mode = False
            _rerun_session_id = None
            _original_session_id = None
            _state_variables = {}
            _prompts = {}
            logging.info("🆕 Tropir: Running in normal mode with explicit variable tracking")

def tropir_variable(key: str, value: Any) -> Any:
    """
    Smart variable that returns rerun value if available, otherwise default.
    Use this to track any value you want to be able to change during rerun.
    
    Usage:
        user_id = tropir_variable("user_id", "user_123")
        temperature = tropir_variable("temperature", 0.7)
        context = tropir_variable("context", retrieve_data())
    """
    _check_rerun_mode()
    
    # Get current session for tracking
    session_id = get_session_id()
    
    if session_id and session_id not in _session_execution_data:
        _session_execution_data[session_id] = {"variables": {}, "prompts": {}}
    
    # Debug logging
    logging.debug(f"🔍 Tropir: tropir_variable('{key}') called - rerun_mode: {_rerun_mode}, has_key: {key in _state_variables}")
    
    if _rerun_mode and key in _state_variables:
        result_value = _state_variables[key]
        logging.info(f"🔄 Tropir: Using rerun variable '{key}': {repr(result_value)} (original: {repr(value)})")
    else:
        result_value = value
        if _rerun_mode:
            logging.debug(f"⚠️ Tropir: Variable '{key}' not found in rerun state, using default: {repr(value)}")
        else:
            logging.debug(f"📝 Tropir: Normal mode - using default value for '{key}': {repr(value)}")
        
    # Track this variable usage
    if session_id:
        _session_execution_data[session_id]["variables"][key] = result_value
        
        # Create a log entry directly (without telemetry)
        try:
            _create_variable_log_entry(session_id, key, result_value)
        except Exception as e:
            logging.debug(f"⚠️ Tropir: Could not create variable log: {e}")
    
    # NEW: Track in current LLM call context if one exists
    if hasattr(_current_llm_call_id, 'call_id') and _current_llm_call_id.call_id:
        call_id = _current_llm_call_id.call_id
        if call_id in _llm_call_context:
            _llm_call_context[call_id]['variables_used'][key] = {
                'default_value': value,
                'final_value': result_value,
                'type': type(result_value).__name__,
                'timestamp': time.time()
            }
    
    return result_value

def tropir_prompt(prompt_id: str, default_prompt: str, role: str = None) -> str:
    """
    Smart prompt that returns rerun prompt if available, otherwise default.
    
    Usage:
        system_prompt = tropir_prompt("system_prompt", "You are a helpful assistant", role="system")
        user_prompt = tropir_prompt("user_prompt", "Answer this question: {question}", role="user")
        
    Args:
        prompt_id: Unique identifier for this prompt
        default_prompt: Default prompt text with optional placeholders
        role: Optional role hint (system/user/assistant) for LLM call reconstruction
    """
    _check_rerun_mode()
    
    # Register this prompt in the global registry
    _prompt_registry[prompt_id] = default_prompt
    
    # Get current session for tracking
    session_id = get_session_id()
    
    if session_id and session_id not in _session_execution_data:
        _session_execution_data[session_id] = {"variables": {}, "prompts": {}}
    
    if _rerun_mode and prompt_id in _prompts:
        result_prompt = _prompts[prompt_id]
        logging.info(f"🔄 Tropir: Using rerun prompt for '{prompt_id}'")
    else:
        result_prompt = default_prompt
        
    # Track this prompt usage with enhanced metadata including role
    if session_id:
        # Store prompt with timestamp for better LLM call mapping
        import hashlib
        import time
        
        prompt_hash = hashlib.md5(result_prompt.encode()).hexdigest()[:8]
        timestamp = time.time()
        
        prompt_metadata = {
            "prompt_text": result_prompt,
            "timestamp": timestamp,
            "prompt_hash": prompt_hash,
            "call_sequence": len(_session_execution_data[session_id]["prompts"]) + 1,
            "role": role,  # Track the role for LLM reconstruction
            "prompt_id": prompt_id,
            "session_id": session_id
        }
        
        _session_execution_data[session_id]["prompts"][prompt_id] = prompt_metadata
        
        # NEW: Store prompt metadata globally for parameter passing tracking
        # This allows us to look up prompt info when we see the prompt text later
        _prompt_metadata[result_prompt] = prompt_metadata
        _prompt_value_to_id[result_prompt] = prompt_id
        
        # Also store a truncated version for partial matches
        if len(result_prompt) > 100:
            truncated = result_prompt[:100]
            _prompt_metadata[truncated] = prompt_metadata
            _prompt_value_to_id[truncated] = prompt_id
        
        # Add to span metadata for better tracking
        span = get_current_span()
        if span:
            span.add(f"tropir_prompt_{prompt_id}", {
                "prompt_id": prompt_id,
                "prompt_hash": prompt_hash,
                "prompt_length": len(result_prompt),
                "timestamp": timestamp,
                "call_sequence": len(_session_execution_data[session_id]["prompts"]),
                "role": role  # Include role in metadata
            })
        
        # Create a log entry directly (without telemetry)
        try:
            _create_prompt_log_entry(session_id, prompt_id, result_prompt, role)
        except Exception as e:
            logging.debug(f"⚠️ Tropir: Could not create prompt log: {e}")
    
    # NEW: Track in current LLM call context if one exists
    if hasattr(_current_llm_call_id, 'call_id') and _current_llm_call_id.call_id:
        call_id = _current_llm_call_id.call_id
        if call_id in _llm_call_context:
            _llm_call_context[call_id]['prompts_used'][prompt_id] = {
                'default_prompt': default_prompt,
                'final_prompt': result_prompt,
                'timestamp': time.time(),
                'role': role  # Track role in LLM call context
            }
    
    return result_prompt

def _get_user_id_from_api_key():
    """Extract user_id from the API key in thread local storage"""
    try:
        # Get the API key from thread local storage
        _init_thread_local()
        tropir_api_key = getattr(_thread_local, 'tropir_api_key', None)
        
        if not tropir_api_key:
            tropir_api_key = os.environ.get("TROPIR_API_KEY")
        
        if not tropir_api_key:
            logging.debug("⚠️ Tropir: No API key found for user_id lookup")
            return None
        
        # Import database here to avoid circular imports
        try:
            import sys
            import os
            api_path = os.path.join(os.getcwd(), '../tropir/api')
            if api_path not in sys.path:
                sys.path.append(api_path)
            
            # Load environment variables from the api directory
            from dotenv import load_dotenv
            load_dotenv(os.path.join(api_path, '.env'))
            
            from utils.database import supabase
        except ImportError:
            logging.debug(f"⚠️ Tropir: Could not import supabase database connection")
            return None
        
        # Look up user_id from api_keys table
        response = supabase.table('api_keys').select("user_id").eq("api_key", tropir_api_key).limit(1).execute()
        
        if not response.data:
            logging.debug(f"⚠️ Tropir: Invalid API key for user_id lookup")
            return None
        
        user_id = response.data[0]["user_id"]
        logging.debug(f"✅ Tropir: Found user_id {user_id} for API key")
        return user_id
        
    except Exception as e:
        logging.debug(f"⚠️ Tropir: Error getting user_id from API key - {e}")
        return None

def _get_git_info():
    """Get git repository information from the current working directory"""
    git_info = {}
    
    try:
        # Get current branch
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            git_info['git_branch'] = result.stdout.strip()
        
        # Get current commit hash
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            git_info['git_commit_hash'] = result.stdout.strip()
        
        # Get remote URL
        result = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            git_info['git_repo_url'] = result.stdout.strip()
            git_info['git_remote_name'] = 'origin'
        
        # Check if working directory is dirty (has uncommitted changes)
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            git_info['git_is_dirty'] = len(result.stdout.strip()) > 0
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not a git repository or git not available
        pass
    
    return git_info

def _get_execution_info():
    """Get execution environment information"""
    execution_info = {}
    
    try:
        # Get Python version
        execution_info['python_version'] = platform.python_version()
        
        # Get working directory
        execution_info['working_directory'] = os.getcwd()
        
        # Get script path from sys.argv
        if sys.argv:
            execution_info['script_path'] = sys.argv[0]
            execution_info['command_line'] = sys.argv.copy()
        
    except Exception as e:
        logging.debug(f"⚠️ Tropir: Error getting execution info - {e}")
    
    return execution_info

def _create_variable_log_entry(session_id: str, key: str, value: Any):
    """Create or update a tropir instrumentation record for a variable"""
    
    try:
        # Import database here to avoid circular imports
        from datetime import datetime
        
        # Try to import the database from API
        try:
            import sys
            import os
            api_path = os.path.join(os.getcwd(), '../tropir/api')
            if api_path not in sys.path:
                sys.path.append(api_path)
            
            # Load environment variables from the api directory
            from dotenv import load_dotenv
            load_dotenv(os.path.join(api_path, '.env'))
            
            from utils.database import supabase
        except ImportError:
            logging.debug(f"⚠️ Tropir: Could not import supabase database connection")
            return
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        session_name = get_session_name()
        user_id = _get_user_id_from_api_key()
        
        # Create variable entry in the expected format
        variable_entry = {
            "value": value,
            "type": type(value).__name__,
            "display_name": key.replace("_", " ").title(),
            "required": True,
            "description": f"Tropir variable of type {type(value).__name__}"
        }
        
        # Try to get existing record first
        existing_result = supabase.table('tropir_instrumentations').select('*').eq('session_id', session_id).execute()
        
        if existing_result.data:
            # Update existing record
            existing_record = existing_result.data[0]
            existing_variables = existing_record.get('instrumented_variables', {})
            existing_variables[key] = variable_entry
            
            supabase.table('tropir_instrumentations').update({
                'instrumented_variables': existing_variables,
                'updated_at': timestamp
            }).eq('session_id', session_id).execute()
        else:
            # Get git and execution info for new record
            git_info = _get_git_info()
            execution_info = _get_execution_info()
            
            # Create new record with git and execution info
            new_record = {
                'session_id': session_id,
                'pipeline_name': session_name,  # Use session name as pipeline name
                'user_id': user_id,  # Add user_id from API key lookup
                'instrumented_variables': {key: variable_entry},
                'instrumented_prompts': {},
                'created_at': timestamp,
                'updated_at': timestamp,
                **git_info,  # Add git information
                **execution_info  # Add execution information
            }
            
            supabase.table('tropir_instrumentations').insert(new_record).execute()
            
            logging.debug(f"✅ Tropir: Created instrumentation record with git info - repo: {git_info.get('git_repo_url', 'unknown')}, branch: {git_info.get('git_branch', 'unknown')}")
        
        logging.debug(f"✅ Tropir: Updated instrumentation record for variable {key} in session {session_id}")
        
    except Exception as e:
        logging.debug(f"⚠️ Tropir: Variable instrumentation error - {e}")
        pass

def _create_prompt_log_entry(session_id: str, prompt_id: str, prompt_text: str, role: str = None):
    """Create or update a tropir instrumentation record for a prompt"""
    
    try:
        # Import database here to avoid circular imports
        from datetime import datetime
        
        # Try to import the database from API
        try:
            import sys
            import os
            api_path = os.path.join(os.getcwd(), '../tropir/api')
            if api_path not in sys.path:
                sys.path.append(api_path)
            
            # Load environment variables from the api directory
            from dotenv import load_dotenv
            load_dotenv(os.path.join(api_path, '.env'))
            
            from utils.database import supabase
        except ImportError:
            logging.debug(f"⚠️ Tropir: Could not import supabase database connection")
            return
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        session_name = get_session_name()
        user_id = _get_user_id_from_api_key()
        
        # Create prompt entry in the expected format with role
        prompt_entry = {
            "default_prompt": prompt_text,
            "display_name": prompt_id.replace("_", " ").title(),
            "description": "Tropir prompt",
            "category": "user_defined",
            "role": role  # Include role information
        }
        
        # Try to get existing record first
        existing_result = supabase.table('tropir_instrumentations').select('*').eq('session_id', session_id).execute()
        
        if existing_result.data:
            # Update existing record
            existing_record = existing_result.data[0]
            existing_prompts = existing_record.get('instrumented_prompts', {})
            existing_prompts[prompt_id] = prompt_entry
            
            supabase.table('tropir_instrumentations').update({
                'instrumented_prompts': existing_prompts,
                'updated_at': timestamp
            }).eq('session_id', session_id).execute()
        else:
            # Get git and execution info for new record
            git_info = _get_git_info()
            execution_info = _get_execution_info()
            
            # Create new record with git and execution info
            new_record = {
                'session_id': session_id,
                'pipeline_name': session_name,  # Use session name as pipeline name
                'user_id': user_id,  # Add user_id from API key lookup
                'instrumented_variables': {},
                'instrumented_prompts': {prompt_id: prompt_entry},
                'created_at': timestamp,
                'updated_at': timestamp,
                **git_info,  # Add git information
                **execution_info  # Add execution information
            }
            
            supabase.table('tropir_instrumentations').insert(new_record).execute()
            
            logging.debug(f"✅ Tropir: Created instrumentation record with git info - repo: {git_info.get('git_repo_url', 'unknown')}, branch: {git_info.get('git_branch', 'unknown')}")
        
        logging.debug(f"✅ Tropir: Updated instrumentation record for prompt {prompt_id} in session {session_id}")
        
    except Exception as e:
        logging.debug(f"⚠️ Tropir: Prompt instrumentation error - {e}")
        pass

# Removed automatic frame variable capture - now using explicit tropir_variable() annotations

def _serialize_value(value):
    """Serialize a value to a JSON-compatible format"""
    try:
        # Convert to a serializable format
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, (list, tuple)):
            # Only keep simple lists/tuples
            if len(value) < 100:  # Limit size
                serializable_list = []
                for item in value:
                    if isinstance(item, (str, int, float, bool, type(None))):
                        serializable_list.append(item)
                    else:
                        serializable_list.append(str(item)[:100])  # Truncate complex items
                return serializable_list
        elif isinstance(value, dict):
            # Only keep simple dicts
            if len(value) < 50:  # Limit size
                serializable_dict = {}
                for k, v in value.items():
                    if isinstance(k, str) and isinstance(v, (str, int, float, bool, type(None))):
                        serializable_dict[k] = v
                    elif isinstance(k, str):
                        serializable_dict[k] = str(v)[:100]  # Truncate complex values
                return serializable_dict
        else:
            # For complex objects, store a string representation
            return str(value)[:200]  # Truncate long strings
    except Exception:
        # If serialization fails, store as string
        return str(value)[:200]
    
    return None

def _capture_execution_context(session_id: str):
    """Capture execution context for rerun capabilities"""
    if not session_id or _rerun_mode:
        return
    
    try:
        # Initialize context for session
        if session_id not in _execution_context:
            _execution_context[session_id] = {}
        
        context = {}
        
        # 1. Git Information
        try:
            context["git"] = {
                "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=".", stderr=subprocess.DEVNULL).decode().strip(),
                "commit_hash": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=".", stderr=subprocess.DEVNULL).decode().strip(),
                "is_dirty": len(subprocess.check_output(["git", "status", "--porcelain"], cwd=".", stderr=subprocess.DEVNULL).decode().strip()) > 0,
                "remote_url": subprocess.check_output(["git", "config", "--get", "remote.origin.url"], cwd=".", stderr=subprocess.DEVNULL).decode().strip()
            }
        except (subprocess.CalledProcessError, FileNotFoundError):
            context["git"] = {"error": "Not a git repository or git not available"}
        
        # 2. System Information
        context["system"] = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "working_directory": os.getcwd(),
            "command_line": sys.argv.copy(),
            "script_name": sys.argv[0] if sys.argv else "unknown"
        }
        
        # 3. Environment Variables (filter sensitive ones)
        important_env_vars = [
            "ENVIRONMENT", "NODE_ENV", "PYTHONPATH", "PATH",
            "TROPIR_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
            "TROPIR_RERUN_MODE", "TROPIR_METADATA_ENDPOINT"
        ]
        context["environment"] = {
            key: os.environ.get(key, "") for key in important_env_vars if key in os.environ
        }
        
        # 4. Package Dependencies (sample key packages)
        try:
            important_packages = ["openai", "anthropic", "requests", "httpx", "numpy", "pandas", "torch", "transformers"]
            context["dependencies"] = {}
            for pkg_name in important_packages:
                try:
                    pkg = pkg_resources.get_distribution(pkg_name)
                    context["dependencies"][pkg_name] = pkg.version
                except pkg_resources.DistributionNotFound:
                    pass
        except Exception:
            context["dependencies"] = {"error": "Could not determine package versions"}
        
        # 5. Execution Metadata
        context["execution"] = {
            "start_time": time.time(),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "session_id": session_id,
            "random_state": None  # Can be set by user if needed
        }
        
        # Store the context
        _execution_context[session_id] = context
        
        logging.debug(f"📊 Tropir: Captured execution context for session {session_id}")
        
    except Exception as e:
        logging.warning(f"⚠️ Tropir: Execution context capture error - {e}")
        pass

def _inject_variables_into_frame(frame, session_id: str):
    """Inject rerun variables into the current frame"""
    if not _rerun_mode or not _state_variables:
        return
        
    try:
        # Inject state variables into the frame's local namespace
        for name, value in _state_variables.items():
            if name not in frame.f_locals:  # Only inject if not already present
                frame.f_locals[name] = value
                
        logging.debug(f"🔄 Tropir: Injected {len(_state_variables)} variables into frame")
        
    except Exception as e:
        logging.debug(f"⚠️ Tropir: Variable injection error - {e}")
        pass

# === RERUN AND EXPORT UTILITIES ===

def export_session_data(session_id: str = None, session_name: str = None) -> Dict[str, Any]:
    """
    Export session data for rerun capabilities.
    
    Args:
        session_id: Optional session ID to export
        session_name: Optional session name to export
        
    Returns:
        Dictionary containing all session data needed for rerun
    """
    if not session_id:
        session_id = get_session_id()
    
    if not session_id:
        logging.warning("No session ID provided or found for export")
        return {}
    
    # Get session data
    session_data = _session_execution_data.get(session_id, {"variables": {}, "prompts": {}})
    
    # Export data
    export_data = {
        "session_id": session_id,
        "session_name": session_name or get_session_name(),
        "variables": session_data["variables"],
        "prompts": session_data["prompts"],
        "prompt_registry": _prompt_registry.copy(),
        "execution_context": _execution_context.get(session_id, {}),
        "timestamp": time.time(),
        "rerun_mode": False
    }
    
    logging.info(f"📤 Tropir: Exported session data - {len(session_data['variables'])} variables, {len(session_data['prompts'])} prompts")
    
    return export_data

def create_rerun_script(
    session_id: str = None, 
    session_name: str = None, 
    output_file: str = None,
    modified_variables: Dict[str, Any] = None,
    modified_prompts: Dict[str, str] = None,
    startup_command: str = None,
    local_mode: bool = True
) -> str:
    """
    Create a rerun script for the current session with optional modifications.
    
    Args:
        session_id: Optional session ID to create script for
        session_name: Optional session name
        output_file: Optional output file path
        modified_variables: Optional dictionary of variables to override
        modified_prompts: Optional dictionary of prompts to override
        startup_command: Optional custom startup command
        local_mode: Whether to create a local execution script (default: True)
        
    Returns:
        Generated rerun script content
    """
    session_data = export_session_data(session_id, session_name)
    
    if not session_data:
        return ""
    
    # Start with original session data
    variables = session_data["variables"].copy()
    prompts = session_data["prompts"].copy()
    
    # Apply modifications if provided
    if modified_variables:
        variables.update(modified_variables)
        
    if modified_prompts:
        prompts.update(modified_prompts)
    
    # Create environment variables for rerun (compact JSON for shell compatibility)
    variables_json = json.dumps(variables)
    prompts_json = json.dumps(prompts)
    
    # Escape single quotes for shell safety
    variables_json_escaped = variables_json.replace("'", "'\"'\"'")
    prompts_json_escaped = prompts_json.replace("'", "'\"'\"'")
    
    # Get execution context for comments
    context = session_data.get("execution_context", {})
    git_info = context.get("git", {})
    system_info = context.get("system", {})
    
    # Determine startup command
    if not startup_command:
        startup_command = system_info.get('script_name', 'python main.py')
        if startup_command and not startup_command.startswith('python'):
            startup_command = f"python {startup_command}"
    
    # Generate new session ID for rerun result
    new_session_id = str(uuid.uuid4())
    
    # Create script based on mode
    if local_mode:
        script_content = f"""#!/bin/bash
# Tropir Local Rerun Script
# Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}
# Session: {session_data['session_name']} ({session_data['session_id']})
# Rerun Session ID: {new_session_id}
#
# Original Execution Context:
# Git Branch: {git_info.get('branch', 'unknown')}
# Git Commit: {git_info.get('commit_hash', 'unknown')[:8] if git_info.get('commit_hash') else 'unknown'}...
# Python Version: {system_info.get('python_version', 'unknown')}
# Platform: {system_info.get('platform', 'unknown')}
# Script: {system_info.get('script_name', 'unknown')}
# Working Directory: {system_info.get('working_directory', os.getcwd())}

echo "🔄 Starting Tropir Local Rerun..."
echo "📊 Original Session: {session_data['session_id']}"
echo "🆔 Rerun Session: {new_session_id}"
echo "🎯 Startup Command: {startup_command}"
echo "📂 Working Directory: {os.getcwd()}"

# Set rerun mode environment variables
export TROPIR_RERUN_MODE="true"
export TROPIR_RERUN_SESSION_ID="{new_session_id}"
export TROPIR_ORIGINAL_SESSION_ID="{session_data['session_id']}"

# Set captured variables ({len(variables)} total)
export TROPIR_STATE_VARIABLES='{variables_json_escaped}'

# Set captured prompts ({len(prompts)} total)
export TROPIR_PROMPTS='{prompts_json_escaped}'

# Set development mode for local execution
export TROPIR_DEV="true"

# Show summary
echo "📊 Variables: {len(variables)}"
echo "📝 Prompts: {len(prompts)}"
echo "🌿 Original branch: {git_info.get('branch', 'unknown')}"

# Execute the startup command
echo "🚀 Executing: {startup_command}"
{startup_command}

echo "✅ Local rerun completed"
"""
    else:
        # Traditional rerun script (for compatibility)
        script_content = f"""#!/bin/bash
# Tropir Rerun Script
# Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}
# Session: {session_data['session_name']} ({session_data['session_id']})
#
# Original Execution Context:
# Git Branch: {git_info.get('branch', 'unknown')}
# Git Commit: {git_info.get('commit_hash', 'unknown')[:8] if git_info.get('commit_hash') else 'unknown'}...
# Python Version: {system_info.get('python_version', 'unknown')}
# Platform: {system_info.get('platform', 'unknown')}
# Script: {system_info.get('script_name', 'unknown')}
# Working Directory: {system_info.get('working_directory', 'unknown')}

# Set rerun mode environment variables
export TROPIR_RERUN_MODE="true"
export TROPIR_RERUN_SESSION_ID="{session_data['session_id']}"

# Set captured variables
export TROPIR_STATE_VARIABLES='{variables_json_escaped}'

# Set captured prompts
export TROPIR_PROMPTS='{prompts_json_escaped}'

# Run the original script
echo "🔄 Running in Tropir rerun mode..."
echo "📊 Variables: {len(variables)}"
echo "📝 Prompts: {len(prompts)}"
echo "🎯 Original script: {system_info.get('script_name', 'unknown')}"
echo "🌿 Original branch: {git_info.get('branch', 'unknown')}"

# Execute the original script (replace with your script path)
python "$@"
"""
    
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(script_content)
            # Make script executable
            os.chmod(output_file, 0o755)
            logging.info(f"💾 Tropir: {'Local ' if local_mode else ''}Rerun script saved to {output_file}")
        except Exception as e:
            logging.error(f"❌ Tropir: Failed to save rerun script: {e}")
    
    return script_content

def create_local_rerun_script_with_modifications(
    session_id: str,
    modified_variables: Dict[str, Any] = None,
    modified_prompts: Dict[str, str] = None,
    startup_command: str = "python main.py",
    output_file: str = None
) -> str:
    """
    Convenience function to create a local rerun script with modifications.
    
    Args:
        session_id: Session ID to rerun
        modified_variables: Variables to override
        modified_prompts: Prompts to override  
        startup_command: Command to execute
        output_file: Optional file to save script to
        
    Returns:
        Generated script content
    """
    return create_rerun_script(
        session_id=session_id,
        modified_variables=modified_variables,
        modified_prompts=modified_prompts,
        startup_command=startup_command,
        output_file=output_file,
        local_mode=True
    )

def get_session_summary(session_id: str = None) -> Dict[str, Any]:
    """
    Get a summary of the current session.
    
    Args:
        session_id: Optional session ID
        
    Returns:
        Dictionary with session summary information
    """
    if not session_id:
        session_id = get_session_id()
    
    if not session_id:
        return {"error": "No active session"}
    
    session_data = _session_execution_data.get(session_id, {"variables": {}, "prompts": {}})
    
    context = _execution_context.get(session_id, {})
    
    summary = {
        "session_id": session_id,
        "session_name": get_session_name(),
        "variable_count": len(session_data["variables"]),
        "prompt_count": len(session_data["prompts"]),
        "variables": list(session_data["variables"].keys()),
        "prompts": list(session_data["prompts"].keys()),
        "rerun_mode": _rerun_mode,
        "execution_context": context,
        "timestamp": time.time()
    }
    
    return summary

def print_session_summary(session_id: str = None):
    """Print a formatted summary of the current session."""
    summary = get_session_summary(session_id)
    
    if "error" in summary:
        print(f"❌ {summary['error']}")
        return
    
    print(f"\n🎯 Tropir Session Summary")
    print(f"{'='*50}")
    print(f"Session ID: {summary['session_id']}")
    print(f"Session Name: {summary['session_name']}")
    print(f"Mode: {'🔄 Rerun' if summary['rerun_mode'] else '🆕 Normal'}")
    
    # Show execution context if available
    context = summary.get('execution_context', {})
    if context:
        git_info = context.get('git', {})
        system_info = context.get('system', {})
        
        print(f"\n🔧 Execution Context:")
        if git_info and 'error' not in git_info:
            print(f"  🌿 Git: {git_info.get('branch', 'unknown')} ({git_info.get('commit_hash', 'unknown')[:8]}...)")
            if git_info.get('is_dirty'):
                print(f"      ⚠️ Working directory has uncommitted changes")
        print(f"  🐍 Python: {system_info.get('python_version', 'unknown')}")
        print(f"  💻 Platform: {system_info.get('platform', 'unknown')}")
        print(f"  📁 Working Dir: {system_info.get('working_directory', 'unknown')}")
        print(f"  🎯 Script: {system_info.get('script_name', 'unknown')}")
    
    print(f"\n📊 Variables Captured: {summary['variable_count']}")
    if summary['variables']:
        for var in summary['variables'][:10]:  # Show first 10
            print(f"  • {var}")
        if len(summary['variables']) > 10:
            print(f"  ... and {len(summary['variables']) - 10} more")
    
    print(f"\n📝 Prompts Used: {summary['prompt_count']}")
    if summary['prompts']:
        for prompt in summary['prompts'][:10]:  # Show first 10
            print(f"  • {prompt}")
        if len(summary['prompts']) > 10:
            print(f"  ... and {len(summary['prompts']) - 10} more")
    
    print(f"\n🕐 Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(summary['timestamp']))}")
    print(f"{'='*50}\n")

def print_prompt_mapping_status(session_id: str = None):
    """Print current prompt mapping and tracking status."""
    if not session_id:
        session_id = get_session_id()
    
    if not session_id:
        print("❌ No active session found")
        return
    
    print(f"\n🔗 Tropir Prompt Mapping Status")
    print(f"{'='*50}")
    print(f"Session ID: {session_id}")
    
    # Show current span metadata
    span = get_current_span()
    if span and span.metadata:
        prompt_entries = {k: v for k, v in span.metadata.items() if k.startswith('tropir_prompt_')}
        
        if prompt_entries:
            print(f"📝 Active Prompt Tracking: {len(prompt_entries)} prompts")
            for key, data in prompt_entries.items():
                prompt_id = key.replace('tropir_prompt_', '')
                if isinstance(data, dict):
                    print(f"  • {prompt_id} (hash: {data.get('prompt_hash', 'unknown')}, seq: {data.get('call_sequence', '?')})")
                else:
                    print(f"  • {prompt_id}")
        else:
            print("📝 No active prompt tracking in current span")
    else:
        print("📝 No active span or metadata")
    
    # Show session execution data
    if session_id in _session_execution_data:
        session_data = _session_execution_data[session_id]
        prompts = session_data.get("prompts", {})
        
        print(f"💾 Session Storage: {len(prompts)} prompts recorded")
        for prompt_id, prompt_data in prompts.items():
            if isinstance(prompt_data, dict):
                print(f"  • {prompt_id} (hash: {prompt_data.get('prompt_hash', 'unknown')})")
            else:
                print(f"  • {prompt_id}")
    else:
        print("💾 No session execution data found")
    
    print(f"\n💡 To track prompts: use tropir_prompt('id', 'your prompt text')")
    print(f"💡 To view mapping: Check PipelineOptimize → 'View Prompt ↔ LLM Calls'")
    print(f"{'='*50}\n")

# === END RERUN AND EXPORT UTILITIES ===

# Monitor task cancellation
def _setup_task_cleanup():
    """Setup task cleanup for session management"""
    try:
        loop = asyncio.get_running_loop()
        
        # Only add the callback once per loop
        if loop not in _loop_sessions:
            _loop_sessions[loop] = {}
            
            # Add callback to clean up task sessions when they complete
            def task_cleanup(task):
                task_id = id(task)
                with _session_lock:
                    if task_id in _async_task_sessions:
                        del _async_task_sessions[task_id]
                    if task_id in _async_task_parents:
                        del _async_task_parents[task_id]
            
            # Add a callback to all tasks when they're done
            asyncio.all_tasks(loop=loop)
            loop.set_task_factory(_session_aware_task_factory)
    except RuntimeError:
        # Not in an async context
        pass

# Custom task factory that tracks parent-child task relationships
_original_task_factory = None
def _session_aware_task_factory(loop, coro):
    """Task factory that maintains session context across task parent-child relationships"""
    if _original_task_factory is None:
        task = asyncio.Task(coro, loop=loop)
    else:
        task = _original_task_factory(loop, coro)
    
    # Get current task and link the new task to it
    try:
        current_task = asyncio.current_task(loop=loop)
        if current_task:
            # Track parent-child relationship
            _async_task_parents[id(task)] = id(current_task)
            
            # If parent has a session, inherit it
            if id(current_task) in _async_task_sessions:
                _async_task_sessions[id(task)] = _async_task_sessions[id(current_task)].copy()
    except Exception:
        pass
    
    # Add done callback to clean up
    task.add_done_callback(lambda t: _cleanup_task_session(id(t)))
    
    return task

def _cleanup_task_session(task_id):
    """Remove task from tracking dictionaries when it completes"""
    with _session_lock:
        if task_id in _async_task_sessions:
            del _async_task_sessions[task_id]
        if task_id in _async_task_parents:
            del _async_task_parents[task_id]

# Store original requests.Session.send method
_original_requests_session_send = requests.Session.send
_original_httpx_async_client_send = httpx.AsyncClient.send # Added for httpx

# Default metadata endpoint
def get_default_metadata_endpoint():
    if os.environ.get("ENVIRONMENT") == "dev":
        return "http://localhost:8080/api/v1/metadata"
    else:
        return "https://api.tropir.com/api/v1/metadata"

# Initialize thread-local storage
def _init_thread_local():
    if not hasattr(_thread_local, 'session_stack'):
        _thread_local.session_stack = []
    if not hasattr(_thread_local, 'named_sessions'):
        _thread_local.named_sessions = {}
    if not hasattr(_thread_local, 'session_id'):
        _thread_local.session_id = None
    if not hasattr(_thread_local, 'current_session_name'):
        _thread_local.current_session_name = None
    if not hasattr(_thread_local, 'patch_count'): # For requests
        _thread_local.patch_count = 0
    if not hasattr(_thread_local, 'httpx_patch_count'): # Added for httpx
        _thread_local.httpx_patch_count = 0
    if not hasattr(_thread_local, 'manually_managed_sessions'):
        _thread_local.manually_managed_sessions = {}
    if not hasattr(_thread_local, 'tropir_api_key'):
        _thread_local.tropir_api_key = os.environ.get("TROPIR_API_KEY") or "070ca1b5-3a68-4cb4-bf65-d0ae71e60c2c"

class SessionManager:
    """
    Manager class for Tropir sessions that provides methods for adding metadata steps.
    Can be used as a context manager or directly accessed to add steps to an existing session.
    """
    def __init__(self, session_name=None):
        self.session_name = session_name
        self.session_id = None
        self.is_context_manager = False
        self.previous_stack = None
        self.previous_session_name = None
        
        # When using session() inside an async function decorated with @begin_session,
        # we need to ensure it gets the correct session ID for the current execution context
        
        # First check if we're in an async context
        try:
            current_task = asyncio.current_task()
            if current_task and id(current_task) in _async_task_sessions:
                task_session = _async_task_sessions[id(current_task)]
                # If this session name matches our current async task session, use that
                if session_name == task_session['session_name']:
                    self.session_id = task_session['session_id']
                    return
        except RuntimeError:
            # Not in an async context
            pass
        
        # If not in a matching async context, check the thread-local session stack
        _init_thread_local()
        current_stack_session_id = get_session_id()
        
        # If we have both a current session ID from the stack AND a session name that matches
        # what we're looking for, use that ID instead of a stored one
        if current_stack_session_id and session_name == _thread_local.current_session_name:
            self.session_id = current_stack_session_id
            return
            
        # If this is an existing session manager, retrieve it
        if session_name and session_name in _global_session_managers:
            existing_manager = _global_session_managers[session_name]
            self.session_id = existing_manager.session_id
            return
            
        # If session_name is provided, try to find an existing session ID
        if session_name:
            # Check thread-local named sessions first
            if session_name in _thread_local.named_sessions:
                self.session_id = _thread_local.named_sessions[session_name]
            # Then check global sessions by name
            elif session_name in _global_sessions_by_name:
                self.session_id = _global_sessions_by_name[session_name]
                # Copy to thread-local too
                _thread_local.named_sessions[session_name] = self.session_id
            
        # Store the manager in the global dict
        if session_name:
            _global_session_managers[session_name] = self
    
    def __enter__(self):
        """Start the session when used as a context manager."""
        _init_thread_local()
        self.is_context_manager = True
        self.previous_stack = list(_thread_local.session_stack)  # Create a copy of the stack
        self.previous_session_name = _thread_local.current_session_name
        
        # If we don't have a session ID yet, generate one
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
            if self.session_name:
                _thread_local.named_sessions[self.session_name] = self.session_id
                _global_sessions_by_name[self.session_name] = self.session_id
        
        # Push session ID to the stack and set current session name
        _thread_local.session_stack.append(self.session_id)
        _thread_local.current_session_name = self.session_name
        
        # Register in parent thread sessions for inheritance by child threads
        current_thread = threading.current_thread().name
        _parent_thread_sessions[current_thread] = (self.session_id, self.session_name)
        
        _apply_requests_patch_if_needed() # Apply requests patch
        _apply_httpx_patch_if_needed() # Apply httpx patch
        logging.debug(f"Started session: {self.session_name or 'unnamed'} with ID: {self.session_id} on thread {current_thread}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the session when the context manager exits."""
        if not self.is_context_manager:
            return
            
        # Restore previous stack state and session name
        _thread_local.session_stack = self.previous_stack
        _thread_local.current_session_name = self.previous_session_name
        
        current_thread = threading.current_thread().name
        
        # Update parent thread sessions register with previous state
        if self.previous_session_name:
            prev_id = _thread_local.named_sessions.get(self.previous_session_name)
            if prev_id:
                _parent_thread_sessions[current_thread] = (prev_id, self.previous_session_name)
        elif not self.previous_stack and not self.previous_session_name:
            # If we're ending all sessions, remove from parent thread register
            if current_thread in _parent_thread_sessions:
                del _parent_thread_sessions[current_thread]
        
        _revert_requests_patch_if_needed() # Revert requests patch
        _revert_httpx_patch_if_needed() # Revert httpx patch
        logging.debug(f"Ended session: {self.session_name or 'unnamed'} on thread {current_thread}")
    
    def add_step(self, data, step_name=None):
        """
        DEPRECATED: Use get_current_span().add(key, value) instead.
        
        Add metadata as a step to the current session using the new span-based approach.
        This method is maintained for backward compatibility but now uses spans internally.
        
        Args:
            data: Any JSON-serializable data to be added as metadata
            step_name: Optional name for this step (used as the key)
        
        Returns:
            Always returns True for compatibility, actual metadata is stored in span
        """
        logging.warning("add_step() is deprecated. Use get_current_span().add(key, value) instead.")
        
        # Get or create span for current session
        span = get_current_span()
        if not span:
            # Ensure we have a session
            if not self.session_id:
                # Try to find an existing session by name
                if self.session_name:
                    if self.session_name in _thread_local.named_sessions:
                        self.session_id = _thread_local.named_sessions[self.session_name]
                    else:
                        self.session_id = str(uuid.uuid4())
                        _thread_local.named_sessions[self.session_name] = self.session_id
                        _global_sessions_by_name[self.session_name] = self.session_id
                
                if not self.session_id:
                    current_session_id = get_session_id()
                    if current_session_id:
                        self.session_id = current_session_id
                    else:
                        logging.warning(f"Cannot add step: No active session found for {self.session_name or 'unnamed'}")
                        return False
            
            # Create span for this session
            span = Span(self.session_id, self.session_name)
            _session_spans[self.session_id] = span
        
        # Use step_name as key, or generate a generic one
        key = step_name if step_name else f"step_{int(time.time())}"
        
        # Add the data to the span
        span.add(key, data)
        
        logging.debug(f"Added metadata step '{key}' to session {self.session_name or 'unnamed'} via deprecated add_step()")
        return True

def _add_tropir_headers(headers_obj, url_str):
    """Helper function to add all Tropir headers to a headers object."""
    # Try to detect if we're in an async task context first
    try:
        current_task = asyncio.current_task()
        if current_task and id(current_task) in _async_task_sessions:
            task_session = _async_task_sessions[id(current_task)]
            session_id = task_session['session_id']
            session_name = task_session['session_name']
            
            headers_obj["X-Session-ID"] = str(session_id)
            headers_obj["X-Session-Name"] = str(session_name)
            logging.debug(f"Tropir Session (async): Added headers - ID: {session_id}, Name: {session_name}")
            
            tropir_api_key = getattr(_thread_local, 'tropir_api_key', None)
            # If not in thread local, try environment variable
            if not tropir_api_key:
                tropir_api_key = os.environ.get("TROPIR_API_KEY")
            # If still not found, use hardcoded key as fallback
            if not tropir_api_key:
                tropir_api_key = "fcbb43b6-5b9b-4c32-a6d7-5a4a1ea63e82"
            if tropir_api_key:
                headers_obj["X-TROPIR-API-KEY"] = tropir_api_key
            
            # Determine if it's a target host for logging
            parsed_url = urlparse(url_str)
            hostname = parsed_url.hostname
            port = parsed_url.port
            is_target_host = (hostname == "api.tropir.com") or \
                (hostname == "localhost" and port == 8080) or \
                (hostname == "host.docker.internal" and port == 8080)
                
            return is_target_host
    except RuntimeError:
        # Not in an async context, continue with normal flow
        pass
    
    # Normal flow for non-async contexts
    session_id = get_session_id()
    if session_id:
        headers_obj["X-Session-ID"] = str(session_id)
        logging.debug(f"Tropir Session: Added X-Session-ID to headers: {session_id}")
    else:
        logging.debug("Tropir Session: No active session ID found, X-Session-ID header not added.")

    session_name = get_session_name()
    if session_name:
        headers_obj["X-Session-Name"] = str(session_name)
        logging.debug(f"Tropir Session: Added X-Session-Name to headers: {session_name}")
    else:
        logging.debug("Tropir Session: No active session name found, X-Session-Name header not added.")

    tropir_api_key = getattr(_thread_local, 'tropir_api_key', None)
    
    # If not in thread local, try environment variable
    if not tropir_api_key:
        tropir_api_key = os.environ.get("TROPIR_API_KEY")
    
    # If still not found, use hardcoded key as fallback
    if not tropir_api_key:
        tropir_api_key = "fcbb43b6-5b9b-4c32-a6d7-5a4a1ea63e82"
    
    # Determine if it's a target host for logging purposes (original logic retained for other potential uses)
    parsed_url = urlparse(url_str)
    hostname = parsed_url.hostname
    port = parsed_url.port

    is_target_host_for_logging = (hostname == "api.tropir.com") or \
       (hostname == "localhost" and port == 8080) or \
       (hostname == "host.docker.internal" and port == 8080)

    if tropir_api_key:
        headers_obj["X-TROPIR-API-KEY"] = tropir_api_key
        logging.debug("Tropir Session: Added X-TROPIR-API-KEY to headers for URL: %s", url_str)
    else:
        logging.debug("Tropir Session: TROPIR_API_KEY not found in thread local or environment, skipping API key header for URL: %s", url_str)
    
    return is_target_host_for_logging # Return original target_host status, mainly for _log_request_details

def _log_request_details(url_str, headers_obj, body_content, content_type_str):
    """Helper function to log request details including headers and body."""
    # Function intentionally left blank after removing all print and logging.debug statements as per instructions.
    pass


async def _patched_httpx_async_client_send(client_instance, request, **kwargs):
    """
    Patched version of httpx.AsyncClient.send that adds Tropir session headers.
    """
    _add_tropir_headers(request.headers, str(request.url))
    
    content_type = request.headers.get("Content-Type", "").lower()
    # Check if it's a target host for detailed logging
    parsed_url = urlparse(str(request.url))
    hostname = parsed_url.hostname
    port = parsed_url.port
    is_target_host = (hostname == "api.tropir.com") or \
                     (hostname == "localhost" and port == 8080) or \
                     (hostname == "host.docker.internal" and port == 8080)

    if is_target_host:
        _log_request_details(str(request.url), request.headers, request.content, content_type)

    return await _original_httpx_async_client_send(client_instance, request, **kwargs)


def _patched_requests_session_send(session_instance, request, **kwargs):
    """
    Patched version of requests.Session.send that adds Tropir session headers.
    """
    is_target_host = _add_tropir_headers(request.headers, request.url)
    
    if is_target_host:
        content_type = request.headers.get("Content-Type", "").lower()
        _log_request_details(request.url, request.headers, request.body, content_type)

    return _original_requests_session_send(session_instance, request, **kwargs)

def _apply_requests_patch_if_needed():
    _init_thread_local() 
    if _thread_local.patch_count == 0:
        requests.Session.send = _patched_requests_session_send
        logging.debug("Tropir Session: Patched requests.Session.send.")
    _thread_local.patch_count += 1

def _revert_requests_patch_if_needed():
    _init_thread_local() 
    if hasattr(_thread_local, 'patch_count') and _thread_local.patch_count > 0:
        _thread_local.patch_count -= 1
        if _thread_local.patch_count == 0:
            requests.Session.send = _original_requests_session_send
            logging.debug("Tropir Session: Reverted requests.Session.send to original.")
    elif hasattr(_thread_local, 'patch_count') and _thread_local.patch_count == 0 :
        if requests.Session.send != _original_requests_session_send:
             requests.Session.send = _original_requests_session_send
             logging.warning("Tropir Session: patch_count (requests) was 0 but send was not original. Reverted.")

def _apply_httpx_patch_if_needed():
    _init_thread_local()
    if _thread_local.httpx_patch_count == 0:
        httpx.AsyncClient.send = _patched_httpx_async_client_send
        logging.debug("Tropir Session: Patched httpx.AsyncClient.send.")
    _thread_local.httpx_patch_count += 1

def _revert_httpx_patch_if_needed():
    _init_thread_local()
    if hasattr(_thread_local, 'httpx_patch_count') and _thread_local.httpx_patch_count > 0:
        _thread_local.httpx_patch_count -= 1
        if _thread_local.httpx_patch_count == 0:
            httpx.AsyncClient.send = _original_httpx_async_client_send
            logging.debug("Tropir Session: Reverted httpx.AsyncClient.send to original.")
    elif hasattr(_thread_local, 'httpx_patch_count') and _thread_local.httpx_patch_count == 0:
        if httpx.AsyncClient.send != _original_httpx_async_client_send:
            httpx.AsyncClient.send = _original_httpx_async_client_send
            logging.warning("Tropir Session: httpx_patch_count was 0 but send was not original. Reverted.")

def _inherit_parent_session():
    """Inherit session from parent thread if available."""
    current_thread = threading.current_thread()
    
    # Skip for MainThread since it has no parent
    if current_thread.name == 'MainThread':
        return
    
    # Check if there's a parent session we can inherit
    if 'MainThread' in _parent_thread_sessions:
        parent_session = _parent_thread_sessions['MainThread']
        if parent_session:
            session_id, session_name = parent_session
            set_session_id(session_id, session_name)
            logging.debug(f"Thread {current_thread.name} inherited session {session_name} ({session_id}) from MainThread")

def get_session_id():
    """Get the current session ID.
    
    Checks in this order:
    1. Rerun session ID (if in rerun mode)
    2. Current async task context
    3. Parent async task context (if current task has no session)
    4. Thread-local storage
    5. Parent thread inheritance
    6. Event loop specific storage
    
    Returns:
        str or None: The current session ID if one exists, otherwise None.
    """
    # Check rerun mode first
    _check_rerun_mode()
    if _rerun_mode and _rerun_session_id:
        return _rerun_session_id
    
    # Ensure task monitoring is setup if we're in an async context
    try:
        _setup_task_cleanup()
    except Exception:
        pass
    
    # Check if we're in an async context
    try:
        current_task = asyncio.current_task()
        if current_task:
            task_id = id(current_task)
            
            # Direct task session
            with _session_lock:
                if task_id in _async_task_sessions:
                    return _async_task_sessions[task_id]['session_id']
                
                # Check parent task's session (for nested tasks)
                if task_id in _async_task_parents:
                    parent_id = _async_task_parents[task_id]
                    if parent_id in _async_task_sessions:
                        # Create a copy for this task too for future lookups
                        _async_task_sessions[task_id] = _async_task_sessions[parent_id].copy()
                        return _async_task_sessions[task_id]['session_id']
                
                # Check event loop-specific sessions
                loop = asyncio.get_running_loop()
                if loop in _loop_sessions and 'current_session_id' in _loop_sessions[loop]:
                    return _loop_sessions[loop]['current_session_id']
    except RuntimeError:
        # Not in an async context
        pass
    
    _init_thread_local()
    
    # Check thread-local stack first
    if _thread_local.session_stack:
        return _thread_local.session_stack[-1]
    
    # Then check thread-local session ID
    if _thread_local.session_id:
        return _thread_local.session_id
    
    # Try to inherit from parent if we don't have a session yet
    _inherit_parent_session()
    
    # Check again after potential inheritance
    if _thread_local.session_stack:
        return _thread_local.session_stack[-1]
    if _thread_local.session_id:
        return _thread_local.session_id
    
    # No session found
    return None

def get_session_name():
    """Get the current session name, if any."""
    # Ensure task monitoring is setup if we're in an async context
    try:
        _setup_task_cleanup()
    except Exception:
        pass
    
    # First check if we're in an async context
    try:
        current_task = asyncio.current_task()
        if current_task:
            task_id = id(current_task)
            
            # Direct task session
            with _session_lock:
                if task_id in _async_task_sessions:
                    return _async_task_sessions[task_id]['session_name']
                
                # Check parent task's session (for nested tasks)
                if task_id in _async_task_parents:
                    parent_id = _async_task_parents[task_id]
                    if parent_id in _async_task_sessions:
                        # Create a copy for this task too for future lookups
                        _async_task_sessions[task_id] = _async_task_sessions[parent_id].copy()
                        return _async_task_sessions[task_id]['session_name']
                
                # Check event loop-specific sessions
                loop = asyncio.get_running_loop()
                if loop in _loop_sessions and 'current_session_name' in _loop_sessions[loop]:
                    return _loop_sessions[loop]['current_session_name']
    except RuntimeError:
        # Not in an async context
        pass
    
    _init_thread_local()
    
    # Try to inherit from parent if we don't have a session yet
    if not hasattr(_thread_local, 'current_session_name') or not _thread_local.current_session_name:
        _inherit_parent_session()
        
    return getattr(_thread_local, 'current_session_name', None)

def set_session_id(session_id, session_name=None):
    """Set the session ID for the current thread.
    
    Also registers the session ID globally for cross-thread usage.
    
    Args:
        session_id: The session ID to set
        session_name: Optional name to associate with this session
    """
    _init_thread_local()
    _thread_local.session_id = session_id
    
    # Register in global sessions for inheritance by child threads
    current_thread = threading.current_thread().name
    _parent_thread_sessions[current_thread] = (session_id, session_name)
    
    if session_name:
        _thread_local.current_session_name = session_name
        if not hasattr(_thread_local, 'named_sessions'):
            _thread_local.named_sessions = {}
        _thread_local.named_sessions[session_name] = session_id
        
        # Store in global sessions by name
        _global_sessions_by_name[session_name] = session_id

def clear_session_id():
    """Clear the session ID for the current thread."""
    _init_thread_local()
    _thread_local.session_id = None
    _thread_local.session_stack = []
    
    # Don't clear named sessions dictionary - we want persistence
    # But do clear current session name
    _thread_local.current_session_name = None
    
    # Remove from parent thread register
    current_thread = threading.current_thread().name
    if current_thread in _parent_thread_sessions:
        del _parent_thread_sessions[current_thread]

def session(session_name=None):
    """Create or access a session manager for the given session name.
    
    This can be used both as a context manager or to get a reference to
    an existing session manager:
    
    # As a context manager:
    with session("my_session") as s:
        s.add_step({"key": "value"})
    
    # To access an existing session:
    session("my_session").add_step({"key": "value"})
    
    In concurrent environments (like multiple async functions decorated with @begin_session),
    this function will return the SessionManager associated with the current execution context.
    
    Args:
        session_name: Optional name for the session. If provided and this
                     session has been used before, the same session ID will be reused,
                     unless we're in an active session context with that name.
                     
    Returns:
        SessionManager: A manager for the session that can be used to add metadata steps.
    """
    # When using session() inside concurrent @begin_session functions,
    # we need to ensure it gets the correct session manager for the current execution context
    return SessionManager(session_name)

def begin_session(session_name_or_func=None):
    """Decorator or function to begin a session with automatic variable tracking.
    
    This can be used as:
    
    1. A decorator around a function:
       @begin_session
       def my_func():
           # Variables are automatically tracked
           user_id = "user123"
           question = "What is AI?"
           # Use tropir_prompt for prompts you want to track
           prompt = tropir_prompt("system_prompt", "You are helpful")
    
    2. A decorator with a session name:
       @begin_session("my_session")
       def my_func():
           # Variables are automatically tracked for this session
           temperature = 0.7
           prompt = tropir_prompt("user_prompt", "Answer: {question}")
    
    3. A direct function call to start a session:
       begin_session("my_session")
       # Later:
       session("my_session").add_step({"data": "value"})
       end_session("my_session")  # End the session
    
    Args:
        session_name_or_func: Optional name for the session, or the function to decorate.
                             If a name is provided and this session has been used before,
                             the same session ID will be reused. If used as @begin_session
                             with no arguments, the function name is used as the session name.
    """
    _init_thread_local()
    _check_rerun_mode()  # Initialize rerun mode detection

    param = session_name_or_func

    # Case 1: Used as @begin_session (param is the function to decorate)
    if callable(param) and not isinstance(param, functools.partial): # Make sure it's a function/method not a partial
        func_to_decorate = param
        session_name_to_use = getattr(func_to_decorate, '__name__', 'unnamed_session')

        if inspect.iscoroutinefunction(func_to_decorate):
            @functools.wraps(func_to_decorate)
            async def async_wrapper(*args, **kwargs):
                # Generate a unique session ID for this call
                unique_session_id = str(uuid.uuid4())
                session_manager = SessionManager(session_name_to_use)
                session_manager.session_id = unique_session_id
                
                # Update thread-local and global stores
                _thread_local.named_sessions[session_name_to_use] = unique_session_id
                _global_sessions_by_name[session_name_to_use] = unique_session_id
                
                with session_manager:
                    # Capture execution context at session start
                    _capture_execution_context(unique_session_id)
                    
                    try:
                        result = await func_to_decorate(*args, **kwargs)
                        return result
                    finally:
                        # Trigger auto-evaluation before ending session
                        try:
                            _trigger_auto_evaluation(unique_session_id)
                        except Exception as e:
                            logging.debug(f"⚠️ Tropir: Auto-evaluation trigger failed: {e}")
            return async_wrapper
        else:
            @functools.wraps(func_to_decorate)
            def sync_wrapper(*args, **kwargs):
                _init_thread_local()  # Ensure thread-local is initialized
                
                # Generate a unique session ID for this call
                unique_session_id = str(uuid.uuid4())
                session_manager = SessionManager(session_name_to_use)
                session_manager.session_id = unique_session_id
                
                # Update thread-local and global stores
                _thread_local.named_sessions[session_name_to_use] = unique_session_id
                _global_sessions_by_name[session_name_to_use] = unique_session_id
                
                with session_manager:
                    # Capture execution context at session start
                    _capture_execution_context(unique_session_id)
                    
                    try:
                        # Execute the function
                        result = func_to_decorate(*args, **kwargs)
                        return result
                    finally:
                        # Trigger auto-evaluation before ending session
                        try:
                            _trigger_auto_evaluation(unique_session_id)
                        except Exception as e:
                            logging.debug(f"⚠️ Tropir: Auto-evaluation trigger failed: {e}")
            return sync_wrapper

    # Case 2: Used as @begin_session("name") or @begin_session() which returns a decorator,
    # or as a direct call: begin_session("name")
    # Here, param is the session name (a string) or None.
    else:
        session_name_from_call = param  # This is the name passed like begin_session("my_name"), or None

        def decorator_factory(func_to_decorate):
            # If @begin_session() was used, session_name_from_call is None; use func_to_decorate name.
            # If @begin_session("my_name") was used, session_name_from_call is "my_name".
            actual_session_name = session_name_from_call if session_name_from_call is not None \
                                else getattr(func_to_decorate, '__name__', 'unnamed_session')

            if inspect.iscoroutinefunction(func_to_decorate):
                @functools.wraps(func_to_decorate)
                async def async_wrapper(*args, **kwargs):
                    # Generate a unique session ID for each call (with the same name)
                    unique_session_id = str(uuid.uuid4())
                    # Create a new SessionManager with this ID but reusing the name
                    session_manager = SessionManager(actual_session_name)
                    session_manager.session_id = unique_session_id
                    
                    # Track session for this specific async task
                    current_task = asyncio.current_task()
                    if current_task:
                        _async_task_sessions[id(current_task)] = {
                            'session_id': unique_session_id,
                            'session_name': actual_session_name
                        }
                    
                    # Also update the thread-local and global store
                    _thread_local.named_sessions[actual_session_name] = unique_session_id
                    _global_sessions_by_name[actual_session_name] = unique_session_id
                    
                    # Use __enter__ and __exit__ manually to ensure proper session management
                    session_manager.__enter__()
                    try:
                        # Get the calling frame for variable tracking
                        frame = inspect.currentframe()
                        try:
                            # Move to the actual function frame (skip wrapper frames)
                            caller_frame = frame.f_back
                            while caller_frame and caller_frame.f_code.co_name in ['async_wrapper', 'sync_wrapper']:
                                caller_frame = caller_frame.f_back
                            
                            if caller_frame:
                                # Inject variables in rerun mode
                                _inject_variables_into_frame(caller_frame, unique_session_id)
                                
                                # Execute the function
                                result = await func_to_decorate(*args, **kwargs)
                                
                                # Note: Automatic frame variable capture was removed in favor of explicit tropir_variable() annotations
                                # Previously: _capture_frame_variables(caller_frame, unique_session_id, f"{actual_session_name}_post_execution")
                                
                                return result
                            else:
                                return await func_to_decorate(*args, **kwargs)
                        finally:
                            del frame
                    finally:
                        # Trigger auto-evaluation before cleaning up
                        try:
                            _trigger_auto_evaluation(unique_session_id)
                        except Exception as e:
                            logging.debug(f"⚠️ Tropir: Auto-evaluation trigger failed: {e}")
                        
                        # Clean up the async task tracking
                        if current_task and id(current_task) in _async_task_sessions:
                            del _async_task_sessions[id(current_task)]
                        session_manager.__exit__(None, None, None)
                return async_wrapper
            else:
                @functools.wraps(func_to_decorate)
                def sync_wrapper(*args, **kwargs):
                    # Generate a unique session ID for each call (with the same name)
                    unique_session_id = str(uuid.uuid4())
                    # Create a new SessionManager with this ID but reusing the name
                    session_manager = SessionManager(actual_session_name)
                    session_manager.session_id = unique_session_id
                    _thread_local.named_sessions[actual_session_name] = unique_session_id
                    _global_sessions_by_name[actual_session_name] = unique_session_id
                    
                    # Use __enter__ and __exit__ manually to ensure proper session management
                    session_manager.__enter__()
                    try:
                        # Capture execution context at session start
                        _capture_execution_context(unique_session_id)
                        
                        try:
                            # Execute the function
                            result = func_to_decorate(*args, **kwargs)
                            return result
                        finally:
                            pass
                    finally:
                        # Trigger auto-evaluation before cleaning up
                        try:
                            _trigger_auto_evaluation(unique_session_id)
                        except Exception as e:
                            logging.debug(f"⚠️ Tropir: Auto-evaluation trigger failed: {e}")
                        
                        session_manager.__exit__(None, None, None)
                return sync_wrapper
        
        # If begin_session("some_name") was called directly, this part also starts the session.
        if isinstance(session_name_from_call, str):
            # Create a session manager and start the session
            session_manager = SessionManager(session_name_from_call)
            session_manager.__enter__()
            
            # Store the session manager in thread-local storage for end_session to use
            _thread_local.manually_managed_sessions[session_name_from_call] = session_manager
            
            logging.debug(f"Started session: {session_name_from_call} with ID: {session_manager.session_id} (via direct begin_session call)")

        return decorator_factory

def end_session(session_name=None):
    """Function to end a session.
    
    This is primarily used to end sessions started by direct calls to begin_session.
    For sessions started using the context manager or decorator, the session will
    be ended automatically.
    
    Args:
        session_name: Optional name of the session to end. If not provided,
                     the most recent session will be ended.
    """
    _init_thread_local()
    
    current_thread = threading.current_thread().name
    
    # First check for manually managed sessions
    if hasattr(_thread_local, 'manually_managed_sessions') and session_name in _thread_local.manually_managed_sessions:
        session_manager = _thread_local.manually_managed_sessions[session_name]
        session_id = session_manager.session_id
        
        # Trigger auto-evaluation before ending session
        try:
            _trigger_auto_evaluation(session_id)
        except Exception as e:
            logging.debug(f"⚠️ Tropir: Auto-evaluation trigger failed: {e}")
        
        session_manager.__exit__(None, None, None)
        del _thread_local.manually_managed_sessions[session_name]
        logging.debug(f"Ended manually managed session: {session_name} with ID: {session_id} on thread {current_thread}")
        return
    
    # Otherwise, handle traditional session stack
    if _thread_local.session_stack:
        session_id = _thread_local.session_stack.pop()
        # Clear current session name if it matches the ended session
        if _thread_local.current_session_name == session_name:
            _thread_local.current_session_name = None
            # Remove from parent thread sessions if no more sessions
            if not _thread_local.session_stack:
                if current_thread in _parent_thread_sessions:
                    del _parent_thread_sessions[current_thread]
        
        _revert_requests_patch_if_needed() # Revert requests patch
        _revert_httpx_patch_if_needed() # Revert httpx patch
        logging.debug(f"Ended session: {session_name or 'unnamed'} with ID: {session_id} on thread {current_thread}")
    else:
        logging.warning(f"Attempted to end session {session_name or 'unnamed'} but no active sessions found on thread {current_thread}")

# Monkey-patch threading.Thread to enable automatic session inheritance
_original_thread_init = threading.Thread.__init__

def _thread_init_with_session_inheritance(self, *args, **kwargs):
    # Call the original __init__
    _original_thread_init(self, *args, **kwargs)
    
    # Check if we're in an async context first
    try:
        current_task = asyncio.current_task()
        if current_task and id(current_task) in _async_task_sessions:
            # Store the async task's session for inheritance in the new thread
            self._parent_async_session = _async_task_sessions[id(current_task)]
            return
    except RuntimeError:
        # Not in an async context
        pass
    
    # If not in async context, fall back to thread-based inheritance
    if threading.current_thread().name in _parent_thread_sessions:
        self._parent_session = _parent_thread_sessions[threading.current_thread().name]
    else:
        self._parent_session = None

threading.Thread.__init__ = _thread_init_with_session_inheritance

# Monkey-patch threading.Thread.run to inherit session on start
_original_thread_run = threading.Thread.run

def _thread_run_with_session_inheritance(self):
    # First check for async context inheritance
    if hasattr(self, '_parent_async_session'):
        session_id = self._parent_async_session['session_id']
        session_name = self._parent_async_session['session_name']
        if session_id and session_name:
            # Set thread-local storage for this thread
            set_session_id(session_id, session_name)
            # Also register in thread-specific named sessions
            _init_thread_local()
            _thread_local.named_sessions[session_name] = session_id
            logging.debug(f"Thread {self.name} inherited async session {session_name} ({session_id})")
    # Otherwise fall back to thread session inheritance
    elif hasattr(self, '_parent_session') and self._parent_session:
        session_id, session_name = self._parent_session
        if session_id and session_name:
            set_session_id(session_id, session_name)
            logging.debug(f"Thread {self.name} inherited thread session {session_name} ({session_id})")
    
    # Call the original run method
    _original_thread_run(self)

threading.Thread.run = _thread_run_with_session_inheritance

def capture_async_session_context():
    """
    Capture the current async session context for use in thread workers.
    
    This is useful when you need to explicitly pass the session context to a thread,
    such as in ThreadPoolExecutor which might not properly inherit the async context.
    
    Returns:
        dict: A dictionary containing the session context, or None if not in an async context.
    """
    # Ensure task monitoring is setup if we're in an async context
    try:
        _setup_task_cleanup()
    except Exception:
        pass
    
    try:
        current_task = asyncio.current_task()
        if current_task and id(current_task) in _async_task_sessions:
            # Make a copy to avoid reference issues
            with _session_lock:
                return _async_task_sessions[id(current_task)].copy()
                
        # Check parent task session
        if current_task and id(current_task) in _async_task_parents:
            parent_id = _async_task_parents[id(current_task)]
            if parent_id in _async_task_sessions:
                with _session_lock:
                    # Create a copy for this task too for future lookups
                    _async_task_sessions[id(current_task)] = _async_task_sessions[parent_id].copy()
                    return _async_task_sessions[id(current_task)].copy()
                    
        # Check event loop specific sessions
        loop = asyncio.get_running_loop()
        if loop in _loop_sessions and 'current_session' in _loop_sessions[loop]:
            return _loop_sessions[loop]['current_session'].copy()
    except RuntimeError:
        # Not in an async context
        pass
    
    # If not in an async context or no session found, return thread-local session info
    _init_thread_local()
    session_id = get_session_id()
    session_name = get_session_name()
    
    if session_id and session_name:
        return {
            'session_id': session_id,
            'session_name': session_name,
            'thread_id': threading.get_ident()
        }
    return None

def apply_session_context(context_dict):
    """
    Apply a captured session context to the current thread or async task.
    
    Args:
        context_dict: The session context dictionary from capture_async_session_context().
    """
    if not context_dict:
        return
        
    session_id = context_dict.get('session_id')
    session_name = context_dict.get('session_name')
    
    if not session_id or not session_name:
        return
        
    # Set in thread-local storage with thread safety
    with _session_lock:
        set_session_id(session_id, session_name)
        
        # Also try to set in async task context if we're in an async context
        try:
            current_task = asyncio.current_task()
            if current_task:
                task_id = id(current_task)
                _async_task_sessions[task_id] = {
                    'session_id': session_id,
                    'session_name': session_name,
                    'applied_at': time.time()
                }
                
                # Register for cleanup
                current_task.add_done_callback(lambda t: _cleanup_task_session(task_id))
        except RuntimeError:
            # Not in an async context
            pass

# Register cleanup handler for process exit
def _cleanup_sessions():
    """Clean up session tracking to prevent memory leaks."""
    global _async_task_sessions, _async_task_parents, _loop_sessions
    
    with _session_lock:
        # Clear global dictionaries
        _async_task_sessions.clear()
        _async_task_parents.clear()
        _loop_sessions.clear()
        
        # Reset task factory for each loop
        try:
            for loop in asyncio.all_event_loops():
                if loop.is_running():
                    loop.set_task_factory(None)
        except Exception:
            pass

# Register the cleanup handler
atexit.register(_cleanup_sessions)

# Force cleanup on import to prevent issues with module reloading
_cleanup_sessions()

# --- SDK Auto-Patching for Session Header Injection ---

def _create_patched_init(original_init, headers_kwarg_name="default_headers"):
    """
    Creates a patched __init__ method for an SDK client that injects Tropir session headers.
    """
    @functools.wraps(original_init)
    def patched_init(self, *args, **kwargs):
        _init_thread_local()  # Ensure thread-local is set up
        session_id = get_session_id()
        session_name = get_session_name()

        # If there's no active Tropir session, call the original __init__ without changes.
        if not session_id and not session_name:
            return original_init(self, *args, **kwargs)

        user_headers_arg = kwargs.get(headers_kwarg_name)
        
        final_headers = {}
        if isinstance(user_headers_arg, collections.abc.Mapping):
            final_headers.update(user_headers_arg)  # Start with a copy of user's headers
        elif user_headers_arg is not None:
            # Log a warning if the header argument is not a Mapping and not None.
            logging.warning(
                f"Tropir: SDK client {original_init.__qualname__} "
                f"initialized with '{headers_kwarg_name}' of type {type(user_headers_arg)}. "
                f"Expected a Mapping or None. Tropir session headers will not be injected for this client."
            )
            return original_init(self, *args, **kwargs) # Call original to avoid breaking client

        # `final_headers` is now a mutable dict:
        # - Contains a copy of user's headers if they provided a Mapping.
        # - Is an empty dict if user provided None or did not provide the argument.

        modified_by_tropir = False
        if session_id:
            if final_headers.get("X-Session-ID") != str(session_id):
                if "X-Session-ID" in final_headers:
                    logging.debug(f"Tropir: Overriding user-set 'X-Session-ID' in '{headers_kwarg_name}' for {original_init.__qualname__} "
                                  f"with active session ID ({str(session_id)}).")
                final_headers["X-Session-ID"] = str(session_id)
                modified_by_tropir = True
        
        if session_name:
            if final_headers.get("X-Session-Name") != str(session_name):
                if "X-Session-Name" in final_headers:
                     logging.debug(f"Tropir: Overriding user-set 'X-Session-Name' in '{headers_kwarg_name}' for {original_init.__qualname__} "
                                   f"with active session name ('{str(session_name)}').")
                final_headers["X-Session-Name"] = str(session_name)
                modified_by_tropir = True
        
        # Update the headers argument in kwargs.
        # If user_headers_arg was None, it now becomes a dict with session headers.
        # If user_headers_arg was a Mapping, it's updated with session headers.
        kwargs[headers_kwarg_name] = final_headers
        
        if modified_by_tropir:
             logging.debug(f"Tropir: Applied session headers to '{headers_kwarg_name}' for {original_init.__qualname__}. Result: {final_headers}")
        
        return original_init(self, *args, **kwargs)
    
    # Mark the patched init to avoid re-patching
    patched_init._tropir_patched = True
    return patched_init

def _try_patch_sdk(module_name, client_class_name_parts, headers_kwarg_name="default_headers"):
    """
    Attempts to import and patch the __init__ method of an SDK client class.
    client_class_name_parts can be a list for nested classes, e.g., ["OpenAI", "Chat"]
    """
    try:
        module = __import__(module_name, fromlist=[client_class_name_parts[0]])
        
        client_class = module
        for part in client_class_name_parts:
            client_class = getattr(client_class, part, None)
            if client_class is None:
                break
        
        if client_class and hasattr(client_class, '__init__'):
            # Check if already patched
            if getattr(client_class.__init__, '_tropir_patched', False):
                logging.debug(f"Tropir: {module_name}.{'.'.join(client_class_name_parts)} __init__ already patched.")
                return

            original_init = client_class.__init__
            patched_init_method = _create_patched_init(original_init, headers_kwarg_name)
            client_class.__init__ = patched_init_method
            logging.info(f"Tropir: Successfully patched {module_name}.{'.'.join(client_class_name_parts)} to auto-inject session headers.")
        else:
            logging.debug(f"Tropir: Could not find {module_name}.{'.'.join(client_class_name_parts)} for patching.")

    except ImportError:
        logging.debug(f"Tropir: SDK module '{module_name}' not found, skipping patch for {'.'.join(client_class_name_parts)}.")
    except Exception as e:
        logging.warning(f"Tropir: Failed to patch {module_name}.{'.'.join(client_class_name_parts)}: {e}", exc_info=False) # exc_info=True for more detail if needed

def _auto_patch_known_sdks():
    """
    Automatically attempts to patch known SDKs for session header injection.
    """
    logging.debug("Tropir: Attempting to auto-patch known SDKs for session tracking.")
    # OpenAI
    _try_patch_sdk("openai", ["OpenAI"], headers_kwarg_name="default_headers")
    _try_patch_sdk("openai", ["AsyncOpenAI"], headers_kwarg_name="default_headers")
    
    # Anthropic
    _try_patch_sdk("anthropic", ["Anthropic"], headers_kwarg_name="default_headers")
    _try_patch_sdk("anthropic", ["AsyncAnthropic"], headers_kwarg_name="default_headers")
    
    # Add other SDKs here if needed, e.g.:
    # _try_patch_sdk("google.cloud", ["aiplatform", "gapic", "PredictionServiceClient"], headers_kwarg_name="client_options") # Example, actual arg may vary
    logging.debug("Tropir: SDK auto-patching attempt finished.")

# Automatically apply patches when this module is imported.
_auto_patch_known_sdks()

# NEW: LLM Call Context Manager
class TropirLLMCall:
    """
    Context manager for tracking tropir_prompt and tropir_variable usage within an LLM call.
    
    Usage:
        with tropir_llm_call("query_decomposition") as llm_call:
            prompt = tropir_prompt("decompose_prompt", "Break down: {question}")
            question = tropir_variable("question", "What is AI?")
            final_prompt = prompt.format(question=question)
            response = generate_text(final_prompt)
            llm_call.set_response(response)
    """
    
    def __init__(self, call_name: str = None, model: str = None, **kwargs):
        self.call_name = call_name or "unnamed_llm_call"
        self.call_id = str(uuid.uuid4())
        self.model = model
        self.metadata = kwargs
        self.start_time = None
        self.end_time = None
        self.response = None
        self.error = None
        
    def __enter__(self):
        self.start_time = time.time()
        
        # Initialize call context
        _llm_call_context[self.call_id] = {
            'call_name': self.call_name,
            'call_id': self.call_id,
            'session_id': get_session_id(),
            'model': self.model,
            'metadata': self.metadata,
            'prompts_used': {},
            'variables_used': {},
            'start_time': self.start_time,
            'llm_calls': []  # For nested/multiple actual LLM calls
        }
        
        # Set current call ID in thread local
        _current_llm_call_id.call_id = self.call_id
        
        logging.debug(f"🎯 Tropir: Started LLM call context '{self.call_name}' (ID: {self.call_id})")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        
        # Clear current call ID
        _current_llm_call_id.call_id = None
        
        # Finalize call context
        if self.call_id in _llm_call_context:
            context = _llm_call_context[self.call_id]
            context['end_time'] = self.end_time
            context['duration'] = self.end_time - self.start_time
            context['response'] = self.response
            context['error'] = str(exc_val) if exc_val else None
            
            # Save to span metadata
            span = get_current_span()
            if span:
                llm_call_data = {
                    'call_name': self.call_name,
                    'call_id': self.call_id,
                    'model': self.model,
                    'duration': context['duration'],
                    'prompts_used': list(context['prompts_used'].keys()),
                    'prompt_details': context['prompts_used'],
                    'variables_used': list(context['variables_used'].keys()),
                    'variable_details': context['variables_used'],
                    'metadata': self.metadata,
                    'error': context['error']
                }
                
                span.add(f"llm_call_{self.call_name}_{self.call_id[:8]}", llm_call_data)
                
                # Get existing mappings or create new dict
                existing_mappings = span.metadata.get("llm_call_mappings_all", {})
                
                # Add this call's mapping
                existing_mappings[self.call_id] = {
                    'call_name': self.call_name,
                    'prompts': list(context['prompts_used'].keys()),
                    'variables': list(context['variables_used'].keys()),
                    'timestamp': self.start_time
                }
                
                # Use span.add() to trigger database update (not direct assignment)
                span.add("llm_call_mappings_all", existing_mappings)
            
            # Log summary
            logging.info(f"✅ Tropir: Completed LLM call '{self.call_name}' - "
                        f"Used {len(context['prompts_used'])} prompts, "
                        f"{len(context['variables_used'])} variables")
            
            # Clean up context after a delay (for debugging)
            # Note: In production, you might want to persist this data
            def cleanup():
                time.sleep(60)  # Keep for 1 minute for debugging
                if self.call_id in _llm_call_context:
                    del _llm_call_context[self.call_id]
            
            cleanup_thread = threading.Thread(target=cleanup, daemon=True)
            cleanup_thread.start()
    
    def set_response(self, response: Any):
        """Set the response from the LLM call."""
        self.response = response
        if self.call_id in _llm_call_context:
            _llm_call_context[self.call_id]['response'] = response
    
    def add_llm_call(self, log_id: str, messages: list = None, **kwargs):
        """Add an actual LLM call that was made within this context."""
        if self.call_id in _llm_call_context:
            call_data = {
                'log_id': log_id,
                'timestamp': time.time(),
                'messages': messages,
                **kwargs
            }
            _llm_call_context[self.call_id]['llm_calls'].append(call_data)

def tropir_llm_call(call_name: str = None, model: str = None, **kwargs) -> TropirLLMCall:
    """
    Context manager for tracking LLM calls and grouping prompts/variables.
    
    Usage:
        with tropir_llm_call("query_decomposition", model="gpt-4") as llm_call:
            # Any tropir_prompt or tropir_variable calls here will be tracked
            system_prompt = tropir_prompt("system", "You are helpful")
            messages = [{"role": "system", "content": system_prompt}]
            response = generate_text(messages=messages, model=model)
            llm_call.set_response(response)
    """
    return TropirLLMCall(call_name, model, **kwargs)

def tropir_register_prompt_param(prompt_text: str, prompt_id: str = None, role: str = None):
    """
    Register a prompt that was passed as a function parameter with the current LLM call.
    This allows tracking prompts that were created outside the LLM call context.
    
    Usage:
        def generate_response(system_prompt: str, user_prompt: str):
            with tropir_llm_call("synthesis") as llm_call:
                # Register prompts passed as parameters
                tropir_register_prompt_param(system_prompt, "synthesis_system", "system")
                tropir_register_prompt_param(user_prompt, "synthesis_user", "user")
                
                # Use the prompts in LLM call
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                response = generate_text(messages=messages)
                llm_call.set_response(response)
    
    Args:
        prompt_text: The prompt text that was passed as a parameter
        prompt_id: Optional prompt ID (will try to look up if not provided)
        role: Optional role (system/user/assistant)
    """
    if not prompt_text:
        return
        
    # Check if we're in an LLM call context
    if not hasattr(_current_llm_call_id, 'call_id') or not _current_llm_call_id.call_id:
        logging.debug("tropir_register_prompt_param called outside LLM call context")
        return
        
    call_id = _current_llm_call_id.call_id
    if call_id not in _llm_call_context:
        return
        
    # Try to look up prompt metadata if we have it
    prompt_metadata = _prompt_metadata.get(prompt_text)
    if not prompt_metadata:
        # Try truncated version
        truncated = prompt_text[:100] if len(prompt_text) > 100 else prompt_text
        prompt_metadata = _prompt_metadata.get(truncated)
    
    # Determine prompt_id
    if not prompt_id and prompt_metadata:
        prompt_id = prompt_metadata.get('prompt_id')
    elif not prompt_id:
        # Try to find in _prompt_value_to_id
        prompt_id = _prompt_value_to_id.get(prompt_text)
        if not prompt_id:
            truncated = prompt_text[:100] if len(prompt_text) > 100 else prompt_text
            prompt_id = _prompt_value_to_id.get(truncated)
    
    if not prompt_id:
        # Generate a prompt_id if we couldn't find one
        import hashlib
        prompt_hash = hashlib.md5(prompt_text.encode()).hexdigest()[:8]
        prompt_id = f"param_prompt_{prompt_hash}"
    
    # Determine role
    if not role and prompt_metadata:
        role = prompt_metadata.get('role')
    
    # Register the prompt with the LLM call
    _llm_call_context[call_id]['prompts_used'][prompt_id] = {
        'default_prompt': prompt_text,
        'final_prompt': prompt_text,
        'timestamp': time.time(),
        'role': role,
        'source': 'parameter'  # Mark that this was passed as parameter
    }
    
    logging.debug(f"Registered parameter prompt '{prompt_id}' with LLM call '{_llm_call_context[call_id]['call_name']}'")

def get_llm_call_context(call_id: str = None) -> Optional[Dict[str, Any]]:
    """
    Get the context for a specific LLM call or the current one.
    
    Args:
        call_id: Optional call ID. If not provided, returns current call context.
        
    Returns:
        Dictionary with LLM call context or None
    """
    if not call_id:
        # Get current call ID from thread local
        if hasattr(_current_llm_call_id, 'call_id'):
            call_id = _current_llm_call_id.call_id
    
    if call_id and call_id in _llm_call_context:
        return _llm_call_context[call_id].copy()
    
    return None

def get_all_llm_call_mappings(session_id: str = None) -> Dict[str, Any]:
    """
    Get all LLM call mappings for a session showing which prompts and variables
    were used together.
    
    Args:
        session_id: Optional session ID. Uses current session if not provided.
        
    Returns:
        Dictionary mapping call IDs to their prompt/variable usage
    """
    if not session_id:
        session_id = get_session_id()
    
    if not session_id:
        return {}
    
    # Get from span metadata
    span = get_current_span()
    if span:
        # Check for new format first
        if "llm_call_mappings_all" in span.metadata:
            return span.metadata["llm_call_mappings_all"]
        
        # Fall back to legacy format - collect all numbered entries
        mappings = {}
        for key, value in span.metadata.items():
            if key == "llm_call_mappings" or key.startswith("llm_call_mappings_"):
                if isinstance(value, dict):
                    mappings.update(value)
        
        if mappings:
            return mappings
    
    # Alternatively, build from current context
    mappings = {}
    for call_id, context in _llm_call_context.items():
        if context.get('session_id') == session_id:
            mappings[call_id] = {
                'call_name': context['call_name'],
                'prompts': list(context['prompts_used'].keys()),
                'variables': list(context['variables_used'].keys()),
                'timestamp': context['start_time']
            }
    
    return mappings