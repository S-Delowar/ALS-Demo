# # Base image
# FROM python:3.11-slim

# # Setting environment variables
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Setting work directory
# WORKDIR /app

# # Installing system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

#     # Chache
# RUN pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
# RUN pip install sentence-transformers==2.2.2
# RUN pip install playwright
# RUN playwright install chromium
# RUN playwright install-deps


# # Installing Python dependencies
# COPY requirements.txt .
# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt

# # Copying project files
# COPY . .

# # Make start.sh executable
# RUN chmod +x /app/start.sh

# # Exposing the port
# EXPOSE 8000

# # Run the app with start.sh - migration, create superuser, collectstatic and gunicorn
# CMD ["/app/start.sh"]



# Base image
FROM python:3.11-slim

# Setting environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Setting work directory
WORKDIR /app

# --- SYSTEM DEPENDENCIES LAYER ---
# Combine apt-get and playwright deps to create a single cached layer
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# --- HEAVY PYTHON LIBRARIES (The "Static" Layer) ---
# We install these BEFORE requirements.txt because they change rarely but are huge.
# "--mount=type=cache" tells Docker to use a local cache on your host machine.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install playwright && \
    playwright install chromium --with-deps

# --- PROJECT DEPENDENCIES LAYER (The "Dynamic" Layer) ---
COPY requirements.txt .

# Remove "--no-cache-dir" and use the cache mount instead.
# If you add a small package to requirements.txt, pip will check the cache 
# and see it already has the other 20 packages, installing only the new one.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# --- SOURCE CODE LAYER ---
# This is the most frequent changing layer, keep it last.
COPY . .

# Make start.sh executable
RUN chmod +x /app/start.sh

# Exposing the port
EXPOSE 8000

# Run the app
CMD ["/app/start.sh"]