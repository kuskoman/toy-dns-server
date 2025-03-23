import signal
from toy_dns_server.bootstraper import Bootstraper
from toy_dns_server.log.logger import Logger

logger = Logger("main")

def handle_sigint(bootstraper: Bootstraper):
    bootstraper.stop()
    exit(0)

def main():
    bootstraper = Bootstraper()
    bootstraper.run()

    signal.signal(signal.SIGINT, lambda signum, frame: handle_sigint(bootstraper))


if __name__ == "__main__":
    main()
