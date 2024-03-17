#!/bin/bash

source ./.py3/bin/activate

uvicorn main:app --reload 

# start server for ngrok
# this will make it so that anyone can access your app from internet
# ngrok http http://localhost:8000
