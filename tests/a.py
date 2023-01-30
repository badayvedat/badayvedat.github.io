import time
import logging

logging.basicConfig(filename='output.log', level=logging.INFO)

for i in range(100 * 1000):
    time.sleep(0.1)
    logging.info(f"log a: {i}")