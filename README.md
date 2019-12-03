# A lambda function to monitor AWS DocumentDB cursors

This [AWS Lambda-backed CloudFormation Custom Resource] can be used to monitor cursors in every instance of all DocumentDB clusters within a VPC. 

The lambda function is scheduled using a CloudWatch rule. Everytime the function is triggered it queries all clusters current cursor usage and compares it to the a warning and a critical threshold, if the usage is above the threshold it raises an alert to an SNS topic. 

Thresholds are environment variables as well as DocumentDB connection parameters. 

# How to install
1. Clone the xyz folder to your local machine. You can change the "lambda_function.py" if required. 
2. Create a zip file containing folder files. Name it "lambda_function.zip"
3. Upload that zip file to an AWS S3 bucket.
4. Configure the scheduler rule as desired. 
5. Run the CloudFormation template "deploy_docdb_monitor.yaml".
    1. You will need to fill in the parameter for S3 bucket name.
    2. You will need to fill in the parameter for S3 key that you stored the zip as.
6. Once CloudFormation finishes you can use the lambda function from within your CloudFormation templates.
