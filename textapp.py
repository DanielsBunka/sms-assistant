import os
import threading
from dotenv import load_dotenv
from twilio.rest import Client
from flask import Flask, request, copy_current_request_context
from twilio.twiml.messaging_response import MessagingResponse

# Services Imports
from services.trains import grab_trains
from services.stocks import grab_stocks
from services.ai import ask_ai, clear_history
from services.database import startDatabase, saveMessageDatabase

# AI Import
from openai import OpenAI

# Load up all the variables from .env file
load_dotenv()
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
PERSONAL_PHONE = os.getenv("PERSONAL_PHONE")
TRAIN_API = os.getenv("TRAIN_API")
AI_API = os.getenv("AI_API")

# AI Client
AI_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=AI_API
)


# ----------
# Unprompted Send Function
# ----------
def instant_send(textbody, phonenumber):
    client = Client(TWILIO_SID, TWILIO_TOKEN)

    message = client.messages.create(
        body=textbody, from_=TWILIO_PHONE, to=phonenumber
    )

    print("Unprompted message sent! \n Message ID: " + message.sid)


# ----------
# Webhook Listening Part
# ----------
# Starts the Flask web framework
startDatabase()
app = Flask(__name__)


# This opens a webpage that ends with with /sms
# Tells it to expect data - a POST request
# app.route connects it to the listen_reply function
@app.route("/sms", methods=["POST"])
def command_reply():

    # Reads the request that Twilio sent
    incoming_request = request.values.get("Body", "").lower().strip()
    sender_number = request.values.get("From", "unknown")
    print("Message arrived " + incoming_request)

    # To be able to seperate command fields - 1st word = command, 2nd word = destination
    split_request = incoming_request.split()

    # Needed to be able to send a request back to Twilio
    resp = MessagingResponse()

    # Necessary so a empty message doesn't break the code
    if not split_request:
        return str(resp)

    # Makes it more readable - First word in message is the command
    command = split_request[0]

    # Menu
    match command:

        case ".ping":
            resp.message("Pong! The connection works!")
            saveMessageDatabase(sender_number, incoming_request, command, "Pong! The connection works!")

        # Trains
        case ".train":
            # Checks if there is a 2nd word in the message
            if len(split_request) > 1:
                route = split_request[1]
                if route == "default":
                    trainrequest = grab_trains("SOP", "LVC", "Southport", "Liverpool Central", TRAIN_API)
                elif route == "liverpool":
                    trainrequest = grab_trains("LVC", "SOP", "Liverpool Central", "Southport", TRAIN_API)
                elif route == "moorfields":
                    trainrequest = grab_trains("MRF", "SOP", "Moorfields", "Southport", TRAIN_API)
                else:
                    trainrequest = "❌ No Valid Route Input! \n Input a Route with the .train command"
            else:
                trainrequest = ("❌ No Valid Route Input! \n Input a Route with the .train command")

            resp.message(trainrequest)
            saveMessageDatabase(sender_number, incoming_request, command, trainrequest)

        # Stocks
        case ".stock":
            if len(split_request) > 1:
                stockresponse = grab_stocks(split_request[1])
            else:
                stockresponse = grab_stocks()
            resp.message(stockresponse)
            saveMessageDatabase(sender_number, incoming_request, command, stockresponse)

        case ".phone" | ".number":
            response_text = f"Your phone number is {sender_number}"
            resp.message(response_text)
            saveMessageDatabase(sender_number, incoming_request, command, response_text)

        case ".ai":
            if len(split_request) > 1:
                if split_request[1] == "clear":
                    response_text = clear_history(sender_number)
                    resp.message(response_text)
                    saveMessageDatabase(sender_number, incoming_request, command, response_text)
                else:
                    question = " ".join(split_request[1:])
                    
                    @copy_current_request_context
                    def ai_threading_task():
                        ai_answer = ask_ai(question, sender_number, AI_client)
                        instant_send(ai_answer, sender_number)
                        saveMessageDatabase(sender_number, incoming_request, ".ai", ai_answer)

                    thread = threading.Thread(target=ai_threading_task)
                    thread.start()

                    return "",200
                    
            else:
                response_text = ".ai has no command after it"
                resp.message(response_text)
                saveMessageDatabase(sender_number, incoming_request, command, response_text)

        case _:
            response_text = "Unrecognised command! Try Again! \n Commands: \n .ping \n .train \n .stock \n .ai \n .phone"
            resp.message(response_text)
            saveMessageDatabase(sender_number, incoming_request, response=response_text)

    return str(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
