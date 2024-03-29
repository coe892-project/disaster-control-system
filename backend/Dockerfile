FROM python:latest

# Set the working directory
WORKDIR /app

# Copy the Pipfile and Pipfile.lock files to the working directory
COPY Pipfile Pipfile.lock ./

# Install dependencies using pipenv
RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile


# Copy the rest of the application code to the working directory
COPY . .

# Expose the port that the FastAPI service will listen on
EXPOSE 8000

# Start the FastAPI service and RabbitMQ consumer
CMD ["uvicorn", "dispatch_endpoints:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers", "--forwarded-allow-ips", "*", "--access-log", "--log-level", "info"]