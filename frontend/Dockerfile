# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:20 AS build-stage

WORKDIR /app

COPY package*.json /app/

RUN npm install

COPY ./ /app/

ARG VITE_API_URL
# Use the build arg if provided, otherwise use placeholder for runtime replacement
ENV VITE_API_URL=${VITE_API_URL:-__API_BASE__}

RUN echo "Building with VITE_API_URL=$VITE_API_URL" && npm run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1

# Create non-root user for OpenShift compatibility
RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser appuser

COPY --from=build-stage /app/dist/ /usr/share/nginx/html
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf

# Change ownership for non-root user
RUN chown -R appuser:appuser /usr/share/nginx/html
RUN chown -R appuser:appuser /var/cache/nginx
RUN chown -R appuser:appuser /var/log/nginx
RUN chown -R appuser:appuser /etc/nginx/conf.d
RUN touch /var/run/nginx.pid
RUN chown -R appuser:appuser /var/run/nginx.pid

# Switch to non-root user
USER appuser

ENTRYPOINT ["/entrypoint.sh"]

# Expose port
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
