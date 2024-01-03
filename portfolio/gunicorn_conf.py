import os
from multiprocessing import cpu_count

# Get the absolute path of the current script
current_script_path = os.path.abspath(__file__)

# Get the base directory (parent directory of the script)
base_dir = os.path.dirname(current_script_path)

# Socket Path
bind = f"unix:{base_dir}/gunicorn.sock"

# Worker Options
workers = cpu_count() + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Logging Options
loglevel = "debug"
accesslog = "/root/FastAPI/portfolio/access_log"
errorlog = "/root/FastAPI/portfolio/error_log"
