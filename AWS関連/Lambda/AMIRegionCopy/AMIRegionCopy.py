import boto3

def lambda_handler(event, context):
    # ソースとなるAMIのIDを指定します
    source_ami_id = 'source_ami_id'

    # コピー先のリージョンを指定します
    destination_region = 'destination_region'

    # boto3を使用して、ソースリージョンのEC2クライアントを作成します
    source_ec2_client = boto3.client('ec2')

    # ソースAMIの情報を取得します
    source_ami = source_ec2_client.describe_images(ImageIds=[source_ami_id])['Images'][0]

    # ソースAMIのスナップショットIDを取得します
    source_snapshot_id = source_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId']

    # ソースAMIのタグ情報を取得します
    source_ami_tags = source_ami.get('Tags', [])

    # boto3を使用して、コピー先リージョンのEC2クライアントを作成します
    destination_ec2_client = boto3.client('ec2', region_name=destination_region)

    # ソーススナップショットをコピーします
    response = destination_ec2_client.copy_snapshot(
        SourceRegion=source_ec2_client.meta.region_name,
        SourceSnapshotId=source_snapshot_id
    )

    # コピーしたスナップショットのIDを取得します
    destination_snapshot_id = response['SnapshotId']

    # タグ情報をコピーしたスナップショットに設定します
    destination_ec2_client.create_tags(
        Resources=[destination_snapshot_id],
        Tags=source_ami_tags
    )

    # コピーしたスナップショットを使用してAMIを作成します
    response = destination_ec2_client.register_image(
        Name=source_ami['Name'],
        Architecture=source_ami['Architecture'],
        BlockDeviceMappings=source_ami['BlockDeviceMappings'],
        Description=source_ami.get('Description', ''),
        RootDeviceName=source_ami['RootDeviceName'],
        VirtualizationType=source_ami['VirtualizationType'],
        EnaSupport=source_ami['EnaSupport'],
        SriovNetSupport=source_ami.get('SriovNetSupport', ''),
        SnapshotId=destination_snapshot_id
    )

    # 作成したAMIのIDを取得します
    destination_ami_id = response['ImageId']

    # コピーが完了した旨をログに出力します
    print(f'AMI {source_ami_id} を {destination_region} リージョンにコピーしました。AMI ID: {destination_ami_id}')
