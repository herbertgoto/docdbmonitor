import pymongo
import os
import json
import boto3
import botocore

from base64 import b64decode

# variable envs
monitor_tag = os.environ['monitor_tag']
username=os.environ['username']
ENCRYPTED = os.environ['password']
password=boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED))['Plaintext']
document_db_port=os.environ['db_port']
cursors_limit=os.environ['cursors_limit']
warning_threshold=os.environ['warning_threshold']
critical_threshold=os.environ['critical_threshold']
sns_topic_arn=os.environ['sns_topic_arn']

##Create docdb boto3 client
clientDocDB = boto3.client('docdb')
##Create lambda boto3 client
clientLambda = boto3.client('lambda')
##Create SNS boto3 client
clientSns = boto3.client('sns')
##Create S3 boto3 client
clientS3 = boto3.resource('s3')

# Main function - compares cursors limits to thresholds and sends alert
def lambda_handler(event, context):
    try:

        getDocDbCertificate()

        responseLambda = clientLambda.get_function(FunctionName=context.function_name)
        vpcId = responseLambda['Configuration']['VpcConfig']['VpcId']

        resp = 'Monitored!'

        r = getInstances(monitor_tag)
        if(len(r) > 0):
            e = getEndpoints(r,vpcId)
            if(len(e) > 0):
                c = getCursors(e,r)
                
                for i in c:
                    usedCursors = float(c[i]['open']['total'])
                    limit = float(cursors_limit)
                    usedCursorsPercentage = float(1-(limit - usedCursors)/limit)
                    if usedCursorsPercentage >= float(critical_threshold):
                        sendAlert(json.dumps({"Alert": "Critical", "docdbInstance": i, "usedPercentage": (usedCursors*100) , "usedCursors" : usedCursors, "totalCursors": cursors_limit}))
                    elif usedCursorsPercentage >= float(warning_threshold):
                        sendAlert(json.dumps({"Alert": "Critical", "docdbInstance": i, "usedPercentage": (usedCursors*100) , "usedCursors" : usedCursors, "totalCursors": cursors_limit}))
            
            else:
                resp = 'No clusters to monitor!'
        else:
            resp = 'No clusters to monitor!'

        return {
            'statusCode': 200,
            'body': json.dumps(resp)
        }

    except Exception as ex:
        print('Error in handler')
        print(str(ex))

#Function to get instances to monitor
def getInstances(tagValue):
    try:
        response = clientDocDB.describe_db_clusters()
        instances = []

        for i in response["DBClusters"]:
            tags = clientDocDB.list_tags_for_resource(ResourceName=i["DBClusterArn"])
            if len(tags["TagList"]) > 0:
                for j in tags["TagList"]:
                    if j["Value"] == tagValue:                                                          
                        for k in i["DBClusterMembers"]:
                            instances.append(k["DBInstanceIdentifier"])
        
        return instances

    except Exception as ex:
        print('Error in instances')
        print(str(ex))

#Function to get endpoints to monitor
def getEndpoints(instances,vpcId):
    try:
        
        endpoints = []

        for i in instances:
            response = clientDocDB.describe_db_instances(DBInstanceIdentifier=i)
            if response["DBInstances"][0]['DBSubnetGroup']['VpcId'] == vpcId:
                endpoints.append(response["DBInstances"][0]["Endpoint"]["Address"])
        
        return endpoints 

    except Exception as ex:
        print('Error in endpoints')
        print(str(ex))

#Function to get cursors for each endpoint
def getCursors(endpoints, instances):
    try:
        
        n = 0
        cursors = {}

        for i in endpoints:
            ##Create a MongoDB client, open a connection to Amazon DocumentDB with TLS
            db_client = pymongo.MongoClient('mongodb://'+username+':'+str(password,'utf-8')+'@'+i+':'+document_db_port+'/?ssl=true&ssl_ca_certs=/tmp/rds-combined-ca-bundle.pem')
            ##Create a MongoDB client, open a connection to Amazon DocumentDB without TLS
            #db_client = pymongo.MongoClient('mongodb://'+username+':'+str(password,'utf-8')+'@'+i+':'+document_db_port)
            #aws docdb describe-db-cluster-parameters --db-cluster-parameter-group-name=default.docdb3.6
            ##Specify the database to be used
            db = db_client.test
            print(db)
            ## Runs serverStatus Command to get cursors
            x = db.command("serverStatus")
            cursors.update({instances[n]:x["metrics"]["cursor"]})
            n += 1

        return cursors

    except Exception as ex:
        print('Error in cursors')
        print(str(ex))
    finally:
        ##Close the connection
        db_client.close()

#Function to send an SNS alert
def sendAlert(message):
    try:
        response = clientSns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject='Document DB Alarm',
            MessageStructure='default'
        )
    except Exception as ex:
        print('Error in send alert')
        print(str(ex))

#Function to download the current docdb certificate
def getDocDbCertificate():
    try:
        clientS3.Bucket('rds-downloads').download_file('rds-combined-ca-bundle.pem', '/tmp/rds-combined-ca-bundle.pem')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise