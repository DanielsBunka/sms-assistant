from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Starts the Flask web framework
app = Flask(__name__)

#This opens a webpage that ends with with /sms
# Tells it to expect data - a POST request
@app.route("/sms", methods=['POST'])

def listen_reply():
    
    # Reads the request that Twilo sent
    incoming_request = request.values.get('Body','').lower().strip()
    print("Message arrived " + incoming_request)

    # Needed to be able to send a request back to Twilo
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
