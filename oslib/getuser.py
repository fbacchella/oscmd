try: 
    import pwd
    import os
    euid = os.geteuid()
    user = pwd.getpwuid(euid).pw_name
except ImportError:
    import win32api
    user = win32api.GetUserName()
