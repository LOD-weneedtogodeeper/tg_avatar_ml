# Information
Telegram bot, that allows you to create live photos with celebrities, your child photos etc...

![alt text](https://github.com/LOD-weneedtogodeeper/tg_avatar_ml/blob/master/media/work.jpg "Logo Title Text 1")

# Build
```
docker build -t lod-bot -f docker/Dockerfile .
```

# Run
```
docker run -e TELEGRAM_TOKEN=YOUR_TOKEN --network=host lod-bot 
```
