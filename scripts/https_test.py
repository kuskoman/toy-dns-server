#!/usr/bin/env python3

import requests
from dnslib import DNSRecord

q = DNSRecord.question("example.com", qtype="A")
raw_query = q.pack()

headers = {
    "Content-Type": "application/dns-message"
}
response = requests.post(
    "https://localhost:443/",
    data=raw_query,
    headers=headers,
    verify="./scripts/certs/localhost.crt"
)

print("Status:", response.status_code)
print("Response length:", len(response.content))

if response.status_code == 200:
    reply = DNSRecord.parse(response.content)
    print("Answer:")
    for rr in reply.rr:
        print(f"{rr.rname} -> {rr.rdata}")
else:
    print(response.text)
