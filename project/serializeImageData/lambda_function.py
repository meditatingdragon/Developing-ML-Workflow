import json
import boto3
import base64

def download_data(s3_input_uri):
    s3 = boto3.client('s3')
    input_bucket = s3_input_uri.split('/')[0]
    input_object = '/'.join(s3_input_uri.split('/')[1:])
    file_name = '/tmp/image.png'
    s3.download_file(input_bucket, input_object, file_name)
    return file_name

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event["key"]
    bucket = event["bucket"]

    # Download the data from s3 to /tmp/image.png
    filename = download_data(bucket+"/"+key)

    # We read the data from a file
    with open(filename, "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }