import boto3
import io
import pandas as pd

session =boto3.Session('s3')
s3 = boto3.client('s3')

def read_from_s3(file_key, s3_client=s3, bucket='fs-personal-expenses'):
    csv_obj = s3_client.get_object(Bucket=bucket, Key=file_key)
    body = csv_obj['Body']
    csv_string = body.read().decode('utf-8')

    df = pd.read_csv(io.StringIO(csv_string))
    df.loc[:,'Fecha'] = pd.to_datetime(df.Fecha.str.strip(),format='%Y-%m-%d')
    return df

def write_to_s3(df_to_upload,bucket,file_key):
    csv_buffer = io.StringIO()
    df_to_upload.to_csv(csv_buffer, index=False)

    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket, file_key).put(Body=csv_buffer.getvalue())