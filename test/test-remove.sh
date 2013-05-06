#!/bin/bash
#
# test client access to our service

echo -e "\n"
curl -X DELETE http://localhost:8080/moo/data/moo
echo -e "\n"
