from prometheus_client import Counter, Summary

dns_query_counter = Counter(
    "dns_queries_total",
    "Total number of DNS queries received",
    ["protocol", "source"]
)

dns_query_duration = Summary(
    "dns_query_duration_seconds",
    "Time spent resolving DNS queries"
)

dnssec_validation_counter = Counter(
    "dnssec_validations_total",
    "DNSSEC validation attempts",
    ["result"]
)
