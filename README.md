# lambsnappy
A Lambda function written in Python that will automatically take snapshots of your EC2 instances tagged for backup

## How it works
You will tag the instances that you want to take snapshots of. The function will look for any instances containing the tag and take a snapshot of its attached volumes. After that, it will look for any old snapshots past the age limit and delete them. You will specify for how many days to keep the snapshots.

## Setting it up
First of all, you will need to create an IAM role with the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": "ec2:Describe*",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateSnapshot",
                "ec2:ModifySnapshotAttribute",
                "ec2:ResetSnapshotAttribute",
                "ec2:CreateTags"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```
Then zip the files, create the lambda function and upload them. It should look something like this:
![Lambda function configuration](https://cc-public-docs.s3.amazonaws.com/lambda-function.png "Lambda function configuration")

Create a Cloudwatch Event to fire off the job, I run mine every night at 3am: `0 3 * * ? *`
![CloudWatch Event rules](https://cc-public-docs.s3.amazonaws.com/cloudwatch-event-rules.png "CloudWatch Event rules")

Please note that you need to specify how long it should keep the snapshots, example if you want to keep them for 30 days.
```json
{"agelimit": 30}
```
Now tag the instances that you want to backup with the following tag `BackupEnable = True`
