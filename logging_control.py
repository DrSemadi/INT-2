import logging

LOGFILE = "./logs/run.log"

def configure_logging() -> int:
    try: 
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', 
                            encoding="utf-8", 
                            level=logging.INFO,
                            filemode="w",
                            filename=LOGFILE)
        return 0
    except Exception as error:
        return -1
