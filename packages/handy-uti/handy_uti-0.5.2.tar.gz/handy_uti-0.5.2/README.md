# Handy Utilities with Streamlit

> Handy Utilities For Daily Life Hacks

## Utilities

| Feature | Description | Demo |
| --- | --- | :---: |
| YouTube Transcriber | Extract captions if available, transcribe the audio with AI otherwise |  [![youtube]](https://youtu.be/BdSL8LLJOok)  [![youtube]]( https://youtu.be/I5r0O7iMjKc)  [![screenshot]](https://raw.githubusercontent.com/hoishing/handy-uti/main/screenshots/yt_transcriber.webp) |
| Token Counter | Count tokens used in a text for different LLM models |  [![youtube]](https://youtu.be/gfKEGCvUJbQ)  [![screenshot]](https://raw.githubusercontent.com/hoishing/handy-uti/main/screenshots/token_counter.webp) |
| Mistral OCR | Turn PDF or Image to Markdown with Mistral AI OCR |  [![youtube]](https://youtu.be/NGe5YIqdYQQ)  [![screenshot]](https://raw.githubusercontent.com/hoishing/handy-uti/main/screenshots/mistral_ocr.webp) |
| MD to EPUB | Convert markdown with images to epub |  [![youtube]](https://youtu.be/X3eKrTwfYHw)  [![screenshot]](https://raw.githubusercontent.com/hoishing/handy-uti/main/screenshots/md2epub.webp) |
| Direct Link | Get direct media file link from Google Drive or Github |  [![youtube]](https://youtu.be/1v-viXpOY2g)  [![screenshot]](https://raw.githubusercontent.com/hoishing/handy-uti/main/screenshots/direct_link.webp) |
| APNs Tester | Test Apple Push Notification With Ease |  [![youtube]](https://youtu.be/ZocYEKC9rSA)  [![screenshot]](https://raw.githubusercontent.com/hoishing/handy-uti/main/screenshots/apn_tester.webp) |
| Remove DRM | Remove DRM of Your Own Ebook from Adobe Digital Edition |  [![youtube]](https://youtu.be/frNyHMN4_e4)  [![screenshot]](https://raw.githubusercontent.com/hoishing/handy-uti/main/screenshots/rm_drm.webp) |
| Groq Models | List all currently active and available models in Groq |  [![youtube]](https://youtu.be/CO8QFJhJ2Z8)  [![screenshot]](https://raw.githubusercontent.com/hoishing/handy-uti/main/screenshots/groq_models.webp) |
| PyPI Name Checker | Check the availability of PyPi package names |  [![youtube]](https://youtu.be/SRdoIzs6N3k)  [![screenshot]](https://raw.githubusercontent.com/hoishing/handy-uti/main/screenshots/pypi_name_checker.webp) |
| Astrobro Updater | Update [Astrobro](https://hoishing.github.io/astrobro/) JSON files with city names and country codes |  [![screenshot]](https://raw.githubusercontent.com/hoishing/handy-uti/main/screenshots/astrobro_updater.webp) |

[screenshot]: https://api.iconify.design/material-symbols:imagesmode-rounded.svg?color=%23ffae52
[youtube]: https://api.iconify.design/bi:youtube.svg?color=%23ff4242

## Usage

- Run Directly with `uvx`

```bash
uvx handy-uti

# update with latest version
uvx handy-uti@latest
```

- Install Locally

```bash
uv tool install handy-uti

# then start the streamlit app
handy-uti
```

## API Keys

- api key fields in the app will be auto-filled after providing the `.env` file (optional)

```bash
uvx handy-uti path/to/your/.env
```

- content of `.env` file

```ini
GOOGLE_API_KEY=your-google-api-key
GROQ_API_KEY=your-groq-api-key
MISTRAL_API_KEY=your-mistral-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key
```

## Questions?

Open a [github issue] or ping me on [LinkedIn]

[github issue]: https://github.com/hoishing/handy-utils/issues
[LinkedIn]: https://www.linkedin.com/in/kng2
