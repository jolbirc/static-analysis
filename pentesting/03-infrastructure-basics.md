# INFRA PENTESTING


---

## Basic Methodology:
1. Enumeration
2. Vulnerability Analysis
3. Initial Access
4. Privilege Escalation
5. Reporting


---

## Enumeration
Learn as much as you can about the target before doing anything. Such as:
- What ports are open?
- What services are running?
- What versions are behind them?

### Scanning with Nmap
- Run `nmap -sV -sC -oN scan.txt [TARGET_IP]`
  - `-sV` probes open ports to identify the service and version running behind them
  - `-sC` runs Nmap's default set of scripts. These pull banners, support auth methods, etc.
  - `-oN scan.txt` saves the output to a file called scan.txt. **Outputting to a file saves a lot of time during reporting.**

### Things to Look For
- System Info
  - OS
  - Uptime
  - Architecture 
- Users & Groups
  - Admin?
  - System?
  - Group?
- Open ports & services
  - Port numbers and their relevant service
  - Open? Closed?
- Shares
  - FOlder shares, etc
- Vulnerabilities
  - CVE's
  - Severity

---

## Vulnerability Analysis
Ask questions:
- Is (x) service version outdated?
- Are there known exploits?
- Is something misconfigured?

Using the Nmap example above, a method would be to search the open ports, their versions, along with the word 'exploit'! Beyond that:

### Kali's `searchsploit`
- `searchsploit [SERVICE]`
- Lists all known exploits across **all** versions


---

## Initial Access
- If a known exploit is found, check metasploit for a module:
  - `msfconsole`
  - For example, if the module was `unrealircd`, in msfonsole, search: `search unrealircd`
  - Then use: `use [index]`
  - Once loaded: `show options` for config.
    - Set `RHOSTS` to target machine IP, if applicable
    - Attach a relevant payload: `show payloads`
    - E.g., if not much was known about the target: `set payload cmd/unix/reverse`
    - Once payloads are chosen, set relevant `LHOST` (tun0 IP of attacking machine) and `LPORT` .
  - Run `exploit`!

> Note: When you catch a reverse shell, it's a 'dumb shell': no job control, tab complete, and su/sudo won't work because they require TTY.


---

## Privilege Escalation
- Finding files that may help with escalation:
  - `find / -name password* 2>/dev/null` - This command will attempt to find all files on the target system that contain the word 'password' in their name, supressing errors.
  - In this example, if finding passwords from reverse shell, they could be used on other services (such as SSH) if these services were found to be running earlier. 
    - E.g., ssh root@[IP] > enter found password when prompted. Access gained!


---

## Reporting
Keep in mind: **all a client will ever see of your work is your report**!

A good guide:
  - A cover page with your title, name, email address, and version control
  - A table of contents 
  - An executive summary, aimed at the manager who requested the engagement, explaining what was achieved in *non-technical terms*.
  - A technical summary, aimed at the engineering manager or similar, so they understand the impact and can act on it
  - A table of all vulns found, ordered by severity, aimed at both managers and engineers. 
  - Detailed exploitation section, where each vulnerability and its impact are explained. Exploitation steps and proof are shown, and recommendations for mitigations given. 

Using the example from this page:
- Title: Root Password Stored in Plaintext

- Severity: Critical

- Description: The root user's password was found stored in plaintext within the file /etc/password.txt. This file was readable by low-privileged users, allowing any user with shell access to retrieve the root credentials and fully compromise the system.

- Exploitation Steps:

> Obtain a low-privileged shell on the target system.
Read the contents of /etc/password.txt using cat /etc/password.txt.
Use the discovered root password to escalate privileges via ssh root@IP.

- Recommendation: Remove the plaintext password file immediately and rotate the root password. Credentials should never be stored in plaintext on the filesystem. Implement a secrets management solution or use properly configured system authentication mechanisms (such as /etc/shadow with strong hashing). Additionally, enforce the principle of least privilege to restrict file access permissions.
