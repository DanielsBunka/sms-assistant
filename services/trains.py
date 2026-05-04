import requests

# Get Access Token Function
def get_access_token(api_key):
    url = "https://data.rtt.io/api/get_access_token"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    response = requests.post(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.status_code} {response.text}")
    
    data = response.json()
    return data.get("access_token") or data.get("accessToken") or data.get("token")


def grab_trains(from_crs, to_crs, from_name, to_name, api_key):
      try:
            token = get_access_token(api_key)

            # API request data
            url = "https://data.rtt.io/gb-nr/location" 
            query_params = {
                  "location": from_crs,
                  "filterTo": f"gb-nr:{to_crs}",
                  "timeWindow": 120
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