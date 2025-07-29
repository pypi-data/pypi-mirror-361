from infinianalytics import InfiniAnalytics

execution = InfiniAnalytics(
            token="rwaJOHBWdJ3wH1WqrW6VuxKrBPYygteiJVUQQwYsaUE4fp5STslFr4hUgumk2R4y",
            automation_id="c286cea0-72d2-4556-b69a-89b3bf6b0a70"
        )


execution.start("Starting the process")
 
execution.event("An event occurred")

execution.warning("A warning occurred")

execution.error("An error occurred", error_id="1234", error_detailed="Detailed error message")

execution.end("Ending the process")
