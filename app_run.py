#!/usr/local/bin/python3.9
import sys
import logging
from app import create_app

app = create_app()
app.run(port=5005)