import paramiko
import boto3
import json

def handler(event, context):
    controllersIp = []
    client = boto3.client("ec2",
        config=my_config
        )
    autoscaling  = boto3.client('autoscaling',
        config=my_config
        )
    s3 = boto3.resource('s3')
    controllers = client.describe_instances(Filters=[
    {'Name': 'tag:Type', 'Values': ['Controller']},
    {'Name': 'instance-state-name', 'Values': ['running']}
    ])
    print("----------------event----------------")
    print(event)
    for reservation in controllers["Reservations"]:
        for instance in reservation["Instances"]:
            controllersIp.append(instance["PublicIpAddress"])
    controllerIp=controllersIp[0]
    message =json.loads(event['Records'][0]['Sns']['Message'])
    instanceId = message['EC2InstanceId']
    autoScalingGroupName = message['AutoScalingGroupName']
    lifecycleHookName = message['LifecycleHookName']
    lifecycleActionToken = message['LifecycleActionToken']
    print("----------------message----------------")
    print(message)
    cmd = 'echo `date` >> /home/ubuntu/my-date && ' + 'echo "'+str(instanceId)+'" >> /home/ubuntu/message'
    s3.meta.client.download_file('kube-cluster-lambda-bucket', 'AWS-keypair.pem', '/tmp/AWS-keypair.pem')
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    k = paramiko.RSAKey.from_private_key_file("/tmp/AWS-keypair.pem")
    ssh_client.connect(hostname=controllerIp, username="ubuntu", pkey=k)
    stdin,stdout,stderr=ssh_client.exec_command(cmd)
    lines = stdout.readlines()
    ssh_client.close()
    finish = autoscaling.complete_lifecycle_action(
    AutoScalingGroupName=autoScalingGroupName,
    LifecycleActionResult='CONTINUE',
    LifecycleActionToken=lifecycleActionToken,
    LifecycleHookName=lifecycleHookName,
    )

