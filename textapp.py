import os
import requests
from datetime import datetime, timedelta
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

# Get Access Token Function
def get_access_token():
    url = "https://data.rtt.io/api/get_access_token"
    headers = {
        "Authorization": f"Bearer {TRAIN_API}",
        "Accept": "application/json"
    }
    
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.status_code} {response.text}")
    
    data = response.json()
    return data.get("access_token") or data.get("accessToken") or data.get("token")


def grab_trains(from_crs, to_crs, from_name, to_name):
      try:
            token = get_access_token()

            # API request data
            url = "https://data.rtt.io/gb-nr/location" 
            query_params = {
                  "location": from_crs,
                  "to": to_crs
            }
            headers = {
                  "Authorization": f"Bearer {token}",
                  "Accept": "application/json",
                  "Version": "2026-04-23"
            }

            # API request
            response = requests.get(url,headers=headers, params=query_params)
            data = response.json()

            services = data.get('services',[])
            departures = [train for train in services if train.get("temporalData", {}).get("departure")]

            if not departures:
                  return f"No trains found between {from_name} to {to_name} currently!"
            
            message = f"Train Journey: {from_name} to {to_name}: \n \n"
            
            # Loop through the train services
            for train in departures[:3]:
                  
                  # Get raw nested data
                  departure_data = train.get("temporalData", {}).get("departure")
                  raw_leavetime = departure_data.get("scheduleAdvertised")
                  raw_status = departure_data.get("realtimeForecast")
                  is_cancelled = departure_data.get("isCancelled", False)

                  # Platform logic
                  platform_data = train.get("locationMetadata", {}).get("platform", {})
                  platform = platform_data.get("actual") or platform_data.get("forecast") or platform_data.get("planned") or "TBC"

                  # Format times
                  leavetime = raw_leavetime.split("T")[1][:5] if raw_leavetime else "N/A"
                  status = raw_status.split("T")[1][:5] if raw_status else "On Time"

                  if is_cancelled:
                        message += f"❌ {leavetime} - CANCELLED \n\n"
                  else:
                        message += f"✅ {leavetime} (Exp: {status}) - Platform {platform} \n\n"
                  
            return message
      
      except Exception as e:
            print(f"Train fetch failed: {e}")
            return "⚠️ Error: Couldn't connect to the Realtime Trains API"


        
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

    
