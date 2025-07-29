class LogColors:
    """Colors for log messages
    
    :param str HEADER: Header color
    :param str OKBLUE: Blue color
    :param str OKCYAN: Cyan color
    :param str OKGREEN: Green color
    :param str WARNING: Warning color
    :param str FAIL: Fail color
    :param str ENDC: End color
    :param str OKYELLOW: Yellow color
    :param str OKMAGENTA: Magenta color
    :param str OKWHITE: White color
    :param str BOLD: Bold color
    :param str UNDERLINE: Underline"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    OKYELLOW = '\033[93m'
    OKMAGENTA = '\033[35m'
    OKWHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'