FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Remove supervisord
RUN pip uninstall -y supervisor

COPY . .

# Make start script executable
RUN chmod +x /app/start.sh

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["/app/start.sh"] 