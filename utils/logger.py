
import sys
from loguru import logger
from utils.cfg import Settings

logger.level("ol", no=11, color="<green>")
logger.level("os", no=12, color="<red>")
logger.level("cl", no=13, color="<red><dim>")
logger.level("cs", no=14, color="<green><dim>")

logger.level("sht", no=13, color="<magenta><dim>")
logger.level("lng", no=14, color="<cyan><dim>")

logger.level("fyi", no=19, color="<yellow><dim>")
logger.level("msg", no=20, color="<white>")
logger.level("status", no=21, color="<fg #008080>") # teal, duck green
logger.level("update", no=22, color="<fg #C89B40>") # dark yellow
logger.level("gnews", no=23, color="<cyan>")
logger.level("bnews", no=24, color="<magenta>")
logger.level("important", no=25, color="<yellow> <underline>")
logger.level("alert", no=26, color="<yellow>")

logger.remove()
logger.add(
    sys.stdout, 
    format="[{time:M.D-HH:mm:ss}] |{level}| <level>{message}</level>",
    level=Settings['log_level']
)

# NOTE: TRACE,DEBUG,INFO,SUCCESS,WARNING,ERROR,CRITICAL must use upper case
class Lgr():
    @staticmethod
    def log(*args): logger.log(*args)