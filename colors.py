# ANSI color helpers — no external packages needed

RESET  = "\033[0m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

def ok(msg):
    print(f"{GREEN}✔ {msg}{RESET}")

def err(msg):
    print(f"{RED}✖ {msg}{RESET}")

def info(msg):
    print(f"{CYAN}ℹ {msg}{RESET}")

def warn(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def header(msg):
    print(f"{BOLD}{CYAN}{msg}{RESET}")
