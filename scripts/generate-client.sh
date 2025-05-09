#! /usr/bin/env bash

set -e
set -x

echo "Starting the generate-client script..."

cd backend
/mnt/c/miniconda/aibeniq-react/backend/.venv/Scripts/python.exe -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json
cd ..
mv openapi.json frontend/
cd frontend
npm run generate-client
npx biome format --write ./src/client
