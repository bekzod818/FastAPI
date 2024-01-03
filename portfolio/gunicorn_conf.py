from multiprocessing import cpu_count

 # Socket Path
bind = 'unix:/root/FastAPI/portfolio/gunicorn.sock'

 # Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

 # Logging Options
loglevel = 'debug'
accesslog = '/root/FastAPI/portfolio/access_log'
errorlog =  '/root/FastAPI/portfolio/error_log'
