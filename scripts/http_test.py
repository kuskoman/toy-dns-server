#! /usr/bin/env python3

import requests
from dnslib import DNSRecord

# Build DNS query
q = DNSRecord.question("example.com", qtype="A")
raw_query = q.pack()

# Send it to your DoH server
headers = {
    "Content-Type": "application/dns-message"
}
response = requests.post("http://127.0.0.1:8053/", data=raw_query, headers=headers)

print("Status:", response.status_code)
print("Response length:", len(response.content))

# Parse response
if response.status_code == 200:
    reply = DNSRecord.parse(response.content)
    print("Answer:")
    for rr in reply.rr:
        print(f"{rr.rname} -> {rr.rdata}")
else:
    print(response.text)

