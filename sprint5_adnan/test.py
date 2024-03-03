# Assume you have data in a cloud DB e-g dynamoDB, which contains data about word frequency e-g “hello:2”, “world:5”, create a system where: You have an API called “wordCount”, which takes in a parameter “word” Users can call the API with parameter e-g word=”hello” You should return the word frequency, e-g return “2” for input word=”hello”




import requests
# first I have to send request using requests library.

# I am assuming API URL as /wordCount/{“hello:2”, “world:5”}
URL = '/wordCount/{“hello:2”, “world:5”}'
resp = requests.get(URL)

if resp.status == 200:
    frequency = resp.json()['hello']

    print("Frequency of Hello: ", frequency)