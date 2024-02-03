import logging

logging.basicConfig(level=logging.INFO)

# def main():
def lambda_handler(event, context):
    logging.info("No ENTRYPOINT override set")