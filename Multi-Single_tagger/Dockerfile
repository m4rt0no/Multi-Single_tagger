FROM python:3.12-slim

EXPOSE 8000
# Installing packages
RUN apt update && apt-get clean && \
    apt install -y --no-install-recommends \
        build-essential \
        ffmpeg \
        poppler-utils && \
    rm -rf /var/lib/apt/lists/*
    
# Adding user appuser
RUN useradd -m app_user

# Change to appuser
USER app_user

# Set working dir
WORKDIR /home/app_user

# Create logs directory
RUN mkdir log

# Copying requirements.txt file
COPY requirements.txt .

# Runtime configuration — override at deploy time with -e or via orchestrator env vars
ENV WORKERS=4
ENV SEMAPHORE=20

ENV PATH="/home/app_user/.local/bin:${PATH}"

RUN export PATH=${PATH}:${HOME}/.local/bin/ && pip3 install --no-cache-dir --upgrade pip && pip3 install -r requirements.txt

COPY --chown=app_user . .

RUN chmod +x /home/app_user/service_start.sh

# starting the service
ENTRYPOINT ["./service_start.sh"]
