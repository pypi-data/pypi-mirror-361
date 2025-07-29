import os
import logging
from colorama import init, Fore, Back, Style

# colorama initialize
init()

# 로그 레벨에 따른 색상 설정
LOG_COLORS = {
    logging.DEBUG: Fore.WHITE,
    logging.INFO: Fore.CYAN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.RED + Back.BLACK + Style.BRIGHT,
}


class ColorLogFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = f"{LOG_COLORS[record.levelno]}[HAiQV] [%(asctime)s] [%(levelname)s] - %(message)s{Style.RESET_ALL}"
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


# 로거 설정
def setup_logger(name, level):
    try:
        logger = logging.getLogger(name)
        if level == 'DEBUG':
            logger.setLevel(logging.DEBUG)
        elif level == 'WARN':
            logger.setLevel(logging.WARN)
        elif level == 'ERROR':
            logger.setLevel(logging.ERROR)
        else:
            logger.setLevel(logging.INFO)

        # 스트림 핸들러 설정
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(ColorLogFormatter())
        logger.addHandler(ch)

        return logger
    except Exception as e:
        print(e)
        return None
