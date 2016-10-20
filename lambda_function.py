import boto3
import lambsnappy
import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create connection to EC2
ec2 = boto3.resource('ec2')

# Get account ID
account_id = boto3.client('sts').get_caller_identity().get('Account')
logger.info('Working with account {}'.format(account_id))


def lambda_handler(event, context):
    lambsnappy.perform_snap_operation(account_id)
    lambsnappy.perform_clean_operation(account_id, event['agelimit'])

if __name__ == '__main__':
    # For local testing
    event = {'agelimit': 30}
    context = {}
    lambda_handler(event, context)
