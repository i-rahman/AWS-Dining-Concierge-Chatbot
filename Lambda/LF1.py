import json
import boto3
import re

def lambda_handler(event, context):
    
    source = event['invocationSource']
    slots = event['currentIntent']['slots']
    intent = event['currentIntent']['name']
    
    delresponse =  {
            "dialogAction": {
                "type": "Delegate",
                "slots": slots,
            }
        }
        
    locationresponse = {
            "dialogAction": {
                "type": "ElicitSlot",
                "message": {
                    "contentType": "PlainText",
                    "content": "I am only able to suggest restaurants in New York City (Brooklyn, Queens and Manhattan)."
                },
                "intentName": intent,
                "slots": slots,
                "slotToElicit" : "location"
            }
        }
        
    cuisineresponse = {
            "dialogAction": {
                "type": "ElicitSlot",
                "message": {
                    "contentType": "PlainText",
                    "content": "Please choose from Chinese, Japanese, Mexican, Indian, Thai and Korean cuisines"
                },
                "intentName": intent,
                "slots": slots,
                "slotToElicit" : "cuisine"
            }
        }
    peopleresponse = {
            "dialogAction": {
                "type": "ElicitSlot",
                "message": {
                    "contentType": "PlainText",
                    "content": "Please choose between 1 and 20 people"
                },
                "intentName": intent,
                "slots": slots,
                "slotToElicit" : "people"
            }
        }
        
    numberresponse = {
            "dialogAction": {
                "type": "ElicitSlot",
                "message": {
                    "contentType": "PlainText",
                    "content": "Please enter a valid 10 digits phone number"
                },
                "intentName": intent,
                "slots": slots,
                "slotToElicit" : "number"
            }
        }

    successresponse = {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "You will receive our restaurant suggestions on your phone shortly!"
                }
            }
        }
    
    if source == 'DialogCodeHook':
        
        if slots['location'] is None:
            return delresponse
        
        if slots['location'] and not valdate_location(slots['location']):
            return locationresponse
        
        if slots['cuisine'] is None:
            return delresponse
            
        if slots['cuisine'] and not validate_cuisine(slots['cuisine']):
            return cuisineresponse
        

        if slots['people'] is None:
            return delresponse
        
        if slots['people'] and not validate_party_size(slots['people']):
            return peopleresponse
        
        if slots['time'] is None:
            return delresponse
            
        if slots['number'] is None:
            return delresponse
        
        if slots['number'] and not validate_phone_nubmer(slots['number']):
            return numberresponse

     
    if source == 'FulfillmentCodeHook':
        
        sqs = boto3.client('sqs')
        queue_url = sqs.get_queue_url(QueueName='hw1_dining')['QueueUrl']
        sqs.send_message(QueueUrl=queue_url,DelaySeconds=10,MessageBody=(json.dumps(slots)))
        return successresponse
    
    return delresponse

def validate_cuisine(cuisine):
    cuisines = ["chinese", "indian", "japanese", "mexican", "thai", "korean"]
    if cuisine.lower() in cuisines:
        return True
    return False

def validate_party_size(size):
    if int(size) < 1 or int(size) > 20:
        return False
    return True    

def validate_phone_nubmer(phone_number):
    pattern = re.compile("^(?:\+?1[-. ]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$")
    if pattern.match(phone_number) is not None:
        formatted_number=re.sub('[^0-9]+', '', phone_number)
        if len(formatted_number) == 10 or (len(formatted_number) > 10 and len(formatted_number) < 12 and formatted_number[0] == "1"):
            return True
    return False

def valdate_location(location):
    locations = ["nyc", "brooklyn", "new york city", "new york", "queens"]
    if location.lower() not in locations:
        return False
    return True