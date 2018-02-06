from getNextTransit import response


def hello_world(intent):
    speech_output = 'Hello World!'
    reprompt_text = 'What?'
    should_end_session = False

    return response.build_response({}, response.build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def welcome():
    card_title = 'Welcome'
    speech_output = 'Welcome to Transitly.'
    reprompt_text = 'You can ask when your next train is coming by saying, for example, ' \
                    'When is the next N coming?'
    should_end_session = False

    return response.build_response({}, response.build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def end_session():
    card_title = "Session Ended"
    speech_output = "Thank you for trying Transitly. Have a nice day!"

    # Setting this to true ends the session and exits the skill.
    should_end_session = True

    return response.build_response({}, response.build_speechlet_response(
        card_title, speech_output, None, should_end_session))
