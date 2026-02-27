import os
import requests
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
# Main Train Data Grabbing Function
#----------

def grab_trains(from_crs, to_crs, from_name, to_name):
      api_url = f"https://api1.raildata.org.uk/1010-live-departure-board-dep1_2/LDBWS/api/20220120/GetDepartureBoard/{from_crs}"
      apiheaders = { "x-apikey": TRAIN_API }
      api_parameters = {
            "numRows": 3,
            "filterCrs": to_crs,
            "filterType": "to",
      }

      try:
        apiresponse = requests.get(api_url, headers=apiheaders, params=api_parameters)
        data = apiresponse.json()
        filterdata = data.get('trainServices',[])

        if not filterdata:
              return f"No trains found between {from_name} to {to_name} currently!"
        
        message = f"Train Journey: {from_name} to {to_name}: \n \n"

        # Loop through the 3 trains provided by the API
        for train in filterdata:
              leavetime = train.get('std')
              status = train.get('etd')
              platform = train.get('platform', 'TBC')
              is_cancelled = train.get('isCancelled', False)
              
              if is_cancelled:
                    message += f"❌ {leavetime} - CANCELLED \n\n"
              else:
                    message += f"✅ {leavetime} ({status}) - Platform {platform} \n \n"

        return message
      
      except Exception as e:
            return "⚠️ Error: Couldn't connect to the Official National Rail API"
        
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
def command_reply():
    
    # Reads the request that Twilio sent
    incoming_request = request.values.get('Body','').lower().strip()
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
    if command == '.ping':
            resp.message("Pong! The connection works!")
    elif command == '.train':
            # Checks if there is a 2nd word in the message
            if len(split_request) > 1:
                  route = split_request[1]
                  if route == 'default':
                        trainrequest = grab_trains('SOP', 'LVC', 'Southport', 'Liverpool Central')
                  elif route == 'liverpool':
                        trainrequest = grab_trains('LVC', 'SOP', 'Liverpool Central', 'Southport')
                  elif route == 'moorfields':
                        trainrequest = grab_trains('MRV', 'SOP', 'Moorfields', 'Southport')
                  else:
                        trainrequest = '❌ No Valid Route Input! \n Input a Route with the .train command'
            else:
                  trainrequest = '❌ No Valid Route Input! \n Input a Route with the .train command'
            resp.message(trainrequest)
    else:
            resp.message("Unrecognised command texted! Try Again!")

    return str(resp)




if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)

    
