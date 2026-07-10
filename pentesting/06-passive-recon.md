# PASSIVE RECON

---

## COMMON ACTIVITIES

- Querying public DNS records from open resolvers (A, MX, TXT, etc.)
- Searching cert history transparency logs (e.g. crt.sh) for subdomains and issued certs.
- Reviewing job postings on LinkedIn or company career pages for tech stack hints
- Reading public news, press releases, or leaked documents on paste sites
- Checking exposed devices via search engines like Shodan or Censys
- Scanning public GitHub repos for hardcoded credentials, config files, or info on commits

---

- `whois` (being replaced with RDAP - easier to parse and script) What to look for:
  - Redirection chain (Verisign to registrar server).
  - Dates: useful for estimating company age or identifying renewal phishing windows.
  - Name servers: potential new targets (if in scope).
  - Status: locked domains (e.g., clientTransferProhibited) are harder to hijack.

- `nslookup` (e.g. `nslookup -type=TYPE DOMAIN_NAME [SERVER]`)
- `dig` (more modern option of above). Common DNS record types:

| Query type | Result |
|---|---|
| A | IPv4 address(es) for the domain |
| AAAA | IPv6 address(es) for the domain |
| CNAME | Canonical Name: an alias that points one domain name to another |
| MX | Mail Servers: the servers responsible for handling email for the domain |
| SOA | Start of Authority: the primary name server, admin email, and zone serial number |
| TXT | Text Records: arbitrary text, commonly used for SPF, DKIM, DMARC, and domain verification |

| Purpose | Command-line Example |
|---|---|
| Lookup WHOIS record | `whois [DOMAIN]` |
| Lookup DNS A records (legacy) | `nslookup -type=A [DOMAIN]` |
| Lookup DNS MX records at specific server (legacy) | `nslookup -type=MX [DOMAIN] 1.1.1.1` |
| Lookup DNS TXT records (legacy) | `nslookup -type=TXT [DOMAIN]` |
| Lookup DNS A records (recommended) | `dig [DOMAIN] A` |
| Lookup DNS MX records at specific server (recommended) | `dig @1.1.1.1 [DOMAIN] MX` |
| Lookup DNS TXT records (recommended) | `dig [DOMAIN] TXT` |
| Passive subdomain discovery (browser-based) | Visit https://crt.sh and search `%.[DOMAIN]` |

- DNSDumpster: aggresgates public DNS data from sources such as search engines, zone transfer, cert records... good for subdomains. **Not** full enumeration, so remainds passive
- https://crt.sh/ : Certificate transparency logs
- [shodan.io ](https://www.shodan.io/) - focus on devices; IoT equipment
