import os
from src.processors import Processor
from src.errors import *

current_path = os.getcwd()
# print(current_path)

# try:
proc = Processor(current_path, os.path.join(current_path, "books"), layer=0)
proc.run()
# except ConstructorError:
#     print()