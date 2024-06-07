# CSE123 Automatic Pet Feeder 
## Testing Commands for API Endpoint

Food Level Low and Water Level High:<br>
curl -X POST -H "Content-Type: application/json" -d '{"food_level": "low", "water_level": "high"}' http://localhost:8080/api/receive_data <br>
{ 
"status": "Data successfully received" 
} 

Food Level High and Water Level Low:<br>
curl -X POST -H "Content-Type: application/json" -d '{"food_level": "high", "water_level": "low"}' http://localhost:8080/api/receive_data <br>
{ 
"status": "Data successfully received" 
} 

/api/food_level:<br>
curl http://localhost:8080/api/food_level <br>
{ 
"food_level": "high" 
}

/api/water_level:<br>
curl http://localhost:8080/api/water_level <br>
{
  "water_level": "low"
}

## Testing Commands for Token API with curl and Firebase
POST Request (Login or Register): <br>
This curl command basically takes a username and a password then gives an api_key. <br>

curl -X POST http://localhost:8080/register \ <br>
-H "Content-Type: application/json" \ <br>
-d '{"username": "newuser", "password": "password123"}' <br>

GET or POST Request Requiring API Key: <br>
After registering or logging in, use the returned API key to make further requests. Replace YOUR_API_KEY_HERE with the actual API key. <br>

curl -X GET http://localhost:8080/api/get_levels \ <br>
-H "Authorization: Bearer YOUR_API_KEY_HERE" <br>

See the contens post in Firebase and "status: "Data updated in Firebase": <br>
curl -X POST http://localhost:8080/api/update_levels \ <br>
-H "Content-Type: application/json" \ <br>
-H "Authorization: Bearer YOUR_API_KEY_HERE" \ <br>
-d '{"food_level": "high", "water_level": "low"}' <br>

## Secure Connection Between Hardware/Software
POST to hardware to execute a command (dispense food or capture image): <br>
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer TOKENHERE" -d '{"command": "DISPENSE FOOD"}' http://10.0.0.98:8080/api/commands <br>
{ <br>
  "message": "Command received and written" <br>
}<br>

## Issues with JSON when trying to run between the server.py and client.py?
Delete the instructions.json on the server side under /.../uploads
