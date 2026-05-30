import os
import shutil
import subprocess
import sys

# -- ANSI COLOURS
#
#
R = "\033[91m"  # Red - findings
G = "\033[92m"  # Green - all clear
Y = "\033[93m"  # Yellow - info/output
B = "\033[94m"  # Blue - headers
W = "\033[97m"  # White - body text
DIM = "\033[2m"
RST = "\033[0m"


def banner(title):
    print(f"\n{B}{'-' * 60}")
    print(f"{title}")
    print(f"{'-' * 60}{RST}")


def found(msg):
    print(f"{R}!FOUND: {W}{msg}{RST}")


def info(msg):
    print(f"{Y}-> {W}{msg}{RST}")


def ok(msg):
    print(f"{G}OK: {msg}{RST}")


def run(msg):
    """Run shell command and return stdout"""
    result = subprocess.run(msg, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr


# -- CHECKS
#
#
def check_exists(path):
    banner("1 - FILE EXISTS / BASIC INFO")
    info(f"Target: {path}")
    if not os.path.exists(path):
        found(f"File not found: {path}")
        sys.exit(1)
    ok("File exists")


def check_ls(path):
    banner("2 - ls -la (permissions, size, timestamps)")
    info("Looking for: unusual size, permissions, and timestamps.")
    out, _ = run(f"ls -la {path}")
    print(f"{DIM}{out.strip()}{RST}")

    # Pull size in bytes
    size = os.path.getsize(path)
    info(f"Size reported by os.path.getsize(): {size} bytes.")
    if size == 0:
        found("File is empty - may be a decoy.")
    elif size > 10_000:
        found(f"File is unusually large ({size} bytes) for a simple text file.")
    else:
        ok(f"File size is reasonable ({size} bytes).")
    return size


def main():
    if len(sys.argv) < 2:
        print("Usage: python file-analysis.py <path_to_file>:")
        sys.exit(1)

    path = sys.argv[1]

    print("=== STATIC FILE INSPECTOR ===")

    check_exists(path)
    ls_size = check_ls(path)
    check_wc = (path, ls_size)
    check_cat_a(path)
    data = check_xxd(path)
    check_strings(path)
    check_bytes(path)

    print("Analysis complete. Review any 'FOUND' lines above.")


if __name__ == "__main__":
    main()
