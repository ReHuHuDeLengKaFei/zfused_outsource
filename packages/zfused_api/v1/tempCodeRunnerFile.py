import os
LOCAL_DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", "..", "..", "database"))
print(LOCAL_DATABASE_PATH)