import pytest 
import requests

DOMAIN = "127.0.0.1"



if __name__ == "__main__":   
    # Making a GET request
    r = requests.get('https://api.github.com/users/naveenkrnl')
    
    # check status code for response received
    # success code - 200
    print(r)
    
    # print content of request
    print(r.content)