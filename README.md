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
curl http://localhost:8080/api/water_level
{
  "water_level": "low"
}