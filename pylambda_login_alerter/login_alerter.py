#!/bin/env python

import logging
log = logging.getLogger()
log.setLevel(logging.INFO)

import boto3
import json
import zlib
import base64
import datetime

logging.captureWarnings(True)

mytopic_arn = "ARN_OF_YOUR_SNS_TOPIC"


def fetch_tags(instance_id):
    """Return an array of tags for a given instance id."""
    log.info("Fetching tags for instance: {}".format(instance_id))
    client = boto3.client('ec2')

    tags = client.describe_tags(
        Filters=[{
            'Name': 'resource-id',
            'Values': [instance_id]
        }]
    )
    log.info("Tag return call is: {}".format(json.dumps(tags)))

    clean_tags = {}
    for tag in tags['Tags']:
        if 'Key' in tag:
            log.info("This tag is {} - {}".format(tag['Key'], tag['Value']))
            clean_tags[tag['Key']] = tag['Value']

    return clean_tags


def lambda_handler(event, context):
    """Primary event handler when running on Lambda."""
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

    tags = fetch_tags(instance)
    project = tags.get('project', 'unknown')

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
        sns_msg = "SSH Login by {} via {} detected on {} (project {}) at {}".format(fields['9'], fields['11'], instance, project, timestamp)
        sns_sbj = "AWS SSH Monitor"
        # do sns post
        res = client.publish(
            TopicArn=mytopic_arn,
            Message=sns_msg,
            Subject=sns_sbj)

    return {'sns_results': res}

if __name__ == "__main__":
    """Default action for interactive runs."""
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)

    tags = fetch_tags('i-65d944bg')
    log.info("Returned tags are {}".format(tags))
    print("This host has is in the {} project".format(tags.get('project', 'unknown')))
