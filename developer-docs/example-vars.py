"""
Example vars.py for Project APE
This is a template - copy and customize for your clients
"""

# List of clients to process (lowercase, underscores for spaces)
clients = ["example_client"]

# Client configuration: example_client
example_client_name = "Example Corporation"
example_client_industry = "technology"
example_client_subsegments = "cloud services, SaaS platforms, cybersecurity"
example_client_folder = "/app/client_data/ExampleClient"

# AI persona (used in chat prompts)
persona = "experienced enterprise solutions architect"

# Execution mode (fast or deep)
MODE = "fast"

# Dashboard configuration
DASHBOARD_PORT = 8765

# Timing configurations
TIMINGS = {
    'initial_offset': (0.0, 30.0),
    'pdf_consolidation': (25.0, 35.0),
    'source_upload_wait': (30.0, 35.0),
    'ask_prompt_delay': (8.0, 12.0),
    'chat_prompt_delay': (5.0, 8.0),
    'mind_map_generation': (60.0, 90.0),
    'final_summary_delay': (10.0, 15.0),
}

DEEP_TIMINGS = {
    'initial_offset': (0.0, 45.0),
    'pdf_consolidation': (35.0, 45.0),
    'source_upload_wait': (45.0, 60.0),
    'ask_prompt_delay': (15.0, 25.0),
    'chat_prompt_delay': (10.0, 15.0),
    'mind_map_generation': (90.0, 120.0),
    'final_summary_delay': (15.0, 20.0),
}

# Retry configuration
RETRY_CONFIG = {
    'max_attempts': 5,
    'base_delay': 10,
    'ask_max_attempts': 7,
    'ask_base_delay': 30,
}
