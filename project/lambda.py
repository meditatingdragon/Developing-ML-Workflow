""" 
serializing image data
"""
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

"""
image prediction function
"""

import json
import sagemaker
import base64
from sagemaker.serializers import IdentitySerializer
from sagemaker.predictor import Predictor


# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2025-01-05-03-57-27-667"

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])

    # Instantiate a Predictor
    predictor = Predictor(ENDPOINT)

    # For this model the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")
        
    # Make a prediction:
    inferences = predictor.predict(image)

    # We return the data back to the Step Function    
    event["inferences"] = inferences.decode('utf-8')

    return {
        'statusCode': 200,
        'inferences': inferences.decode('utf-8')
    }

"""
inference threshold function
"""

import json

THRESHOLD = .90

def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = json.loads(event['inferences'])

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(float(val) > THRESHOLD for val in inferences)

    statusCode = 200
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        statusCode = 500

    return {
        'status': statusCode,
        'meets_threshold': meets_threshold,
        'body': json.dumps(event)
    }