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

            for rrset in msg.answer:
                if rrset.rdtype == dns.rdatatype.RRSIG:
                    continue

                # finding RRSIG for this RRset
                covered_type = rrset.rdtype
                rrsig_rrset = next(
                    (sig for sig in msg.answer if sig.rdtype == dns.rdatatype.RRSIG and sig.name == rrset.name),
                    None
                )
                if not rrsig_rrset:
                    self._logger.warn(f"No RRSIG for {covered_type}")
                    return False

                rrsig = next((r for r in rrsig_rrset if r.covered == covered_type), None)
                if not rrsig:
                    self._logger.warn(f"No matching RRSIG for type {covered_type}")
                    return False

                dnskey_rrset = self._get_dnskey(name)
                dns.dnssec.validate(rrset, rrsig, {name: dnskey_rrset})

            self._logger.info("DNSSEC validation successful")
            return True

        except Exception as e:
            self._logger.warn(f"DNSSEC validation failed: {e}")
            return False


    def _get_dnskey(self, name: dns.name.Name):
        answer = dns.resolver.resolve(name, 'DNSKEY')
        return answer
