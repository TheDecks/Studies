from typing import Union

import AgentBasedModeling.common.log.fmt_dict as fmt

import logging
import sys
import os

DEFAULT_LEVEL = logging.INFO


class FormattingDict:

    __singleItemFormatter = "\x1b[{style};{font};{background}m"

    def __init__(self, style_definition_dict: dict):
        self.formatting_dict = {
            k: FormattingDict.__singleItemFormatter.format(**v) if isinstance(v, dict) else v
            for k, v in style_definition_dict.items()
        }

    @property
    def formatter(self):
        return self.formatting_dict


class ConsoleLogHandler(logging.StreamHandler):

    _formatter: str
    _formattersByLevel: dict

    _basicFormatString = "{{ASCTIME_STYLE}}{{{{asctime:^{{ASCTIME_LENGTH}}}}}}{{STYLE_EXIT}}|" \
                         "{{NAME_STYLE}}{{{{name:^{{NAME_LENGTH}}}}}}{{STYLE_EXIT}}|" \
                         "{{{0}_STYLE}}{{{{levelname:^{{LEVEL_NAME_LENGTH}}}}}}{{STYLE_EXIT}}|" \
                         "\t{{MESSAGE_STYLE}}{{{{message}}}}{{STYLE_EXIT}}"

    _acceptedLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    def __init__(self, colour_scheme: FormattingDict):
        super().__init__(sys.stdout)
        if sys.platform.lower() == "win32":
            os.system('color')

        self._formattersByLevel = {
            lvl: logging.Formatter(
                ConsoleLogHandler._basicFormatString.format(lvl).format(**colour_scheme.formatter),
                style='{', datefmt='%Y/%m/%d %H:%M:%S'
            ) for lvl in ConsoleLogHandler._acceptedLevels
        }

        self._colour_palette = colour_scheme
        self._formatter = 'INFO'
        self.setFormatter(self._formattersByLevel[self._formatter])

    def switch_formatter(self, level: str):
        self.setFormatter(self._formattersByLevel[level.upper().strip()])
        self._formatter = level.upper().strip()

    def emit(self, record):
        if record.levelname.upper().strip() != self._formatter:
            self.switch_formatter(record.levelname)
        record.name = record.name.split('.')[-1]
        super().emit(record)

    def reformat(self):
        self._formattersByLevel = {
            lvl: logging.Formatter(
                ConsoleLogHandler._basicFormatString.format(lvl).format(**self._colour_palette.formatter),
                style='{', datefmt='%Y/%m/%d %H:%M:%S'
            ) for lvl in ConsoleLogHandler._acceptedLevels
        }

    def switch_colour_palette(self, colour_palette: FormattingDict):
        if isinstance(colour_palette, dict):
            colour_palette = FormattingDict(colour_palette)
        self._colour_palette = colour_palette
        self.reformat()


class LoggerUtil(logging.Logger):

    __level_name_to_int = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }

    _console_handler: ConsoleLogHandler
    _database_level: int = 100

    def __init__(
            self, name: str, level: int = DEFAULT_LEVEL,
            colour_scheme: Union[dict, FormattingDict] = fmt.console_format_palette
    ):
        super().__init__(name=name, level=level)
        if isinstance(colour_scheme, dict):
            colour_scheme = FormattingDict(colour_scheme)
        self._console_handler = ConsoleLogHandler(colour_scheme=colour_scheme)
        self.addHandler(self._console_handler)

    def change_colour_schema(self, colour_palette: FormattingDict):
        self._console_handler.switch_colour_palette(colour_palette)


logging.setLoggerClass(LoggerUtil)


def get_logger(name: str) -> Union[LoggerUtil, logging.Logger]:
    return logging.getLogger(name)
