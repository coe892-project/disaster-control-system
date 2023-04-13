FROM python:latest

# Set the working directory
WORKDIR /app

# Copy the Pipfile and Pipfile.lock files to the working directory
COPY Pipfile Pipfile.lock ./

# Install dependencies using pipenv
RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile


# Copy the rest of the application code to the working directory
COPY backend .

# Expose the port that the FastAPI service will listen on
EXPOSE 8000

# Set the environment variables
ENV RABBITMQ_HOST="138.91.227.110"

# Start the FastAPI service and RabbitMQ consumer
CMD ["uvicorn", "dispatch_endpoints:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers", "--forwarded-allow-ips", "*", "--access-log", "--log-level", "info"]

FROM node:15.4 as build

WORKDIR /app
COPY disaster_control_ui/package*.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:1.19

COPY disaster_control_ui/nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/build /usr/share/nginx/html
