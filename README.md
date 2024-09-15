# Watcher
Finding secrets in CloudWatch logs.

## Technical Information

### Logs

By default, Watcher will search the logs generated in the last hour, as can be read in the script file:

```
time_source = int((datetime.utcnow() - timedelta(hours=1)).timestamp() * 1000)
```

To search within more hours, modify the `1` number with the desired hours.

### AWS Keys

`boto3` will grab the AWS keys from:
- Environment variables
- `~/.aws/credentials` file

### IAM Permissions

The script will make use of the CloudWatch (`cloudwatch:*`) IAM permissions, just for reading.

>**Masked data**: Some values may be masked. In order to see them, the IAM permission `logs:Unmask` is needed.

* * *

Example output:

```
$ python3 watcher.py

 _       __        __         __               
| |     / /____ _ / /_ _____ / /_   ___   _____
| | /| / // __ `// __// ___// __ \ / _ \ / ___/
| |/ |/ // /_/ // /_ / /__ / / / //  __// /    
|__/|__/ \__,_/ \__/ \___//_/ /_/ \___//_/     
                                               

[✓] AWS Credentials: Valid
[✓] CloudWatch Permissions: OK

[✓] Logs found:

+------------+-------------+------------------------------------------------------------------+
| Region     | Log Group   | Log Stream                                                       |
+============+=============+==================================================================+
| eu-north-1 | aws         | information                                                      |
+------------+-------------+------------------------------------------------------------------+
| eu-north-1 | test        | http                                                             |
+------------+-------------+------------------------------------------------------------------+
| eu-north-1 | test        | test_stream                                                      |
+------------+-------------+------------------------------------------------------------------+
| us-east-1  | safe        | log_stream_created_by_aws_to_validate_log_delivery_subscriptions |
+------------+-------------+------------------------------------------------------------------+
| us-east-1  | safe        | no issues                                                        |
+------------+-------------+------------------------------------------------------------------+
| us-east-1  | usa_client  | usa client important                                             |
+------------+-------------+------------------------------------------------------------------+

[✓] Searching logs from 2024-09-14 11:31:32 to 2024-09-15 11:31:32

Potential secret found in aws/information (Region: eu-north-1):
  - Rule Name: Secret Key
  - Description: AWS - Secret Access Key
  - Matched Secret: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

Potential secret found in aws/information (Region: eu-north-1):
  - Rule Name: AKID
  - Description: AWS - Access Key ID
  - Matched Secret: AKIAIOSFODNN7EXAMPLE

Potential secret found in test/http (Region: eu-north-1):
  - Rule Name: JWT
  - Description: JSON Web Token (JWT)
  - Matched Secret: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

Potential secret found in test/http (Region: eu-north-1):
  - Rule Name: Mail Address
  - Description: Mail Address
  - Matched Secret: security@test.com

Potential secret found in usa_client/usa client important (Region: us-east-1):
  - Rule Name: American Express Credit Card
  - Description: American Express Credit Card
  - Matched Secret: 378734493671000

Potential secret found in usa_client/usa client important (Region: us-east-1):
  - Rule Name: MasterCard Credit Card
  - Description: MasterCard Credit Card
  - Matched Secret: 5555555555554444
```
