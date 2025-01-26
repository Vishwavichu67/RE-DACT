#!/usr/bin/env bash
apt-get update && apt-get install -y libmupdf-dev mupdf-tools
pip install -r requirements.txt
