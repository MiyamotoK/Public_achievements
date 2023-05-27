#===============================================================================================
#Description
#
#instance_idに再起動するEC2インスタンスのIDを指定してください。
#Lambda関数をデプロイし、トリガーを設定すると、
#指定したEC2インスタンスのステータスが監視され、ステータスが"running"以外の場合に再起動が行われます。
#再起動が実行されると、ログに再起動のメッセージが表示されます。
#
#===============================================================================================
import boto3

def lambda_handler(event, context):
    # 監視するEC2インスタンスのIDを指定します
    instance_id = 'instance_id'

    # EC2クライアントを作成します
    ec2_client = boto3.client('ec2')

    # 監視対象のEC2インスタンスのステータスを取得します
    response = ec2_client.describe_instance_status(InstanceIds=[instance_id])

    # EC2インスタンスのステータスが存在する場合、再起動します
    if 'InstanceStatuses' in response:
        status = response['InstanceStatuses'][0]['InstanceState']['Name']
        if status != 'running':
            # EC2インスタンスを再起動します
            ec2_client.reboot_instances(InstanceIds=[instance_id])
            print(f'EC2インスタンス {instance_id} を再起動しました。')
    else:
        print(f'EC2インスタンス {instance_id} のステータス情報が取得できませんでした。')
