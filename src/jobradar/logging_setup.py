import logging
import sys

def setup(level:str='INFO')->None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)-8s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )