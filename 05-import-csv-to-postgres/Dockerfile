FROM python:3.12

# Install the required packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the application code to the container image
WORKDIR /usr/src/app
COPY . /usr/src/app

# Run the application
CMD ["python", "main.py"]
