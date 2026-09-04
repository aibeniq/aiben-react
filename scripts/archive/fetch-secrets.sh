#!/bin/bash

# Remove existing file first
sudo rm -f /etc/profile.d/aiben-react-env.sh

PARAMS=(
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  #OPENAI_API_KEY
  REPLICATE_API_TOKEN
  SMTP_PASSWORD
  POSTGRES_PASSWORD
  SECRET_KEY
  FIRST_SUPERUSER_PASSWORD
)

for PARAM in "${PARAMS[@]}"; do
  VALUE=$(aws ssm get-parameter --name "/aiben-react/$PARAM" --with-decryption --query "Parameter.Value" --output text --region eu-north-1)
  # Use >> for the first entry, then >> for subsequent ones, or use a temp file approach
  echo "export $PARAM=$VALUE" | sudo tee -a /etc/profile.d/aiben-react-env.sh > /dev/null
done

sudo chmod +x /etc/profile.d/aiben-react-env.sh