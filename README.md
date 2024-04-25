# CSE123 Automatic Pet Feeder 
## Testing Commands for API Endpoint

Food Level Low and Water Level High: 
curl -X POST -H "Content-Type: application/json" -d '{"food_level": "low", "water_level": "high"}' http://localhost:8080/api/receive_data 
{ 
"status": "Data successfully received" 
} 

Food Level High and Water Level Low: 
curl -X POST -H "Content-Type: application/json" -d '{"food_level": "high", "water_level": "low"}' http://localhost:8080/api/receive_data 
{ 
"status": "Data successfully received" 
} 

/api/food_level: 
curl http://localhost:8080/api/food_level 
{ 
"food_level": "high" 
}
