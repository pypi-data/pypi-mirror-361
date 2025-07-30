import time
import sys
import inspect
import linecache
from contextlib import contextmanager
import functools
import tracemalloc


def whip(func_or_name=None, *, use_memory=False):
    if callable(func_or_name):
        return _profile_function(func_or_name, use_memory)
    elif func_or_name is None:
        return lambda func: _profile_function(func, use_memory)
    else:
        return _profile_block(func_or_name, use_memory)


def _profile_function(func, use_memory=False):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        filename = inspect.getsourcefile(func)
        timings = {}

        last_line = {"lineno": None, "start_time": None, "start_mem": None}

        def tracer(frame, event, arg):
            if frame.f_code == func.__code__ and event == "line":
                lineno = frame.f_lineno
                now = time.perf_counter()

                current_mem = (
                    tracemalloc.get_traced_memory()[1] / 1024 if use_memory else 0
                )

                if last_line["lineno"] is not None:
                    duration = now - last_line["start_time"]
                    delta_mem = (
                        current_mem - last_line["start_mem"]
                        if use_memory
                        else 0
                    )
                    timings[last_line["lineno"]] = (
                        duration,
                        delta_mem,
                        linecache.getline(filename, last_line["lineno"]).strip()
                    )

                last_line["lineno"] = lineno
                last_line["start_time"] = now
                last_line["start_mem"] = current_mem

            return tracer

        if use_memory:
            tracemalloc.start()
        sys.settrace(tracer)
        start_total = time.perf_counter()
        result = func(*args, **kwargs)
        end_total = time.perf_counter()
        sys.settrace(None)
        if use_memory:
            tracemalloc.stop()

        print(f"\nProfiling Function: {func.__name__}")
        print(f"Total Time: {end_total - start_total:.6f} seconds")
        if use_memory:
            print(f"Memory measured in KB (approx)")
        print("-" * 60)
        for lineno, (duration, delta_mem, line) in sorted(timings.items()):
            if use_memory:
                print(f"{filename}:{lineno} | {duration:.6f}s | {delta_mem:+.2f} KB | {line}")
            else:
                print(f"{filename}:{lineno} | {duration:.6f}s | {line}")
        print("-" * 60)

        return result

    return wrapper


@contextmanager
def _profile_block(name="Block", use_memory=False):
    if use_memory:
        tracemalloc.start()
        start_mem = tracemalloc.get_traced_memory()[1] / 1024
    print(f"\nTiming block: {name}")
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    if use_memory:
        end_mem = tracemalloc.get_traced_memory()[1] / 1024
        tracemalloc.stop()
        delta = end_mem - start_mem
        print(f"Done in {end - start:.6f}s | Memory: {delta:+.2f} KB")
    else:
        print(f"Done in {end - start:.6f}s")
