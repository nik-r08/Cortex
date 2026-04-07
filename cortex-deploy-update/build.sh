#!/usr/bin/env bash
set -e

echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Building frontend..."
cd frontend
npm install
npx vite build
cd ..

echo "Build complete"
