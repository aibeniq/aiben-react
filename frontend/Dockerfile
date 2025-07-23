# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:18.20.8 AS build-stage

WORKDIR /app

# Add this debug line temporarily
RUN node -v && npm -v

COPY package*.json /app/

RUN npm install

COPY ./ /app/

ARG VITE_API_URL=${VITE_API_URL}

RUN npm run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1

COPY --from=build-stage /app/dist/ /usr/share/nginx/html

# Copy .htpasswd for Nginx basic auth
COPY .htpasswd /usr/share/nginx/html/.htpasswd

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
