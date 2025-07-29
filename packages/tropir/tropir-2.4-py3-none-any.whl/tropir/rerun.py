# Enhanced Tropir Python SDK with Rerun State Management
import threading
import uuid
import os
import logging
import functools
from contextlib import contextmanager
import requests
import httpx
from urllib.parse import urlparse
import inspect
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import pickle
import weakref
import atexit
import time
import collections.abc
from typing import Dict, Any, Optional, Union, Callable
from enum import Enum

# ==================== TROPIR STATE MANAGEMENT ====================

class TropirExecutionMode(Enum):
    REGULAR = "regular"
    TROPIR = "tropir"

class TropirStateManager:
    """
    Core state manager that handles switching between regular and Tropir execution modes.
    In Tropir mode, it uses state variables and optimized prompts from the platform.
    """
    
    def __init__(self):
        self._mode = TropirExecutionMode.REGULAR
        self._state_variables = {}
        self._session_context = None
        self._optimized_prompts = {}
        self._rerun_session_id = None
        self._metadata_cache = {}
        
    @property
    def mode(self) -> TropirExecutionMode:
        return self._mode
    
    @property
    def is_tropir_mode(self) -> bool:
        return self._mode == TropirExecutionMode.TROPIR
    
    def enter_tropir_mode(self, rerun_session_id: str, state_variables: Dict[str, Any]):
        """Enter Tropir mode with provided state variables"""
        self._mode = TropirExecutionMode.TROPIR
        self._rerun_session_id = rerun_session_id
        self._state_variables = state_variables.copy()
        logging.info(f"Entered Tropir mode with session: {rerun_session_id}")
        
    def exit_tropir_mode(self):
        """Exit Tropir mode and return to regular execution"""
        self._mode = TropirExecutionMode.REGULAR
        self._state_variables.clear()
        self._optimized_prompts.clear()
        self._rerun_session_id = None
        logging.info("Exited Tropir mode")
    
    def get_state_variable(self, key: str, default=None):
        """Get a state variable - returns Tropir variable in Tropir mode, regular value otherwise"""
        if self.is_tropir_mode and key in self._state_variables:
            return self._state_variables[key]
        return default
    
    def set_metadata_instrumentation(self, key: str, value: Any, metadata_type: str = "auto"):
        """Set metadata that can be automatically captured for future reruns"""
        if not self.is_tropir_mode:
            self._metadata_cache[key] = {
                "value": value,
                "type": metadata_type,
                "timestamp": time.time()
            }

# Global state manager instance
_tropir_state = TropirStateManager()

# ==================== TROPIR DECORATORS AND UTILITIES ====================

def tropir_variable(key: str, default_value=None, metadata_type: str = "input"):
    """
    Decorator/function to handle Tropir state variables.
    In regular mode: returns default_value and instruments the metadata
    In Tropir mode: returns the Tropir state variable value
    """
    def decorator(func_or_value):
        if callable(func_or_value):
            # Used as decorator
            @functools.wraps(func_or_value)
            def wrapper(*args, **kwargs):
                if _tropir_state.is_tropir_mode:
                    tropir_value = _tropir_state.get_state_variable(key)
                    if tropir_value is not None:
                        return tropir_value
                
                # Regular mode - execute function and instrument
                result = func_or_value(*args, **kwargs)
                _tropir_state.set_metadata_instrumentation(key, result, metadata_type)
                return result
            return wrapper
        else:
            # Used as function call
            if _tropir_state.is_tropir_mode:
                tropir_value = _tropir_state.get_state_variable(key, default_value)
                return tropir_value
            else:
                # Instrument the default value
                _tropir_state.set_metadata_instrumentation(key, func_or_value, metadata_type)
                return func_or_value
    
    if default_value is not None:
        return decorator(default_value)
    return decorator

def tropir_prompt(prompt_id: str, default_prompt: str = ""):
    """
    Function to handle Tropir optimized prompts.
    In regular mode: returns default_prompt
    In Tropir mode: fetches optimized prompt from Tropir platform
    """
    if _tropir_state.is_tropir_mode:
        # Fetch optimized prompt from Tropir platform
        optimized = _fetch_optimized_prompt(prompt_id, _tropir_state._rerun_session_id)
        if optimized:
            return optimized
    
    return default_prompt

