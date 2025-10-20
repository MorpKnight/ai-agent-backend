# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set the working directory in the container
WORKDIR /code

# 3. Copy the dependencies file and install them
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 4. Copy the local code to the container
COPY ./app /code/app

# 5. Expose the port the app runs on
EXPOSE 8000

# 6. Command to run the application using Uvicorn
# The host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]