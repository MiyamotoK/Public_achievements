#===============================================================================================
#Description
#
#指定したS3バケット内のELBアクセスログファイルをLambda関数がトリガーとして検出し、
#ログデータをCloudWatch Logsにインポートします。ログデータを処理する部分では、ログエントリを1行ずつ処理し、
#必要に応じてレイテンシーのメトリクス化などの処理を行うことができます。
#最後に、CloudWatch Logsにログイベントを書き込みます。
#
#===============================================================================================
import boto3
import gzip
import json

def lambda_handler(event, context):
    # インポートするELBのアクセスログが保存されているS3バケット名とキーを取得します
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']
    
    # インポートするログデータをダウンロードします
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    log_data = response['Body'].read()
    
    # gzip形式のログデータを展開します
    log_data = gzip.decompress(log_data)
    
    # ログエントリを1行ずつ処理してCloudWatch Logsに書き込みます
    cw_logs_client = boto3.client('logs')
    log_group_name = 'your_log_group_name'
    log_stream_name = 'your_log_stream_name'
    
    log_events = []
    
    for line in log_data.decode().splitlines():
        log_entry = json.loads(line)
        
        # レイテンシーのメトリクス化など、必要な処理を行います
        
        # ログイベントを作成し、リストに追加します
        log_events.append({
            'timestamp': log_entry['timestamp'],
            'message': line
        })
        
    # CloudWatch Logsにログイベントを書き込みます
    response = cw_logs_client.create_log_stream(
        logGroupName=log_group_name,
        logStreamName=log_stream_name
    )
    
    sequence_token = response.get('uploadSequenceToken')
    
    if sequence_token:
        response = cw_logs_client.put_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            logEvents=log_events,
            sequenceToken=sequence_token
        )
    else:
        response = cw_logs_client.put_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            logEvents=log_events
        )
    
    # レスポンスをログに出力します
    print(response)
