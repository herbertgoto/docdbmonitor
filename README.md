# A lambda function to monitor AWS DocumentDB cursors

This template can be used to deploy a lambda to monitor cursors in every instance of all DocumentDB clusters within a VPC. 

The lambda function is scheduled using a CloudWatch rule. Everytime the function is triggered it queries all clusters current cursor usage and compares it to the a warning and a critical threshold, if the usage is above the threshold it raises an alert to an SNS topic. 

Thresholds are environment variables as well as DocumentDB connection parameters. 

Since documentDB are private resources that run in one VPC, there should be as many lambdas as vpcs with clusters to be monitored. Lambdas run within VPC therefore it is necessary that it runs in at least one private subnet that can reach internet using a NAT gateway. 

Lambda uses documentDB credentials and password is encrypted using KMS. The documentDB user needs to have access to the default test database and to run the serverStatus command.   

# How to install
1. Create a python virtualenv and move files in app folder to it. Install dependencies and zip it. Name it "lambda_function.zip". Python runtime used is 3.7.4. 
2. Upload that zip file to an AWS S3 bucket.
3. Run the CloudFormation template "documentdb_monitor.yaml".
    1. You will need to fill in the parameter for S3 bucket name.
    2. You will need to fill in the parameter for S3 key that you stored the zip as.
    3. You will need to fill in the parameter for the subnets where the lambda will run.
    4. You will need to fill in the parameter for the seceurity groups where the lambda will run.
    5. You will need to fill in the parameter for the documentDB credentials. 
    6. You will need to fill in the parameter for the monitoring thresholds. 
    7. You will need to fill in the parameter for the tag that will identify the clusters to monitor. 
4. Once CloudFormation finishes, you need to encrypt documentDB password using a KMS key. You can do this in the lambda console using the encryption helper.  
5. Cloudwatch rule is schedule to run every hour and is disabled by design, modify according to your needs and enable it. 