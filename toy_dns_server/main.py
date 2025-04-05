import os
import signal
from toy_dns_server.bootstraper import Bootstraper
from toy_dns_server.log.logger import Logger

logger = Logger("main")

def handle_sigint(bootstraper: Bootstraper):
    bootstraper.stop()
    logger.info("Exiting...")
    exit(0)

def main():
    logger.info("Starting...")

    main_file_path = os.path.abspath(__file__)
    main_file_dir = os.path.dirname(main_file_path)
    bootstraper = Bootstraper(main_file_dir)
    signal.signal(signal.SIGINT, lambda signum, frame: handle_sigint(bootstraper))

    bootstraper.run()



if __name__ == "__main__":
    main()
