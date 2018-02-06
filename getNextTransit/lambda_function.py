"""
This file defines the lambda handler, which builds responses based
on various intents.
"""

from getNextTransit import intents
import os


def on_launch():
    """Called when the user launches the skill without specifying what they want"""
    return intents.welcome()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "HelloWorldIntent":
        return intents.hello_world(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return intents.welcome()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return intents.end_session()
    else:
        raise ValueError("Invalid intent")


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """

    # This prevents someone else from configuring a skill to send requests to this function.
    if event['session']['application']['applicationId'] != os.environ.get("SKILL_ID"):
        raise ValueError("Invalid Application ID")

    if event['request']['type'] == "LaunchRequest":
        return on_launch()
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
