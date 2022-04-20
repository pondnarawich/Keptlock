import os
from dotenv import load_dotenv


# import the environment


load_dotenv()


A = os.getenv('LOCAL_IP')
LOCAL_PORT = os.getenv('LOCAL_PORT')
PI_IP = os.getenv('PI_IP')
PI_PORT = os.getenv('PI_PORT')
PI_PASSWORD = os.getenv('PI_PASSWORD')


print(A)
