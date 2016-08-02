# KIMSUFI MONITOR LAMBDA

This lambda function is used to monitor the OVH server availability API for
a list of servers and send a notification through a slack web hook if one or
more servers are available.

## Configuration file

```json
{
  "servers": {
    "160sk1": "Kimsufi KS-1 (HDD 500Gb)",
    "160sk2": "Kimsufi KS-2 (HDD 1Tb)",
    "160sk21": "Kimsufi KS-2 (SSD 40Gb)",
    "160sk22": "Kimsufi KS-2 (SSD 80Gb)"
  },
  "slack": {
    "bot_url": "<YOUR SLACK HOOK HERE>",
    "bot_name": "OVH Servers",
    "bot_message_tpl": "{server} is available!"
  }
}
```

Before packaging your function you need to create a `config.json` file to store:
* what servers are you interested in
* the webhook url for your slack bot. See the [slack documentation][slack-docs]
  for more information about webhooks and slack.

You can copy [config-sample.json][config-sample] and use it as a starting point
for your own configuration file.

## Packaging

It's easy. Just run:

```sh
make
```

This will download all the dependencies and generate a `kimsufi-monitor.zip`
file you can use in your lambda function.

## Deploying

There are at least a couple of ways to deploy an AWS lambda function, but for
this kind of small upload-once-and-forget-about-it functions I like the CLI
more. Obliviously the following commands assume you already installed and
configured `aws-cli` on your current host (see the
[documentation][aws-cli-docs] if it is not) and you have some familiarity with
AWS terminology.

Let's then create our new function!

```sh
aws lambda create-function \
  --function-name KimsufiMonitor \
  --runtime python2.7 \
  --memory 128 \
  --timeout 10 \
  --handler main.handle_lambda \
  --role "<your lambda execution role ARN>" \
  --zip-file fileb://./kimsufi-monitor.zip \
  --description "Kimsufi Monitor" --output json
```

This should return to you something like (depending in what version you are
downloading from this repository):

```json
{
    "Description": "Kimsufi Monitor",
    "Runtime": "python2.7",
    "CodeSize": 950867,
    "FunctionName": "KimsufiMonitor",
    "CodeSha256": "b/gcaDsaL5ly13pMRs301IG8BMdWGTUBcHfbwC/tsiQ=",
    "Handler": "main.handle_lambda",
    "Timeout": 10,
    "Role": "arn:aws:iam::0000000:role/lambda_kimsufi_monitor",
    "FunctionArn": "arn:aws:lambda:us-east-1:0000000:function:KimsufiMonitor",
    "LastModified": "2016-08-02T21:25:23.417+0000",
    "MemorySize": 128,
    "Version": "$LATEST"
}
```

This is unfortunately not enough. We have a lambda function yes, but can only
execute it manually right now, and instead we want to schedule it. To do that,
we need to leverage CloudWatch events, like below.

```sh
aws events put-rule \
  --name "1HourRule" \
  --schedule-expression "rate(1 hour)" --output json
aws events put-targets \
  --rule "1HourRule"
  --targets "Id=km,Arn=arn:aws:lambda:us-east-1:0000000:function:KimsufiMonitor"
```

For the second command, in the `targets` parameter, the `Arn` to use is the
`FunctionArn` we got when creating the lambda function, while the `Id` is
simply a unique string.

And we are all set!

Enjoy your notifications, I guess.

[slack-docs]: https://api.slack.com/incoming-webhooks
[config-sample]: ../config-sample.json
[aws-cli-docs]: http://docs.aws.amazon.com/cli/latest/userguide/installing.html
