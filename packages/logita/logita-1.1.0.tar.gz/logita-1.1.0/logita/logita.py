import logging
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

class Logita:
    """
    Clase de logging que imprime mensajes coloreados en consola y opcionalmente los guarda en archivo.

    Atributos:
        print_to_console (bool): Si imprime mensajes en consola.
        use_colors (bool): Si usa colores en consola.
        logger (logging.Logger): Logger interno para archivo.
    """

    def __init__(self, log_to_file=False, log_filename="app.log", print_to_console=True, use_colors=True):
        """
        Inicializa la instancia de Logita.

        Args:
            log_to_file (bool): Si se guarda en archivo.
            log_filename (str): Nombre del archivo para logs.
            print_to_console (bool): Si imprime en consola.
            use_colors (bool): Si usa colores en consola.
        """
        self.print_to_console = print_to_console
        self.use_colors = use_colors

        self.logger = logging.getLogger("Logita")
        self.logger.setLevel(logging.DEBUG)

        if log_to_file:
            file_handler = logging.FileHandler(log_filename)
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.color_dict = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "error": Fore.LIGHTRED_EX,
            "warning": Fore.LIGHTYELLOW_EX,
            "debug": Fore.LIGHTBLUE_EX,
            "critical": Fore.LIGHTMAGENTA_EX,
            "exception": Fore.LIGHTWHITE_EX + Style.BRIGHT,
        }

    def _log(self, level, message):
        current_time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        color = self.color_dict.get(level, "") if self.use_colors else ""
        reset = Style.RESET_ALL if self.use_colors else ""

        if self.print_to_console:
            print(f"{current_time} {color}{message}{reset}")

        if self.logger.hasHandlers():
            if level == "exception":
                self.logger.exception(message, exc_info=True)
            else:
                log_func = {
                    "info": self.logger.info,
                    "success": self.logger.info,
                    "error": self.logger.error,
                    "warning": self.logger.warning,
                    "debug": self.logger.debug,
                    "critical": self.logger.critical,
                }.get(level, self.logger.info)
                log_func(message)

    def info(self, message):
        """Log nivel INFO."""
        self._log("info", message)

    def success(self, message):
        """Log nivel SUCCESS (alias de INFO)."""
        self._log("success", message)

    def error(self, message):
        """Log nivel ERROR."""
        self._log("error", message)

    def warning(self, message):
        """Log nivel WARNING."""
        self._log("warning", message)

    def debug(self, message):
        """Log nivel DEBUG."""
        self._log("debug", message)

    def critical(self, message):
        """Log nivel CRITICAL."""
        self._log("critical", message)

    def exception(self, message):
        """Log nivel EXCEPTION con traceback."""
        self._log("exception", message)

    def set_log_level(self, level):
        """
        Cambia el nivel de logging.

        Args:
            level (str): 'debug', 'info', 'warning', 'error' o 'critical'.
        """
        level_dict = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        self.logger.setLevel(level_dict.get(level, logging.DEBUG))
