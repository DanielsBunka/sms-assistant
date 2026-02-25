import os
from dotenv import load_dotenv
from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Load up all the variables from .env file
load_dotenv()
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
PERSONAL_PHONE = os.getenv("PERSONAL_PHONE")
TRAIN_API = os.getenv("TRAIN_API")

#----------
# Unprompted Send Function
#----------
def instant_send(textbody):
      client = Client(TWILIO_SID, TWILIO_TOKEN)
      
      message = client.messages.create(
            body=textbody,
            from_=TWILIO_PHONE,
            to=PERSONAL_PHONE
      )

      print("Unprompted message sent! \n Message ID: " + message.sid )

#----------
# Webhook Listening Part
#----------
# Starts the Flask web framework
app = Flask(__name__)

# This opens a webpage that ends with with /sms
# Tells it to expect data - a POST request
# app.route connects it to the listen_reply function
@app.route("/sms", methods=['POST'])
def listen_reply():
    
    # Reads the request that Twilio sent
    incoming_request = request.values.get('Body','').lower().strip()
    print("Message arrived " + incoming_request)

    # Needed to be able to send a request back to Twilio
    resp = MessagingResponse()

    if incoming_request == '.ping':
            resp.message("Pong! The connection works!")
    elif incoming_request == '.train':
            resp.message("Work In Progress Function!")
    else:
            resp.message("Unrecognised command texted! Try Again!")

    return str(resp)




if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)

    
