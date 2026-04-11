import requests

# We test against the local PC-A port 8000
url = "http://192.168.236.84:8000/api/analyze"

data = {
    "node_id": "N-01",
    "temperature": 38,
    "humidity": 25,
    "soil_moisture": 10,
    "light_level": 85000 
}

try:
    response = requests.post(url, data=data)
    print("Status Code:", response.status_code)
    print("Response JSON:")
    print(response.json())
except Exception as e:
    print("Error:", e)
