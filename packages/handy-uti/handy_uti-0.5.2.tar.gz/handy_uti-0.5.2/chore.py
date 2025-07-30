from handy_uti import page_metadata

readme_md = """\
# Handy Utilities with Streamlit

> Handy Utilities For Daily Life Hacks

## Utilities

{utils_table}

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
"""


def utils_table_md():
    raw_img_base = (
        "https://raw.githubusercontent.com/hoishing/handy-uti/main/screenshots/"
    )
    youtube = "[youtube]: https://api.iconify.design/bi:youtube.svg?color=%23ff4242"
    screenshot = "[screenshot]: https://api.iconify.design/material-symbols:imagesmode-rounded.svg?color=%23ffae52"
    table = "| Feature | Description | Demo |\n"
    table += "| --- | --- | :---: |\n"
    for page_name in page_metadata:
        image = f"{raw_img_base}{page_name}.webp"
        img_link = f"[![screenshot]]({image})"
        yt_links = ""
        for yt in page_metadata[page_name]["youtube"].split(","):
            if yt.strip():
                yt_links += f" [![youtube]]({yt}) "
        title = page_metadata[page_name]["title"]
        description = page_metadata[page_name]["description"]
        row = f"| {title} | {description} | {yt_links} {img_link} |\n"
        table += row
    return f"{table}\n{screenshot}\n{youtube}"


if __name__ == "__main__":
    open("README.md", "w").write(readme_md.format(utils_table=utils_table_md()))
