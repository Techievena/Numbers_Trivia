# -*- coding: utf-8 -*-

import logging
import json
import requests
from datetime import datetime

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name, viewport
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand,
    SetPageCommand, HighlightMode, Position)

from typing import Dict, Any

SKILL_NAME = "Numbers Trivia"
HELP_MESSAGE = ("You can ask me questions like, \"Give me a fact about number 42\"; \"What is significance of 42 in mathematics?\"; "
                "\"What is special about 5th September?\"")
HELP_REPROMPT = ("Just ask, \"What is special about today?\"")
STOP_MESSAGE = "Goodbye! Hope you liked playing with the numbers. Please rate us in the Alexa Skills Store."

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _load_apl_document(file_path):
    # type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)

# Built-in Intent Handlers
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequest")

        speech = ('Welcome to the Numbers Trivia skill! '
                  'I can give you many interesting facts about the numbers, '
                  'their significance in the world of mathematics. '
                  'I can also tell all the great historical facts any date is known for.')

        handler_input.response_builder.speak(speech).ask(speech).add_directive(
            RenderDocumentDirective(
                document=_load_apl_document("welcome.json"),
                datasources={
                    "welcomeTemplateData": {
                        "type": "object",
                        "objectId": "bt2Sample",
                        "backgroundImage": {
                            "sources": [
                                {
                                    "url": "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_background.jpg",
                                    "size": "small",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                },
                                {
                                    "url": "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_background.jpg",
                                    "size": "large",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                }
                            ]
                        },
                        "title": "Numbers Trivia",
                        "image": {
                            "sources": [
                                {
                                    "url": "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_skill_logo.png",
                                    "size": "small",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                },
                                {
                                    "url": "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_skill_logo.png",
                                    "size": "large",
                                    "widthPixels": 0,
                                    "heightPixels": 0
                                }
                            ]
                        },
                        "textContent": {
                            "title": {
                                "type": "PlainText",
                                "text": "Hi, there."
                            },
                            "subtitle": {
                                "type": "PlainText",
                                "text": "It's great to have you here with us!"
                            },
                            "primaryText": {
                                "type": "PlainText",
                                "text": speech
                            }
                        },
                        "logoUrl": "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_skill_logo.png",
                        "hintText": "Try, \"Alexa, what is special about today?\""
                    }
                }
            )
        )


        return handler_input.response_builder.response


def date_suffix(date_val):
    return 'th' if 11<=date_val<=13 else {1:'st',2:'nd',3:'rd'}.get(date_val%10, 'th')


