
# PENTESTING FRAMEWORKS 

---

## POPULAR FRAMEWORKS

*Framework selection is the first decision to make after receiving an engagement brief*.

Relying on a structured methodology provides:
  - **Thoroughness**
  - **Consistency**
  - **Compliance**
  - **Communication**

1. [OWASP Web Security Testing Guide (WSTG)](https://owasp.org/www-project-web-security-testing-guide/) - **Go-to framework for web application assessments**, *web application coverage*
2. [Open Source Security Testing Methodology Manual (OSSTMM)](https://www.isecom.org/OSSTMM.3.pdf) - *Scientific* metrics-driven approach to security testin
3. [NIST Special Publication 800-115](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-115.pdf) - U.S governments technical guide to security testing and assessment; *governmental approach*
4. [Penetration Testing Execution Standard (PTES)](http://www.pentest-standard.org/index.php/Main_Page) - Practical phase-driven standard that mirrors how real engagements are conducted
5. [Information Systems Security Assessment Framework (ISSAF)](https://untrustednetwork.net/files/issaf0.2.1.pdf) - Historical influential methodology with a detailed nine-step assessment model.
    
- The [MITRE ATT&CK](https://attack.mitre.org/) Framework also serves as a good knowledge base
- In the real world: **PTES is like the diagnostic procedure, ATT&CK is like the medical dictionary**

---

## 9-STEP ASSESSMENT MODEL FROM ISSAF

The 9-step assessment model from ISSAF using a company ("TechBridge") as an example:

  1. **Information gathering**: Collect publicly available data about TechBridge. DNS records, WHOIS data, employee profiles on LinkedIn, and technology references in job postings ("experience with Jenkins and GitLab CI required") all feed your understanding of the target.
  2. **Network mapping**: Map the live network topology. You discover TechBridge's external IP range hosts the project portal, a VPN gateway, and a mail server. Internal scanning (once in scope) reveals the Git server, a Jenkins build server, and several developer workstations.
  3. **Vulnerability identification**: Scan the mapped assets for weaknesses. The project portal runs an outdated CMS with a known authentication bypass. The Jenkins server has its administrative console exposed without authentication.
  4. **Penetration**: Attempt initial exploitation. You exploit the unauthenticated Jenkins console to execute system commands on the build server.
  5. **Gaining access and privilege escalation**: Escalate from initial access to higher privileges. From the Jenkins server, you recover stored credentials for the service account that deploys code to production, which has administrative rights on the Git server.
  6. **Enumerating further**: With elevated access, enumerate what is now reachable. From the Git server, you discover repositories containing API keys, database connection strings, and client project source code.
  7. **Compromise remote users/sites (lateral movement)**: Move laterally to other systems. Using the harvested credentials, you access several developer workstations and the internal mail server.
  8. **Maintaining access**: Establish persistent access to demonstrate that a real attacker could retain their foothold. You document (without actually deploying) how a backdoor could be planted in the CI/CD pipeline, persisting across system reboots and deployments.
  9. **Covering tracks**: Demonstrate how an attacker would erase evidence. You document which logs captured your activity and identify gaps in TechBridge's logging that would allow a real adversary to operate undetected.


---

## OTHER FRAMEWORKS

- [WASC Threat Classification](http://projects.webappsec.org/w/page/13246978/Threat%20Classification) - Legacy references
- [CSA Cloud Controls Matrix](https://cloudsecurityalliance.org/research/cloud-controls-matrix) - Cloud security
- [OWASP Mobile Application Security Testing Guide (MASTG)](https://mas.owasp.org/MASTG/) - Mobile (iOS/Android)
- [PCI DSS Penetration Testing Guidelines](https://listings.pcisecuritystandards.org/documents/Penetration-Testing-Guidance-v1_1.pdf) - any engagement involving cardholder data
- [CBEST Framework](https://www.bankofengland.co.uk/financial-stability/operational-resilience-of-the-financial-sector/cbest-threat-intelligence-led-assessments-implementation-guide) - Engagements with UK financial institutions
