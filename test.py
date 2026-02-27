import requests 

reqUrl = "https://api1.raildata.org.uk/1010-live-departure-board-dep1_2/LDBWS/api/20220120/GetDepartureBoard/LST"
                    
headersList = {
"User-Agent":"",
 "x-apikey": "DAuAdLWCtLQKK55tFdQ4JD8qapMqBzZmiBirv9PWRaZcTKiP",
}

payload = ""

response = requests.request("GET", reqUrl, data = payload, headers = headersList)

print(response.text)