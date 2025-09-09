"""
Shared decorators for the application.
"""
import asyncio
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional
import logging
from ..core.exceptions import ValidationException, ApplicationException


def retry(
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,)
):
    """
    Retry decorator for functions that might fail temporarily.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch and retry
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        raise last_exception

                    logging.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {current_delay} seconds..."
                    )

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        raise last_exception

                    logging.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {current_delay} seconds..."
                    )

                    time.sleep(current_delay)
                    current_delay *= backoff

            raise last_exception

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_execution(
        logger: Optional[logging.Logger] = None,
        log_args: bool = False,
        log_result: bool = False,
        log_duration: bool = True
):
    """
    Decorator to log function execution details.

    Args:
        logger: Logger instance to use (default: creates one)
        log_args: Whether to log function arguments
        log_result: Whether to log function result
        log_duration: Whether to log execution duration
    """

    def decorator(func: Callable) -> Callable:
        func_logger = logger or logging.getLogger(func.__module__)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = f"{func.__module__}.{func.__name__}"

            log_msg = f"Starting {func_name}"
            if log_args:
                log_msg += f" with args={args}, kwargs={kwargs}"

            func_logger.info(log_msg)

            try:
                result = await func(*args, **kwargs)

                end_time = time.time()
                duration = end_time - start_time

                success_msg = f"Completed {func_name}"
                if log_duration:
                    success_msg += f" in {duration:.3f}s"
                if log_result:
                    success_msg += f" with result={result}"

                func_logger.info(success_msg)

                return result

            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time

                error_msg = f"Failed {func_name} after {duration:.3f}s: {str(e)}"
                func_logger.error(error_msg)

                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = f"{func.__module__}.{func.__name__}"

            log_msg = f"Starting {func_name}"
            if log_args:
                log_msg += f" with args={args}, kwargs={kwargs}"

            func_logger.info(log_msg)

            try:
                result = func(*args, **kwargs)

                end_time = time.time()
                duration = end_time - start_time

                success_msg = f"Completed {func_name}"
                if log_duration:
                    success_msg += f" in {duration:.3f}s"
                if log_result:
                    success_msg += f" with result={result}"

                func_logger.info(success_msg)

                return result

            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time

                error_msg = f"Failed {func_name} after {duration:.3f}s: {str(e)}"
                func_logger.error(error_msg)

                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def validate_input(**field_validators):
    """
    Decorator to validate function input parameters.

    Args:
        **field_validators: Dictionary of field_name: validator_function pairs

    Example:
        @validate_input(
            email=UserValidator.validate_email,
            password=UserValidator.validate_password
        )
        def create_user(email: str, password: str):
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get function signature to map positional args to parameter names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate each field
            validated_args = {}
            for param_name, value in bound_args.arguments.items():
                if param_name in field_validators:
                    try:
                        validated_value = field_validators[param_name](value)
                        validated_args[param_name] = validated_value
                    except ValidationException:
                        raise
                    except Exception as e:
                        raise ValidationException(param_name, value, str(e))
                else:
                    validated_args[param_name] = value

            # Call the function with validated arguments
            return await func(**validated_args)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get function signature to map positional args to parameter names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate each field
            validated_args = {}
            for param_name, value in bound_args.arguments.items():
                if param_name in field_validators:
                    try:
                        validated_value = field_validators[param_name](value)
                        validated_args[param_name] = validated_value
                    except ValidationException:
                        raise
                    except Exception as e:
                        raise ValidationException(param_name, value, str(e))
                else:
                    validated_args[param_name] = value

            # Call the function with validated arguments
            return func(**validated_args)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def cache_result(ttl: int = 300, key_prefix: str = ""):
    """
    Simple in-memory cache decorator.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys
    """
    cache_storage: Dict[str, Dict[str, Any]] = {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Create cache key
            import hashlib
            import json

            key_data = {
                'function': f"{func.__module__}.{func.__name__}",
                'args': str(args),
                'kwargs': str(sorted(kwargs.items()))
            }
            key_string = json.dumps(key_data, sort_keys=True)
            cache_key = f"{key_prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"

            # Check cache
            current_time = time.time()
            if cache_key in cache_storage:
                cached_data = cache_storage[cache_key]
                if current_time - cached_data['timestamp'] < ttl:
                    return cached_data['result']
                else:
                    # Remove expired entry
                    del cache_storage[cache_key]

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_storage[cache_key] = {
                'result': result,
                'timestamp': current_time
            }

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Create cache key
            import hashlib
            import json

            key_data = {
                'function': f"{func.__module__}.{func.__name__}",
                'args': str(args),
                'kwargs': str(sorted(kwargs.items()))
            }
            key_string = json.dumps(key_data, sort_keys=True)
            cache_key = f"{key_prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"

            # Check cache
            current_time = time.time()
            if cache_key in cache_storage:
                cached_data = cache_storage[cache_key]
                if current_time - cached_data['timestamp'] < ttl:
                    return cached_data['result']
                else:
                    # Remove expired entry
                    del cache_storage[cache_key]

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_storage[cache_key] = {
                'result': result,
                'timestamp': current_time
            }

            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def handle_exceptions(*exception_types, default_return=None, log_error=True):
    """
    Decorator to handle specific exceptions and optionally return a default value.

    Args:
        *exception_types: Exception types to catch
        default_return: Default value to return when exception is caught
        log_error: Whether to log the error
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exception_types as e:
                if log_error:
                    logging.error(f"Exception in {func.__name__}: {str(e)}")

                if default_return is not None:
                    return default_return

                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                if log_error:
                    logging.error(f"Exception in {func.__name__}: {str(e)}")

                if default_return is not None:
                    return default_return

                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def measure_performance(logger: Optional[logging.Logger] = None):
    """
    Decorator to measure and log function performance.

    Args:
        logger: Logger instance to use
    """

    def decorator(func: Callable) -> Callable:
        func_logger = logger or logging.getLogger(func.__module__)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = None

            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())
                start_memory = process.memory_info().rss / 1024 / 1024  # MB
            except ImportError:
                pass

            try:
                result = await func(*args, **kwargs)

                end_time = time.time()
                duration = end_time - start_time

                performance_info = f"{func.__name__} executed in {duration:.3f}s"

                if start_memory is not None:
                    try:
                        end_memory = process.memory_info().rss / 1024 / 1024  # MB
                        memory_diff = end_memory - start_memory
                        performance_info += f", memory change: {memory_diff:+.2f}MB"
                    except:
                        pass

                func_logger.info(performance_info)

                return result

            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                func_logger.error(f"{func.__name__} failed after {duration:.3f}s: {str(e)}")
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = None

            try:
                import psutil
                import os
                process = psutil.Process(os.getpid())
                start_memory = process.memory_info().rss / 1024 / 1024  # MB
            except ImportError:
                pass

            try:
                result = func(*args, **kwargs)

                end_time = time.time()
                duration = end_time - start_time

                performance_info = f"{func.__name__} executed in {duration:.3f}s"

                if start_memory is not None:
                    try:
                        end_memory = process.memory_info().rss / 1024 / 1024  # MB
                        memory_diff = end_memory - start_memory
                        performance_info += f", memory change: {memory_diff:+.2f}MB"
                    except:
                        pass

                func_logger.info(performance_info)

                return result

            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                func_logger.error(f"{func.__name__} failed after {duration:.3f}s: {str(e)}")
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def require_roles(*allowed_roles):
    """
    Decorator to require specific user roles.
    This will be implemented in the web layer with proper dependency injection.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This is a placeholder - actual implementation will be in the web layer
            # with proper user context injection
            return await func(*args, **kwargs)

        # Store allowed roles as function attribute for web layer to use
        wrapper._required_roles = allowed_roles
        return wrapper

    return decorator


def transactional():
    """
    Decorator to mark a function as requiring database transaction.
    The actual transaction management will be implemented in the repository layer.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Mark function as transactional
            # Actual implementation will be in the infrastructure layer
            return await func(*args, **kwargs)

        wrapper._is_transactional = True
        return wrapper

    return decorator