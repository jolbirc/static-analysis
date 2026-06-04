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


# -- DISPLAY
#
#
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


def check_wc(path, ls_size):
    banner("3 - wc -c (byte count cross-check)")
    info(f"Comparing wc -c ({ls_size} bytes) with os.path.getsize ({ls_size} bytes).")
    out, _ = run(f"wc -c {path}")
    wc_size = int(out.strip().split()[0])
    print(f"{DIM} wc -c: {wc_size} bytes{RST}")

    if wc_size != ls_size:
        found(f"Size mismatch: ls = {ls_size} wc={wc_size}")
    else:
        ok(f"wc -c matches os.path.getsize ({wc_size} bytes).")


def check_cat_a(path):
    banner("4 - cat -A (display non-printable characters, trailing whitespace)")
    info("Looking for: trailing spaces/tabs before EOL.")
    out, _ = run(f"cat -A {path}")
    lines = out.splitlines()
    suspicious = []

    for i, line in enumerate(lines, 1):
        # Trailing whitespace before $ = spaces/tabs hidden
        if line.endswith(" $") or "\t" in line.rstrip("$"):
            suspicious.append((i, line))
        if "^@" in line or "^H" in line or "^[" in line:
            suspicious.append((i, line))

    print(f"{DIM}" + "\n".join(f"    {l}" for l in lines) + f"{RST}")

    if suspicious:
        for lineno, content in suspicious:
            found(f"Line {lineno} has suspicious characters: {content}")
    else:
        ok("No obvious hidden whitespace or control characters.")


# -- SUMMARY
#
#
def summary(findings):
    banner("SUMMARY")
    if findings:
        print(f"    {R}Suspicious findings detected:{RST}")
        for finding in findings:
            print(f"    {R}    -    {finding}{RST}")
    else:
        print(f"    {G}Nothing suspicious found in static analysis.")
        print(f"    Consider: Git history, xattrs, steganography analysis.{RST}")


# -- MAIN
#
#
def main():
    if len(sys.argv) < 2:
        print("Usage: python file-analysis.py <path_to_file>:")
        sys.exit(1)

    path = sys.argv[1]

    print("=== STATIC FILE INSPECTOR ===")

    check_exists(path)
    ls_size = check_ls(path)
    check_wc(path, ls_size)
    check_cat_a(path)
    # data = check_xxd(path)
    # check_strings(path)
    # check_bytes(path)

    # Collect all [!] lines
    print(f"\n{B}{'=' * 60}{RST}")
    print(f"Analysis complete. Review any {R}[!] 'FOUND'{W} lines above.")
    print(f"{B}{'=' * 60}{RST}\n")


if __name__ == "__main__":
    main()
