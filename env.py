import os
from dotenv import load_dotenv


# import the environment


load_dotenv(override=True)


LOCAL_IP = os.getenv('LOCAL_IP')
LOCAL_PORT = os.getenv('LOCAL_PORT')
PI_IP = os.getenv('PI_IP')
PI_PORT = os.getenv('PI_PORT')
PI_PASSWORD = os.getenv('PI_PASSWORD')


print(LOCAL_IP)
print(LOCAL_PORT)
print(PI_IP)
print(PI_PORT)
print(PI_PASSWORD)


