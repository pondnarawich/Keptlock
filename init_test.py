import os


# create the environment variable for testing


os.environ['LOCAL_IP'] = '127.0.0.1'
os.environ['LOCAL_PORT'] = '5000'
os.environ['PI_IP'] = '127.0.0.1'
os.environ['PI_PORT'] = '8000'
os.environ['PI_PASSWORD'] = 'raspberry'


print("Exported Environment")
