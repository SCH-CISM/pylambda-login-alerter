# pylambda-login-alerter
A python function for AWS Lambda to receive CloudWatch Logs streams and alert via SNS when a succesfull SSH login is detected.

## Background

Direct SSH logins to instances is highly discouraged. To monitor this use in near real time, CloudWatch Logs 
receives key system logs from all instances. Creating a subscription to this Lambda function will send a 
SNS message for every succesfull SSH login. From SNS, these alerts can be forwarded to Slack, PagerDuty, Email, etc.

Sample filter for `/var/log/secure`: `[month, day, time, host, daemon=sshd*, accepted=Accepted,  ...]`

# References and Credits

This is loosely based upon the very useful patterns demonstrated at 
https://github.com/elelsee/pycfn-custom-resource and https://github.com/elelsee/pycfn-elasticsearch.