def _fetch_optimized_prompt(prompt_id: str, session_id: str) -> Optional[str]:
    """Fetch optimized prompt from Tropir platform"""
    try:
        endpoint = os.environ.get("TROPIR_API_ENDPOINT", "https://api.tropir.com")
        response = requests.get(
            f"{endpoint}/api/v1/prompts/optimized/{prompt_id}",
            params={"session_id": session_id},
            headers={"X-TROPIR-API-KEY": os.environ.get("TROPIR_API_KEY")}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("optimized_prompt")
    except Exception as e:
        logging.warning(f"Failed to fetch optimized prompt {prompt_id}: {e}")
    return None

# ==================== TROPIR CONTEXT MANAGERS ====================

@contextmanager
def tropir_rerun_context(rerun_session_id: str, state_variables: Dict[str, Any]):
    """
    Context manager for executing code in Tropir rerun mode.
    Automatically switches to Tropir mode and back.
    """
    _tropir_state.enter_tropir_mode(rerun_session_id, state_variables)
    try:
        yield _tropir_state
    finally:
        _tropir_state.exit_tropir_mode()

# ==================== INTEGRATION WITH EXISTING SESSION SYSTEM ====================

# Import existing session tracking code (keeping the previous implementation)
_thread_local = threading.local()
_global_sessions_by_name = {}
_global_session_managers = {}
_parent_thread_sessions = {}
_async_task_sessions = {}
_async_task_parents = {}
_loop_sessions = {}
_session_lock = threading.RLock()
_process_session_id = os.getpid()

# [Keep all the existing session management code from the original file]
# ... (including SessionManager, begin_session, etc.)

def _init_thread_local():
    if not hasattr(_thread_local, 'session_stack'):
        _thread_local.session_stack = []
    if not hasattr(_thread_local, 'named_sessions'):
        _thread_local.named_sessions = {}
    if not hasattr(_thread_local, 'session_id'):
        _thread_local.session_id = None
    if not hasattr(_thread_local, 'current_session_name'):
        _thread_local.current_session_name = None
    if not hasattr(_thread_local, 'patch_count'):
        _thread_local.patch_count = 0
    if not hasattr(_thread_local, 'httpx_patch_count'):
        _thread_local.httpx_patch_count = 0
    if not hasattr(_thread_local, 'manually_managed_sessions'):
        _thread_local.manually_managed_sessions = {}
    if not hasattr(_thread_local, 'tropir_api_key'):
        _thread_local.tropir_api_key = os.environ.get("TROPIR_API_KEY") or "aabf5916-2090-4ab9-b788-39bd5adc6fff"

def get_default_metadata_endpoint():
    if os.environ.get("ENVIRONMENT") == "dev":
        return "http://localhost:8000/api/v1/metadata"
    else:
        return "https://api.tropir.com/api/v1/metadata"

class SessionManager:
    """Enhanced SessionManager with Tropir rerun support"""
    
    def __init__(self, session_name=None):
        self.session_name = session_name
        self.session_id = None
        self.is_context_manager = False
        self.previous_stack = None
        self.previous_session_name = None
        
        # Check if we're in a tropir rerun context
        if _tropir_state.is_tropir_mode and _tropir_state._rerun_session_id:
            # Use the rerun session ID and send results back to rerun session
            self.session_id = _tropir_state._rerun_session_id
            self._is_rerun_session = True
        else:
            self._is_rerun_session = False
            # Regular session initialization logic
            self._init_regular_session(session_name)
    
    def _init_regular_session(self, session_name):
        """Initialize regular session (existing logic)"""
        try:
            current_task = asyncio.current_task()
            if current_task and id(current_task) in _async_task_sessions:
                task_session = _async_task_sessions[id(current_task)]
                if session_name == task_session['session_name']:
                    self.session_id = task_session['session_id']
                    return
        except RuntimeError:
            pass
        
        _init_thread_local()
        current_stack_session_id = get_session_id()
        
        if current_stack_session_id and session_name == _thread_local.current_session_name:
            self.session_id = current_stack_session_id
            return
            
        if session_name and session_name in _global_session_managers:
            existing_manager = _global_session_managers[session_name]
            self.session_id = existing_manager.session_id
            return
            
        if session_name:
            if session_name in _thread_local.named_sessions:
                self.session_id = _thread_local.named_sessions[session_name]
            elif session_name in _global_sessions_by_name:
                self.session_id = _global_sessions_by_name[session_name]
                _thread_local.named_sessions[session_name] = self.session_id
            
        if session_name:
            _global_session_managers[session_name] = self
    
    def add_step(self, data, step_name=None):
        """Enhanced add_step with Tropir rerun support"""
        if not self.session_id:
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
                    return None
        
        payload = {
            "session_id": self.session_id,
            "metadata": data
        }
        
        if self.session_name:
            payload["session_name"] = self.session_name
            
        if step_name:
            payload["step_name"] = step_name
        
        # Add Tropir-specific metadata if in rerun mode
        if _tropir_state.is_tropir_mode:
            payload["is_rerun"] = True
            payload["rerun_session_id"] = _tropir_state._rerun_session_id
            payload["tropir_mode"] = True
        
        endpoint = os.environ.get("TROPIR_METADATA_ENDPOINT", get_default_metadata_endpoint())
        headers = {"Content-Type": "application/json"}
        
        _add_tropir_headers(headers, endpoint)
        
        try:
            loop = asyncio.get_running_loop()
            is_async = True
        except RuntimeError:
            is_async = False
        
        if not is_async:
            try:
                req = requests.Request('POST', endpoint, json=payload, headers=headers)
                prepared_req = req.prepare()
                
                logging.info(f"Tropir SessionManager: Sending metadata step (sync) to {endpoint}. Payload: {json.dumps(payload)}")
                
                with requests.Session() as s:
                    response = s.send(prepared_req)
                
                if response.status_code >= 400:
                    logging.warning(f"Failed to send metadata: {response.status_code} - {response.text}")
                else:
                    logging.debug(f"Successfully sent metadata for session {self.session_name or 'unnamed'}")
                    
                return response
            except Exception as e:
                logging.warning(f"Error sending metadata: {str(e)}")
                return None
        else:
            async def _async_send():
                try:
                    async with httpx.AsyncClient() as client:
                        logging.info(f"Tropir SessionManager: Sending metadata step (async) to {endpoint}. Payload: {json.dumps(payload)}")
                        request = httpx.Request('POST', endpoint, json=payload, headers=headers)
                        response = await client.send(request)
                        
                        if response.status_code >= 400:
                            logging.warning(f"Failed to send metadata: {response.status_code} - {response.text}")
                        else:
                            logging.debug(f"Successfully sent metadata for session {self.session_name or 'unnamed'}")
                            
                        return response
                except Exception as e:
                    logging.warning(f"Error sending metadata: {str(e)}")
                    return None
            
            return _async_send()

# ==================== HELPER FUNCTIONS ====================

def _add_tropir_headers(headers_obj, url_str):
    """Enhanced header injection with Tropir state awareness"""
    try:
        current_task = asyncio.current_task()
        if current_task and id(current_task) in _async_task_sessions:
            task_session = _async_task_sessions[id(current_task)]
            session_id = task_session['session_id']
            session_name = task_session['session_name']
            
            headers_obj["X-Session-ID"] = str(session_id)
            headers_obj["X-Session-Name"] = str(session_name)
            
            # Add Tropir-specific headers
            if _tropir_state.is_tropir_mode:
                headers_obj["X-Tropir-Mode"] = "true"
                headers_obj["X-Tropir-Rerun-Session"] = _tropir_state._rerun_session_id
            
            tropir_api_key = getattr(_thread_local, 'tropir_api_key', None)
            if not tropir_api_key:
                tropir_api_key = os.environ.get("TROPIR_API_KEY")
            if not tropir_api_key:
                tropir_api_key = "aabf5916-2090-4ab9-b788-39bd5adc6fff"
            if tropir_api_key:
                headers_obj["X-TROPIR-API-KEY"] = tropir_api_key
            
            parsed_url = urlparse(url_str)
            hostname = parsed_url.hostname
            port = parsed_url.port
            is_target_host = (hostname == "api.tropir.com") or \
                (hostname == "localhost" and port == 8000) or \
                (hostname == "host.docker.internal" and port == 8000)
                
            return is_target_host
    except RuntimeError:
        pass
    

    session_id = get_session_id()
    if session_id:
        headers_obj["X-Session-ID"] = str(session_id)
    
    session_name = get_session_name()
    if session_name:
        headers_obj["X-Session-Name"] = str(session_name)
    
    # Add Tropir-specific headers in regular mode too
    if _tropir_state.is_tropir_mode:
        headers_obj["X-Tropir-Mode"] = "true"
        headers_obj["X-Tropir-Rerun-Session"] = _tropir_state._rerun_session_id
    
    tropir_api_key = getattr(_thread_local, 'tropir_api_key', None)
    if not tropir_api_key:
        tropir_api_key = os.environ.get("TROPIR_API_KEY")
    if not tropir_api_key:
        tropir_api_key = "aabf5916-2090-4ab9-b788-39bd5adc6fff"
    
    parsed_url = urlparse(url_str)
    hostname = parsed_url.hostname
    port = parsed_url.port
    is_target_host_for_logging = (hostname == "api.tropir.com") or \
       (hostname == "localhost" and port == 8000) or \
       (hostname == "host.docker.internal" and port == 8000)

    if tropir_api_key:
        headers_obj["X-TROPIR-API-KEY"] = tropir_api_key
    
    return is_target_host_for_logging

def get_session_id():
    """Get current session ID with Tropir awareness"""
    if _tropir_state.is_tropir_mode and _tropir_state._rerun_session_id:
        return _tropir_state._rerun_session_id
    
    # Existing session ID logic
    try:
        current_task = asyncio.current_task()
        if current_task:
            task_id = id(current_task)
            
            with _session_lock:
                if task_id in _async_task_sessions:
                    return _async_task_sessions[task_id]['session_id']
                
                if task_id in _async_task_parents:
                    parent_id = _async_task_parents[task_id]
                    if parent_id in _async_task_sessions:
                        _async_task_sessions[task_id] = _async_task_sessions[parent_id].copy()
                        return _async_task_sessions[task_id]['session_id']
                
                loop = asyncio.get_running_loop()
                if loop in _loop_sessions and 'current_session_id' in _loop_sessions[loop]:
                    return _loop_sessions[loop]['current_session_id']
    except RuntimeError:
        pass
    
    _init_thread_local()
    
    if _thread_local.session_stack:
        return _thread_local.session_stack[-1]
    
    if _thread_local.session_id:
        return _thread_local.session_id
    
    return None

def get_session_name():
    """Get current session name with Tropir awareness"""
    try:
        current_task = asyncio.current_task()
        if current_task:
            task_id = id(current_task)
            
            with _session_lock:
                if task_id in _async_task_sessions:
                    return _async_task_sessions[task_id]['session_name']
                
                if task_id in _async_task_parents:
                    parent_id = _async_task_parents[task_id]
                    if parent_id in _async_task_sessions:
                        _async_task_sessions[task_id] = _async_task_sessions[parent_id].copy()
                        return _async_task_sessions[task_id]['session_name']
                
                loop = asyncio.get_running_loop()
                if loop in _loop_sessions and 'current_session_name' in _loop_sessions[loop]:
                    return _loop_sessions[loop]['current_session_name']
    except RuntimeError:
        pass
    
    _init_thread_local()
    
    if not hasattr(_thread_local, 'current_session_name') or not _thread_local.current_session_name:
        pass
        
    return getattr(_thread_local, 'current_session_name', None)

# ==================== PUBLIC API ====================

def session(session_name=None):
    """Create or access a session manager - enhanced with Tropir support"""
    return SessionManager(session_name)

def begin_session(session_name_or_func=None):
    """Begin session decorator/function - enhanced with Tropir support"""
    _init_thread_local()
    param = session_name_or_func

    if callable(param) and not isinstance(param, functools.partial):
        func_to_decorate = param
        session_name_to_use = getattr(func_to_decorate, '__name__', 'unnamed_session')

        if inspect.iscoroutinefunction(func_to_decorate):
            @functools.wraps(func_to_decorate)
            async def async_wrapper(*args, **kwargs):
                with SessionManager(session_name_to_use) as session_manager:
                    return await func_to_decorate(*args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func_to_decorate)
            def sync_wrapper(*args, **kwargs):
                with SessionManager(session_name_to_use) as session_manager:
                    return func_to_decorate(*args, **kwargs)
            return sync_wrapper
    else:
        session_name_from_call = param

        def decorator_factory(func_to_decorate):
            actual_session_name = session_name_from_call if session_name_from_call is not None \
                                else getattr(func_to_decorate, '__name__', 'unnamed_session')

            if inspect.iscoroutinefunction(func_to_decorate):
                @functools.wraps(func_to_decorate)
                async def async_wrapper(*args, **kwargs):
                    unique_session_id = str(uuid.uuid4())
                    session_manager = SessionManager(actual_session_name)
                    session_manager.session_id = unique_session_id
                    
                    current_task = asyncio.current_task()
                    if current_task:
                        _async_task_sessions[id(current_task)] = {
                            'session_id': unique_session_id,
                            'session_name': actual_session_name
                        }
                    
                    _thread_local.named_sessions[actual_session_name] = unique_session_id
                    _global_sessions_by_name[actual_session_name] = unique_session_id
                    
                    session_manager.__enter__()
                    try:
                        return await func_to_decorate(*args, **kwargs)
                    finally:
                        if current_task and id(current_task) in _async_task_sessions:
                            del _async_task_sessions[id(current_task)]
                        session_manager.__exit__(None, None, None)
                return async_wrapper
            else:
                @functools.wraps(func_to_decorate)
                def sync_wrapper(*args, **kwargs):
                    unique_session_id = str(uuid.uuid4())
                    session_manager = SessionManager(actual_session_name)
                    session_manager.session_id = unique_session_id
                    _thread_local.named_sessions[actual_session_name] = unique_session_id
                    _global_sessions_by_name[actual_session_name] = unique_session_id
                    
                    session_manager.__enter__()
                    try:
                        return func_to_decorate(*args, **kwargs)
                    finally:
                        session_manager.__exit__(None, None, None)
                return sync_wrapper
        
        if isinstance(session_name_from_call, str):
            session_manager = SessionManager(session_name_from_call)
            session_manager.__enter__()
            _thread_local.manually_managed_sessions[session_name_from_call] = session_manager

        return decorator_factory

# ==================== EXAMPLE USAGE ====================

# Example RAG pipeline with Tropir state support
def example_rag_pipeline():
    """
    Example showing how to use Tropir state management in a RAG pipeline
    """
    
    # Get user inputs - in Tropir mode, these come from state variables
    user_id = tropir_variable("user_id", "default_user_123", "input")
    question = tropir_variable("user_question", "What is the weather?", "input") 
    
    # Fetch user name (this would normally be a database call)
    user_name = f"User_{user_id}"  # Simplified for example
    
    # Use optimized prompt in Tropir mode, default prompt otherwise
    system_prompt = tropir_prompt(
        "rag_system_prompt", 
        f"You are a helpful assistant answering {user_name}'s question."
    )
    
    # Your LLM call would go here
    # In a real implementation, this would use OpenAI, Anthropic, etc.
    response = f"Hello {user_name}, regarding your question '{question}': [AI response]"
    
    # Track this step
    with session("rag_pipeline") as s:
        s.add_step({
            "user_id": user_id,
            "question": question,
            "response": response,
            "prompt_used": system_prompt
        }, "rag_response")
    
    return response

# Example of how to run in Tropir rerun mode
def example_rerun_execution():
    """
    Example of how the rerun system would execute the pipeline
    """
    rerun_session_id = "rerun_12345"
    state_variables = {
        "user_id": "user_456",
        "user_question": "What's the capital of France?"
    }
    
    with tropir_rerun_context(rerun_session_id, state_variables):
        result = example_rag_pipeline()
        print(f"Rerun result: {result}")

if __name__ == "__main__":
    # Test regular mode
    print("=== Regular Mode ===")
    result1 = example_rag_pipeline()
    print(result1)
    
    # Test Tropir rerun mode
    print("\n=== Tropir Rerun Mode ===")
    example_rerun_execution()