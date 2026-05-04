import os
from dotenv import load_dotenv
from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Services Imports
from services.trains import grab_trains
from services.stocks import grab_stocks

# Load up all the variables from .env file
load_dotenv()
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
PERSONAL_PHONE = os.getenv("PERSONAL_PHONE")
TRAIN_API = os.getenv("TRAIN_API")


# ----------
# Unprompted Send Function
# ----------
def instant_send(textbody):
    client = Client(TWILIO_SID, TWILIO_TOKEN)

    message = client.messages.create(
        body=textbody, from_=TWILIO_PHONE, to=PERSONAL_PHONE
    )

    print("Unprompted message sent! \n Message ID: " + message.sid)


# ----------
# Webhook Listening Part
# ----------
# Starts the Flask web framework
app = Flask(__name__)


# This opens a webpage that ends with with /sms
# Tells it to expect data - a POST request
# app.route connects it to the listen_reply function
@app.route("/sms", methods=["POST"])
def command_reply():

    # Reads the request that Twilio sent
    incoming_request = request.values.get("Body", "").lower().strip()
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

        # Stocks
        case ".stock":
            if len(split_request) > 1:
                stockchoice = split_request[1]
                resp.message(grab_stocks(stockchoice))
            else:
                resp.message(grab_stocks())

        case _:
            resp.message("Unrecognised command texted! Try Again!")

    return str(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
