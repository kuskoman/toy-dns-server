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
            rrsets = {}
            rrsigs = {}

            for rr in msg.answer:
                if rr.rdtype == dns.rdatatype.RRSIG:
                    rrsigs[rr.covered] = rr
                else:
                    rrsets[rr.rdtype] = rr

            for rtype, rrset in rrsets.items():
                rrsig = rrsigs.get(rtype)
                if not rrsig:
                    self._logger.warn(f"No RRSIG for {rtype}")
                    return False

                dnskey = self._get_dnskey(name)
                dns.dnssec.validate(rrset, rrsig, {name: dnskey})

            self._logger.info("DNSSEC validation successful")
            return True

        except Exception as e:
            self._logger.warn(f"DNSSEC validation failed: {e}")
            return False

    def _get_dnskey(self, name: dns.name.Name):
        answer = dns.resolver.resolve(name, 'DNSKEY')
        return answer
