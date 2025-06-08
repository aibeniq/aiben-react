#!/bin/bash
PARAMS=(
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  OPENAI_API_KEY
  REPLICATE_API_TOKEN
  SMTP_PASSWORD
  POSTGRES_PASSWORD
  SECRET_KEY
  FIRST_SUPERUSER_PASSWORD
)

for PARAM in "${PARAMS[@]}"; do
  VALUE=$(aws ssm get-parameter --name "/aiben-react/$PARAM" --with-decryption --query "Parameter.Value" --output text --region eu-north-1)
  echo "export $PARAM=$VALUE" | sudo tee -a /etc/profile.d/aiben-react-env.sh
done

sudo chmod +x /etc/profile.d/aiben-react-env.sh