import logging

loggers: dict[str, logging.Logger]

def getLogger(name: str, subFolder: str = None, backupCount: int = 365) -> logging.Logger:
    """
    get logger object

    :param name: logger name
    :param subFolder: subfolder where log file is stored. default=None means root folder located at: os.path.join(os.getenv('LOCALAPPDATA'),'tdRPA','log')
    :param backupCount: number of daily log backups to retain
    """
