import os
import datetime


class Logger:
    def __init__(self, log_file=None, level="info", recreate=False, max_len_per_line=100, line_delimiter=[","]):
        # print(log_file)
        self.log_file = log_file
        self.levels = {"debug": 10, "info": 20, "warning": 30, "error": 40, "result": 50, "format": 60}
        self.level = self.levels.get(level.lower(), 20)

        if self.log_file:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w' if recreate else 'a') as f:
                f.write(f"+{'-' * max_len_per_line}+\n")
                timestamp = f'Log started at {self._timestamp}'
                len_timestamp = len(timestamp)
                f.write(
                    f"|{' ' * ((max_len_per_line - len_timestamp) // 2)}{timestamp}{' ' * ((max_len_per_line - len_timestamp) // 2)}|\n")
                f.write(f"+{'-' * max_len_per_line}+\n")
        self.max_len_per_line = max_len_per_line
        self.line_delimiter = line_delimiter
        self.use_time = True

    @property
    def _timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # def _log(self, level_name, message, print_to_console=True):
    #     if self.levels[level_name] >= self.level:
    #         formatted_message = f"[{self._timestamp}] [{level_name.upper()}] {message}"
    #         if print_to_console:
    #             print(formatted_message)
    #         if self.log_file:
    #             with open(self.log_file, 'a') as f:
    #                 f.write(formatted_message + "\n")

    def _ch_in_delimiter(self, ch):
        return ch in self.line_delimiter

    def set_use_time(self, use_time):
        """
        Set whether to use timestamp in log messages.

        Args:
            use_time (bool): If True, include timestamp in log messages.
        """
        self.use_time = use_time

    def _log(self, level_name, message, print_to_console=True):
        if self.levels[level_name] >= self.level:
            if self.use_time:
                info_message = f"[{self._timestamp}] [{level_name.upper()}] "
                len_info_message = len(info_message)
                formatted_message = f"[{self._timestamp}] [{level_name.upper()}] {message}"
            else:
                info_message = f"[{level_name.upper()}] "
                len_info_message = len(info_message)
                formatted_message = f"[{level_name.upper()}] {message}"
            lines = []
            cnt = 0
            last_delimiter = None
            total_length = len(formatted_message)
            last_split = 0
            idx = 0
            while idx < total_length:
                ch = formatted_message[idx]
                if formatted_message[idx:idx + 3] == 'max':
                    _ = 1
                if self._ch_in_delimiter(ch):
                    last_delimiter = idx
                if cnt == self.max_len_per_line:
                    if last_delimiter is not None:
                        line = formatted_message[last_split:last_delimiter + 1]
                        if lines:
                            line = " " * len_info_message + line
                        lines.append(line)
                        cnt = len_info_message
                        last_split = last_delimiter + 1
                        idx = last_delimiter + 1
                        continue
                    else:
                        raise ValueError(
                            f"Line length exceeds {self.max_len_per_line} characters and no delimiter found.")
                if idx == total_length - 1:
                    line = formatted_message[last_split:total_length]
                    if lines:
                        line = " " * len_info_message + line
                    lines.append(line)
                    break
                cnt += 1
                idx += 1

            formatted_message = '\n'.join(lines)
            if print_to_console:
                print(formatted_message)
            if self.log_file:
                with open(self.log_file, 'a') as f:
                    f.write(formatted_message + "\n")

    def debug(self, message, print_to_console=True):
        self._log("debug", message, print_to_console=print_to_console)

    def info(self, message, print_to_console=True):
        self._log("info", message, print_to_console=print_to_console)

    def warning(self, message, print_to_console=True):
        self._log("warning", message, print_to_console=print_to_console)

    def error(self, message, print_to_console=True):
        self._log("error", message, print_to_console=print_to_console)

    def result(self, message, print_to_console=True):
        self._log("result", message, print_to_console=print_to_console)

    def format(self, message, print_to_console=True):
        level_name = "format"
        info_message = f"[{self._timestamp}] [{level_name.upper()}] "
        len_info_message = len(info_message)
        message = message * (self.max_len_per_line - len_info_message)
        self._log("format", message, print_to_console=print_to_console)


# 使用示例
if __name__ == "__main__":
    logger = Logger(log_file="logs/app.log", level="debug")
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.result("This is a result message.")
    logger.format("This is a format message.")
