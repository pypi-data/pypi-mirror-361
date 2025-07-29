from .manager import LoggerManager
from .progress import download_progress

logger = LoggerManager('Default')

info = logger.info
error = logger.error
debug = logger.debug
catch = logger.catch
warning = logger.warning
critical = logger.critical
sync_catch = logger.sync_catch
