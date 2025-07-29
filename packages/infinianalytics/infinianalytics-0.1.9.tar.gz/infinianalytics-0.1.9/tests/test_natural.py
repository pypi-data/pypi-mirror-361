from infinianalytics.register import InfiniAnalytics
import time

start_time = time.time()
execution = InfiniAnalytics(
            token="randomtoken1",
            automation_id="44444444-4444-4444-4444-444444444444"
        )
print("execution", execution)
print(f"[{time.time() - start_time:.2f}] For initialization")

start_time = time.time()
execution.start("Starting the process")
print(f"[{time.time() - start_time:.2f}] For start")

start_time = time.time()
execution.event("An event occurred")
print(f"[{time.time() - start_time:.2f}] For event")

start_time = time.time()
execution.error("An error occurred", error_id="1234", error_detailed="Detailed error message")
print(f"[{time.time() - start_time:.2f}] For error")

start_time = time.time()
execution.end("Ending the process")
print(f"[{time.time() - start_time:.2f}] For end")
