from datetime import datetime


def log(message: str, level="info"):
    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fd = datetime.now().strftime("%Y-%m-%d")

    log_msg = message
    if level != None:
        log_msg = "[{0}] {1}: {2}".format(level.upper(), ct, message)
        
    print(log_msg)
