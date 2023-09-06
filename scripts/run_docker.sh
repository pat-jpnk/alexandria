docker run -dp 5000:5000 -w /app -v "$(pwd):/app" alexandria-api

# p creates port mapping
# d runs container in detached mode
# w
# v creates a volume (mapping of directory between local filesystem and container)

# w and v: code changes are included dynamically, no need to re-build and run image after every change
#          (running container with volume - host folder synced with container folder)