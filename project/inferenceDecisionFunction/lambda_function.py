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