#!/usr/bin/env bash

echo "🔧 Forcing Python version to 3.10.13"
echo "python-3.10.13" > runtime.txt

echo "📦 Installing dependencies"
pip install -r requirements.txt
