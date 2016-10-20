import boto3
from datetime import datetime
from datetime import timedelta
import pytz
import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create connection to EC2
ec2 = boto3.resource('ec2')


def perform_snap_operation(owner_id):
    def snap_volume(volume_id):
        # Take snapshot of given volume
        logger.info('Snapping volume: {}'.format(volume_id))
        snapshot = ec2.create_snapshot(
            VolumeId=volume_id,
            Description='Snapshot of {} at {}'.format(volume_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        # Tag snapshot as managed
        ec2.create_tags(
            Resources=[snapshot.snapshot_id],
            Tags=[
                {
                    'Key': 'ManagedBackup',
                    'Value': 'True'
                },
            ]
        )
        return snapshot

    # List instances tagged for backup
    logger.info('Looking for instances tagged for backup')
    instances = ec2.instances.filter(
        Filters=[
            {
                'Name': 'tag:BackupEnable',
                'Values': ['True']
            },
            {
                'Name':'owner-id',
                'Values': [owner_id]
            }
        ]
    )

    # Iterate through instances and take snapshot
    for instance in instances:
        logger.info('Found instance for backup: {}'.format(instance.instance_id))
        # Iterate through volumes attached to instance
        for volume in instance.block_device_mappings:
            # Call the snapshot function
            snap_volume(volume['Ebs']['VolumeId'])


def perform_clean_operation(owner_id, agelimit):
    # Get snapshots tagged as managed
    logger.info('Looking for managed snapshots')
    snapshots = ec2.snapshots.filter(
        Filters=[
            {
                'Name': 'tag:ManagedBackup',
                'Values': ['True']
            }
        ],
        OwnerIds=[
            owner_id,
        ],
    )
    # Iterate through snapshots and delete old ones
    for snapshot in snapshots:
        if snapshot.start_time < (datetime.now(pytz.utc) - timedelta(days=agelimit)):
            logger.info('Snapshot {} is old from {} - deleting...'.format(snapshot.snapshot_id, snapshot.start_time))
            snapshot.delete()
        elif snapshot.start_time > (datetime.now(pytz.utc) - timedelta(days=agelimit)):
            logger.info('Snapshot {} is new from {} - leaving...'.format(snapshot.snapshot_id, snapshot.start_time))
        else:
            logger.info('Don\'t know about {} from {}...'.format(snapshot.snapshot_id, snapshot.start_time))
