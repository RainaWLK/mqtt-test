import os
import time
import random
import json
from emu import register

def massRegister():
  for i in range(0,10):
    register.register(i)
    time.sleep(0.1)

massRegister()