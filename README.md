# Build
```
docker build -t lod-bot -f docker/Dockerfile .
```

# Run
```
docker run -e TELEGRAM_TOKEN=YOUR_TOKEN --network=host lod-bot 
```
