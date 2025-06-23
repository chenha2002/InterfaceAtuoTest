import requests
from django.test import TestCase

# Create your tests here.
rep = requests.post(url="https://petstore3.swagger.io/api/v3/pet",data={
  "id": 10,
  "name": "doggie",
  "category": {
    "id": 1,
    "name": "Dogs"
  },
  "photoUrls": [
    "string"
  ],
  "tags": [
    {
      "id": 0,
      "name": "string"
    }
  ],
  "status": "available"
})
print(rep.text)
