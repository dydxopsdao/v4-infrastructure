import json
import logging

import cryptography

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def run(event, context):
    # Get the length and width parameters from the event object. The
    # runtime converts the event object to a Python dictionary
    # length = event["length"]
    # width = event["width"]

    # area = calculate_area(length, width)
    # print(f"The area is {area}")

    # logger.info(f"CloudWatch logs group: {context.log_group_name}")

    # return the calculated area as a JSON string
    data = {"cryptography_version": cryptography.__version__}
    return json.dumps(data)


def calculate_area(length, width):
    return length * width
