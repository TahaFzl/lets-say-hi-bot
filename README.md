# 🎉 Lets Say Hi --- Telegram GIF Generator Bot

A fun Telegram bot that creates a **personalized square GIF** with the
text\
**"Hi `<name>`{=html}"** placed on top of a cat (or any custom) video.

Works in two modes:

1.  **Normal Chat Mode:**\
    `/start → enter a name → choose video or send your own → receive GIF`

2.  **Inline Mode:**\
    Type in any chat:

        @lets_say_hi_bot name

    Bot instantly returns an inline GIF that can be sent to the same
    chat.

------------------------------------------------------------------------

## ✨ Features

-   Add custom text (`Hi <name>`) onto any video
-   Auto-crop video to a perfect **square GIF**
-   Supports:
    -   User-uploaded videos
    -   Bot's built-in base videos
    -   Default video (`default.mp4`)
-   Inline mode with auto-cached GIFs
-   Storage channel support (no messages in user's private chat)
-   Fast, lightweight inline rendering (3 seconds, 256×256 GIF)
-   Clean FFmpeg rendering pipeline

------------------------------------------------------------------------

## 📦 Requirements

-   Python 3.9+

-   FFmpeg installed

    ``` bash
    brew install ffmpeg
    ```

-   Dependencies:

    ``` bash
    pip install python-telegram-bot==20.* python-dotenv
    ```

------------------------------------------------------------------------

## 📁 Project Structure

    LSH/
    │
    ├── main.py                    # Main bot code
    ├── .env                       # Environment variables
    │
    ├── base_videos/               # Base videos (square crop recommended)
    │   └── default.mp4           # Required for inline mode
    │
    ├── fonts/
    │   └── font.ttf               # TTF font for drawtext
    │
    └── README.md

------------------------------------------------------------------------

## 🔧 Environment Variables (`.env`)

Create a `.env` file:

``` env
TELEGRAM_TOKEN=YOUR_BOT_TOKEN_HERE
INLINE_STORAGE_CHAT_ID=-100XXXXXXXXXXXX
```

### How to get `INLINE_STORAGE_CHAT_ID`

1.  Create a **private Telegram channel** (e.g., "LSH Storage")
2.  Add your bot as **Admin** (must be able to send messages)
3.  Send any message inside the channel
4.  Forward that message to `@RawDataBot`
5.  Copy the value of `"chat": { "id": -100XXXXXXXXXX }`

------------------------------------------------------------------------

## 🚀 Run the Bot

``` bash
python3 main.py
```

------------------------------------------------------------------------

## 🧪 Usage

### Normal Chat Mode

1.  Start the bot:

        /start

2.  Enter a name

3.  Choose:

    -   Send your own video\

    -   Click on a base video\

    -   Or use:

            /default

4.  Receive your custom GIF

------------------------------------------------------------------------

### Inline Mode

In **any chat**, type:

    @lets_say_hi_bot name

Bot will generate & cache a lightweight GIF and show it as an inline
result.\
Tap to send it to the chat.

No noise in your private messages --- files are stored in the storage
channel only.

------------------------------------------------------------------------

## 🛠 FFmpeg Rendering

The bot does:

-   Square crop
-   Scaling
-   Text overlay
-   Auto padding
-   GIF optimization

Inline GIFs use:

-   3 seconds duration
-   256×256 resolution
-   10 FPS

This keeps inline responses fast and avoids Telegram timeouts.

------------------------------------------------------------------------

## 🧩 Notes

-   Make sure `default.mp4` exists in `base_videos/`
-   Make sure your bot stays admin in the storage channel
-   The owner of the channel must be a **human account** (Telegram
    limitation)

------------------------------------------------------------------------

## 📝 License

MIT --- Feel free to fork, customize, and build your own fun GIF bot!