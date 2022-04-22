import os


# create the environment variable for testing


os.environ['LOCAL_IP'] = '0.0.0.0'
os.environ['LOCAL_PORT'] = '8000'
os.environ['PI_IP'] = '0.0.0.0'
os.environ['PI_PORT'] = '8000'
os.environ['PI_PASSWORD'] = 'raspberry'


print("Exported Environment")
