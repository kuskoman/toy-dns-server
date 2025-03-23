import dns.message
import dns.dnssec
import dns.name
import dns.rdatatype
import dns.resolver

from toy_dns_server.log.logger import Logger

class DNSSECValidator:
    """This DNSSECValidator is more of an example, than a production-ready implementation.
    It is missing multiple features, such as caching, and root trust anchor handling.
    """
    def __init__(self):
        self._logger = Logger(self)

    def validate(self, response_wire: bytes) -> bool:
        try:
            msg = dns.message.from_wire(response_wire)
            name = msg.question[0].name

            self._logger.debug(f"Validating DNSSEC for {name}")

            for rrset in msg.answer:
                if rrset.rdtype == dns.rdatatype.RRSIG:
                    continue

                if not self._validate_rrset_with_rrsig(msg, rrset):
                    return False

            self._logger.info("DNSSEC validation successful")
            return True

        except Exception as e:
            self._logger.warn(f"DNSSEC validation failed: {e}")
            return False

    def _validate_rrset_with_rrsig(self, msg: dns.message.Message, rrset: dns.rrset.RRset) -> bool:
        covered_type = rrset.rdtype

        rrsig_rrset = [
            rdata
            for rr in msg.answer
            if rr.rdtype == dns.rdatatype.RRSIG and rr.name == rrset.name
            for rdata in rr
        ]

        rrsig = next((r for r in rrsig_rrset if r.covered == covered_type), None)
        if not rrsig:
            self._logger.warn(f"No RRSIG for {covered_type}")
            return False

        dnskey_rrset = self._get_dnskey(msg.question[0].name)
        dns.dnssec.validate(rrset, rrsig, {msg.question[0].name: dnskey_rrset})
        return True

    def _get_dnskey(self, name: dns.name.Name):
        try:
            zone = name.parent() if name.labels > 2 else name
            answer = dns.resolver.resolve(zone, 'DNSKEY')
            return answer
        except Exception as e:
            self._logger.warn(f"Failed to retrieve DNSKEY for {name}: {e}")
            raise
