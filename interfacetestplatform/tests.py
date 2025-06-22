import requests
from django.test import TestCase

# Create your tests here.
rep = requests.get(url="https://petstore3.swagger.io/api/v3/user/login",params={"username":"ch","password":"123456"})
print(rep.text)
