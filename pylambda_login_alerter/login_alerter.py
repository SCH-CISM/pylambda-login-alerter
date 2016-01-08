#!/bin/env python

import logging
log = logging.getLogger()
log.setLevel(logging.WARN)

# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# log.addHandler(ch)

import boto3
import json
import zlib
import base64
import datetime

logging.captureWarnings(True)

mytopic_arn = "arn:aws:sns:us-west-2:935796593605:SlackNotifications"


def lambda_handler(event, context):
    log.info("Received event: {}".format(event))
    log.info("Event: {}".format(json.dumps(event)))

    client = boto3.client('sns')

    context_json = context.__dict__
    context_json['remaining_time'] = context.get_remaining_time_in_millis()
    if 'identity' in context_json.keys():
        context_json.pop('identity')
    log.info("Context: {}".format(json.dumps(context_json)))

    binary_data = base64.b64decode(event['awslogs']['data'])
    decompressed_msg = zlib.decompress(binary_data, zlib.MAX_WBITS | 32)
    decompressed_msg = json.loads(decompressed_msg)
    log.info("Decompressed message: {}".format(decompressed_msg))

    instance = decompressed_msg['logStream']
    log.info("Instance: {}".format(instance))

    for message in decompressed_msg['logEvents']:
        log.debug("Timestamp: {}".format(message['timestamp']))
        timestamp = datetime.datetime.utcfromtimestamp(int(message['timestamp'])/1000).strftime('%Y-%m-%d %H:%M:%S')
        if 'extractedFields' not in message.keys():
            log.warn("No extracted fields found")
            continue
        if message['extractedFields']['accepted'] != "Accepted":
            log.warn("No Accept mesage found")
            continue
        fields = message['extractedFields']
        log.info("Fields: {}".format(json.dumps(fields)))
        sns_msg = "SSH Login by {} via {} detected on {} at {}".format(fields['9'], fields['11'], instance, timestamp)
        sns_sbj = "AWS SSH Monitor"
        # do sns post
        res = client.publish(
            TopicArn=mytopic_arn,
            Message=sns_msg,
            Subject=sns_sbj)

    return {'sns_results': res}
