# A lambda function to monitor AWS DocumentDB cursors

This template can be used to deploy a lambda to monitor cursors in every instance of all DocumentDB clusters within a VPC. 

The lambda function is scheduled using a CloudWatch rule. Everytime the function is triggered it queries all clusters current cursor usage and compares it against warning and critical threshold, if the usage is above any of the thresholds it raises an alert to an SNS topic. 

Thresholds are environment variables as well as DocumentDB connection parameters. 

Since documentDB are private resources that run in one VPC, there should be as many lambdas as vpcs with clusters to be monitored. Lambdas run within VPC therefore it is necessary that it runs in at least one private subnet that can reach internet using a NAT gateway. 

Lambda uses documentDB credentials and password is encrypted using KMS. The documentDB user needs to have access to the default test database and to run the serverStatus command.   

# How to install
1. Create a python virtualenv and move files in app folder to it. Install dependencies and zip it (Python runtime used is 3.7.4)
2. Create a second python virtualenv and move files at https://github.com/herbertgoto/lambda-envvar-encrypter/tree/master/app to it. Install dependencies and zip it (Python runtime used is 3.7.4)
3. Upload both zip files to an AWS S3 bucket.
4. Run the CloudFormation template "documentdb_monitor.yaml".
    1. You will need to fill in the parameter for S3 bucket name.
    2. You will need to fill in the parameter for S3 key for both zip files.
    3. You will need to fill in the parameter for the subnets where the lambda will run.
    4. You will need to fill in the parameter for the security groups where the lambda will run.
    5. You will need to fill in the parameter for the documentDB credentials. 
    6. You will need to fill in the parameter for the monitoring thresholds. 
    7. You will need to fill in the parameter for the tag that will identify the clusters to monitor. Lambda just checks if the value is part of a tag.   
5. Cloudwatch rule is schedule to run every hour and is disabled by design, modify according to your needs and enable it. 

This deployment supports clusters with TLS enabled and disabled. 

Tag your cluster to be considered in the monitoring. Lambda will check if the value enter as parameter is the same as the value in the tag; if it does not macht the cluster will not be considered. 

If you alread have the KMS CMK, you can comment the KMS Resource and instead enable it as a CFN parameter (uncomment this part in the CFN). Review the policies and the custom resource that make use of the KMS CMK and make the changes to use the parameter instead. 