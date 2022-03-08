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