class DateTriviaIntentHandler(AbstractRequestHandler):
    """Handler for Date Trivia Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("DateTriviaIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In Date Trivia Intent")

        slots = handler_input.request_envelope.request.intent.slots

        if 'date_slot' in slots and slots['date_slot'].value != None:
            date_val = slots['date_slot'].value
            handler_input.attributes_manager.session_attributes['date_slot_key'] = date_val
            date_val = datetime.strptime(date_val, "%Y-%m-%d")
            fact = requests.get("http://numbersapi.com/" + str(date_val.month) + "/" + str(date_val.day) + "/date").content
            date_string = date_val.strftime("{S} %B").replace('{S}', str(date_val.day) + date_suffix(date_val.day))
            speech = "Here is something special about " + date_string
            reprompt = HELP_REPROMPT
        elif 'random_slot' in slots and slots['random_slot'].value != None:
            fact = requests.get("http://numbersapi.com/random/date").content
            date_string = "random date"
            speech = "Here is something special about a randomly generated date!"
            reprompt = HELP_REPROMPT
        elif 'date_slot_key' in handler_input.attributes_manager.session_attributes:
            date_val = handler_input.attributes_manager.session_attributes['date_slot_key']
            date_val = datetime.strptime(date_val, "%Y-%m-%d")
            fact = requests.get("http://numbersapi.com/" + str(date_val.month) + "/" + str(date_val.day) + "/date").content
            date_string = date_val.strftime("{S} %B").replace('{S}', str(date_val.day) + date_suffix(date_val.day))
            speech = "Here is something special about " + date_string
            reprompt = HELP_REPROMPT
        else:
            fact = "Sorry! But it seems like you have not specified the date properly. Try saying \"What is special about 2nd October?\""
            date_string = "unspecified date"
            speech = "Here is the result I got!"
            reprompt = HELP_REPROMPT

        handler_input.response_builder.speak(speech).ask(reprompt).add_directive(
            RenderDocumentDirective(
                token="dateToken",
                document=_load_apl_document("trivia.json"),
                datasources={
                    'triviaTemplateData': {
                        'type': 'object',
                        'objectId': 'dateSample',
                        'title': date_string,
                        'backgroundImage': {
                            'sources': [
                                {
                                    'url': "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_background.jpg",
                                    'size': "small",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                },
                                {
                                    'url': "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_background.jpg",
                                    'size': "large",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                }
                            ]
                        },
                        'image': {
                            'sources': [
                                {
                                    'url': "https://dummyimage.com/16:9x1080/4c/00b0e6.png&text=" + date_string,
                                    'size': "small",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                },
                                {
                                    'url': "https://dummyimage.com/16:9x1080/4c/00b0e6.png&text=" + date_string,
                                    'size': "large",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                }
                            ]
                        },
                        'properties': {
                            'triviaSsml': '<speak>' + fact + '</speak>'
                        },
                        'transformers': [
                            {
                                'inputPath': 'triviaSsml',
                                'outputName': 'triviaSpeech',
                                'transformer': 'ssmlToSpeech'
                            },
                            {
                                'inputPath': 'triviaSsml',
                                'outputName': 'triviaText',
                                'transformer': 'ssmlToText'
                            }
                        ],
                        "logoUrl": "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_skill_logo.png",
                        "hintText": "Try, \"Alexa, what is the significance of number 42 in mathematics?\""
                    }
                }
            )
        ).add_directive(
            ExecuteCommandsDirective(
                token="dateToken",
                commands=[
                    SetPageCommand(
                        component_id="pagerComponentId",
                        position=Position.RELATIVE,
                        value=1,
                        delay=3000),
                    SpeakItemCommand(
                        component_id="karaokeComponentId",
                        highlight_mode=HighlightMode.LINE)
                ]
            )
        )

        return handler_input.response_builder.response


class NumberTriviaIntentHandler(AbstractRequestHandler):
    """Handler for Number Trivia Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("NumberTriviaIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In Number Trivia Intent")

        slots = handler_input.request_envelope.request.intent.slots

        if 'number_slot' in slots and slots['number_slot'].value != None:
            number = slots['number_slot'].value
            handler_input.attributes_manager.session_attributes['number_slot_key'] = number
            number_string = str(number)
            fact = requests.get("http://numbersapi.com/" + number_string + "/trivia").content
            speech = "Here is something special about " + number_string
            reprompt = HELP_REPROMPT
        elif 'random_slot' in slots and slots['random_slot'].value != None:
            number_string = "random number"
            fact = requests.get("http://numbersapi.com/random/trivia").content
            speech = "Here is something special about a randomly generated number!"
            reprompt = HELP_REPROMPT
        elif 'number_slot_key' in handler_input.attributes_manager.session_attributes:
            number = handler_input.attributes_manager.session_attributes['number_slot_key']
            number_string = str(number)
            fact = requests.get("http://numbersapi.com/" + number_string + "/trivia").content
            speech = "Here is something special about " + number_string
            reprompt = HELP_REPROMPT
        else:
            fact = "Sorry! But it seems like you have not specified the number properly. Try saying \"What is special about the number 42?\""
            number_string = "unspecified number"
            speech = "Here is the result I got!"
            reprompt = HELP_REPROMPT

        handler_input.response_builder.speak(speech).ask(reprompt).add_directive(
            RenderDocumentDirective(
                token="numberToken",
                document=_load_apl_document("trivia.json"),
                datasources={
                    'triviaTemplateData': {
                        'type': 'object',
                        'objectId': 'numberSample',
                        'title': number_string,
                        'backgroundImage': {
                            'sources': [
                                {
                                    'url': "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_background.jpg",
                                    'size': "small",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                },
                                {
                                    'url': "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_background.jpg",
                                    'size': "large",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                }
                            ]
                        },
                        'image': {
                            'sources': [
                                {
                                    'url': "https://dummyimage.com/16:9x1080/4c/00b0e6.png&text=" + number_string,
                                    'size': "small",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                },
                                {
                                    'url': "https://dummyimage.com/16:9x1080/4c/00b0e6.png&text=" + number_string,
                                    'size': "large",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                }
                            ]
                        },
                        'properties': {
                            'triviaSsml': '<speak>' + fact + '</speak>'
                        },
                        'transformers': [
                            {
                                'inputPath': 'triviaSsml',
                                'outputName': 'triviaSpeech',
                                'transformer': 'ssmlToSpeech'
                            },
                            {
                                'inputPath': 'triviaSsml',
                                'outputName': 'triviaText',
                                'transformer': 'ssmlToText'
                            }
                        ],
                        "logoUrl": "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_skill_logo.png",
                        "hintText": "Try, \"Alexa, give me a fact about 25th September.\""
                    }
                }
            )
        ).add_directive(
            ExecuteCommandsDirective(
                token="numberToken",
                commands=[
                    SetPageCommand(
                        component_id="pagerComponentId",
                        position=Position.RELATIVE,
                        value=1,
                        delay=3000),
                    SpeakItemCommand(
                        component_id="karaokeComponentId",
                        highlight_mode=HighlightMode.LINE)
                ]
            )
        )

        return handler_input.response_builder.response


