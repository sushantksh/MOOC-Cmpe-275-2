#!/bin/bash
#
# test client access to our service

echo -e "\n"
curl -i -H "Accept: application/json" --data "email='test@gmail.com'&password='test'"  http://localhost:8080/user/login
echo -e "\n"


echo -e "\n"
curl -i -H "Accept: application/json" --data "email='test@gmail.com'&password='test123'"  http://localhost:8080/user/login
echo -e "\n"

