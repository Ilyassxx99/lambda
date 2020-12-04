#!/bin/bash
zip -g lambda.zip index.py
git add .
git commit -m "Last push"
git push lambda master
