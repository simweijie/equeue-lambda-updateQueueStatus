import sys
import logging
import pymysql
import json
import os
import boto3

#rds settings
rds_endpoint = os.environ['rds_endpoint']
username=os.environ['username']
password=os.environ['password']
db_name=os.environ['db_name']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SNS client for Singapore Region
session = boto3.Session(
    region_name="us-east-1"
)
sns_client = session.client('sns')

#Connection
try:
    connection = pymysql.connect(host=rds_endpoint, user=username,
        passwd=password, db=db_name)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()
logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

def handler(event, context):
    cur = connection.cursor()  
## Update queue status    
    query = "UPDATE Queue SET status='{}' where branchId='{}' and customerId='{}' and status='{}'".format(event['newStatus'],event['branchId'],event['customerId'],event['currentStatus'])
    cur.execute(query)
    connection.commit()
    print(cur.rowcount, "record(s) update statements affected")

## Retrieve contact details of customer next to see doctor
    if event['newStatus']=='D':
        print('lol')
        query="SELECT c.name,c.contactNo,q.queueNumber \
            FROM Customer c, Queue q \
            WHERE q.branchId='{}' AND q.status='Q' AND c.id=q.customerId \
            ORDER BY queueNumber ASC LIMIT 1".format(event['branchId'])
        cur.execute(query)
        connection.commit()
        print(cur.rowcount, "record(s) select statements affected")
        rows = cur.fetchall()
        contactNo= ""
        name=""
        for row in rows:
            print("TEST {0} {1} {2}".format(row[0],row[1],row[2]))
            name = row[0]
            contactNo = row[1]

## Prepare and send SMS
        ## https://blog.shikisoft.com/send-sms-with-sns-aws-lambda-python/
        print(contactNo)
        response = sns_client.publish(
            PhoneNumber='+65' + contactNo,
            Message='Hi ' + name + 
            ', please note that you are next in line to see the doctor.',
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'eQueue'
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Promotional'
                }
            }
        )

## Construct body of the response object
    transactionResponse = {}
# Construct http response object
    responseObject = {}
    responseObject['data'] = json.dumps(transactionResponse, sort_keys=True,default=str)

    return responseObject