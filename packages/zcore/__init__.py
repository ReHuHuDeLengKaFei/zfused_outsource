import sys

if sys.version_info >= (3, 4):
    import importlib
    reload = importlib.reload
elif (3,4) >= sys.version_info > (3, 4):
    import imp
    reload = imp.reload
else:
    reload = reload