class MathTriviaIntentHandler(AbstractRequestHandler):
    """Handler for Math Trivia Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("MathTriviaIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In Math Trivia Intent")

        slots = handler_input.request_envelope.request.intent.slots

        if 'number_slot' in slots and slots['number_slot'].value != None:
            number = slots['number_slot'].value
            handler_input.attributes_manager.session_attributes['number_slot_key'] = number
            math_string = str(number)
            fact = requests.get("http://numbersapi.com/" + math_string + "/math").content
            speech = "Here is something special about the number " + math_string + " in the world of mathematics!"
            reprompt = HELP_REPROMPT
        elif 'random_slot' in slots and slots['random_slot'].value != None:
            math_string = "random number"
            fact = requests.get("http://numbersapi.com/random/math").content
            speech = "Here is something special about a randomly generated number in the world of mathematics!"
            reprompt = HELP_REPROMPT
        elif 'number_slot_key' in handler_input.attributes_manager.session_attributes:
            number = handler_input.attributes_manager.session_attributes['number_slot_key']
            math_string = str(number)
            fact = requests.get("http://numbersapi.com/" + math_string + "/math").content
            speech = "Here is something special about the number " + math_string + " in the world of mathematics!"
            reprompt = HELP_REPROMPT
        else:
            fact = "Sorry! But it seems like you have not specified the number properly. Try saying \"What is the significance of number 42 in mathematics?\""
            math_string = "unspecified number"
            speech = "Here is the result I got!"
            reprompt = HELP_REPROMPT

        handler_input.response_builder.speak(speech).ask(reprompt).add_directive(
            RenderDocumentDirective(
                token="mathToken",
                document=_load_apl_document("trivia.json"),
                datasources={
                    'triviaTemplateData': {
                        'type': 'object',
                        'objectId': 'mathSample',
                        'title': math_string,
                        'backgroundImage': {
                            'sources': [
                                {
                                    'url': "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_background.jpg",
                                    'size': "small",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                },
                                {
                                    'url': "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_background.jpg",
                                    'size': "large",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                }
                            ]
                        },
                        'image': {
                            'sources': [
                                {
                                    'url': "https://dummyimage.com/16:9x1080/4c/00b0e6.png&text=" + math_string,
                                    'size': "small",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                },
                                {
                                    'url': "https://dummyimage.com/16:9x1080/4c/00b0e6.png&text=" + math_string,
                                    'size': "large",
                                    'widthPixels': 0,
                                    'heightPixels': 0
                                }
                            ]
                        },
                        'properties': {
                            'triviaSsml': '<speak>' + fact + '</speak>'
                        },
                        'transformers': [
                            {
                                'inputPath': 'triviaSsml',
                                'outputName': 'triviaSpeech',
                                'transformer': 'ssmlToSpeech'
                            },
                            {
                                'inputPath': 'triviaSsml',
                                'outputName': 'triviaText',
                                'transformer': 'ssmlToText'
                            }
                        ],
                        "logoUrl": "https://raw.githubusercontent.com/Techievena/Techievena.github.io/master/img/post_images/numbers_trivia_skill_logo.png",
                        "hintText": "Try, \"Alexa, tell me something about any number.\""
                    }
                }
            )
        ).add_directive(
            ExecuteCommandsDirective(
                token="mathToken",
                commands=[
                    SetPageCommand(
                        component_id="pagerComponentId",
                        position=Position.RELATIVE,
                        value=1,
                        delay=3000),
                    SpeakItemCommand(
                        component_id="karaokeComponentId",
                        highlight_mode=HighlightMode.LINE)
                ]
            )
        )

        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(
                SKILL_NAME, HELP_MESSAGE))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(STOP_MESSAGE)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak('EXCEPTION_MESSAGE').ask(
            HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(DateTriviaIntentHandler())
sb.add_request_handler(NumberTriviaIntentHandler())
sb.add_request_handler(MathTriviaIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# TODO: Uncomment the following lines of code for request, response logs.
# sb.add_global_request_interceptor(RequestLogger())
# sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
