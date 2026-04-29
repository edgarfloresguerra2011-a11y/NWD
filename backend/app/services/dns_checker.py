"""
DNS Checker: Validates SPF, DKIM, and DMARC records for domains.
Uses DNS-over-HTTPS (DoH) via Cloudflare API for cross-platform compatibility.
No dependency on raw UDP DNS (works on Windows).
"""
import httpx
import json
from typing import Dict, Any, List

DOH_URL = "https://cloudflare-dns.com/dns-query"


async def resolve_dns_txt(domain: str) -> List[str]:
    """Resolve DNS TXT records via Cloudflare DoH API"""
    try:
        # A TXT lookup just needs type=TXT
        url = f"{DOH_URL}?name={domain}&type=TXT"
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(url, headers={"Accept": "application/dns-json"})
            if resp.status_code != 200:
                return []
            data = resp.json()
            records = []
            for answer in data.get("Answer", []):
                if answer.get("type") == 16:  # TXT record type
                    txt = answer.get("data", "")
                    # Remove surrounding quotes if present
                    if txt.startswith('"') and txt.endswith('"'):
                        txt = txt[1:-1]
                    records.append(txt)
            return records
    except Exception:
        return []


async def check_spf(domain: str) -> Dict[str, Any]:
    """Check SPF record"""
    records = await resolve_dns_txt(domain)

    for record in records:
        if record.startswith("v=spf1"):
            return {
                "status": "ok",
                "record": record,
                "details": "SPF record found and valid",
            }

    return {
        "status": "missing",
        "record": None,
        "details": "No SPF record found. Add: v=spf1 include:_spf.google.com ~all",
    }


async def check_dkim(domain: str) -> Dict[str, Any]:
    """Check DKIM record via common selectors"""
    selectors = ["google", "default", "dkim", "selector1", "mail"]
    for selector in selectors:
        dkim_domain = f"{selector}._domainkey.{domain}"
        records = await resolve_dns_txt(dkim_domain)
        for record in records:
            if "v=DKIM1" in record:
                return {
                    "status": "ok",
                    "record": record,
                    "details": f"DKIM record found for selector: {selector}",
                }

    return {
        "status": "missing",
        "record": None,
        "details": "No DKIM record found. Common selectors checked: google, default, dkim, selector1, mail",
    }


async def check_dmarc(domain: str) -> Dict[str, Any]:
    """Check DMARC record"""
    records = await resolve_dns_txt(f"_dmarc.{domain}")

    for record in records:
        if "v=DMARC1" in record:
            policy = "none"
            if "p=reject" in record:
                policy = "reject"
            elif "p=quarantine" in record:
                policy = "quarantine"
            elif "p=none" in record:
                policy = "none"

            return {
                "status": "ok",
                "record": record,
                "details": f"DMARC record found. Policy: {policy}",
            }

    return {
        "status": "missing",
        "record": None,
        "details": "No DMARC record found. Add: v=DMARC1; p=none; rua=mailto:dmarc@{domain}",
    }


async def check_dns(domain: str) -> Dict[str, Any]:
    """Run full DNS check for a domain using DoH"""
    spf, dkim, dmarc = await asyncio.gather(
        check_spf(domain),
        check_dkim(domain),
        check_dmarc(domain),
    )

    return {
        "spf": spf,
        "dkim": dkim,
        "dmarc": dmarc,
    }
