# TDLOG Project ENPC

It is a website, where you can create an account and invest in stocks for fun (access of real stock actions trough APIs). Then you can also buy some actions (american or european thanks to a pricer).

## Install

- when opening VSCode, install the suggested extensions (Python, Black Formatter and Pylance)
- create your python environment `python3 -m venv .venv`
- copy the `.env.example` file to a `.env` file
- replace the `OPENAI_API_KEY` and `OPENAI_ORGANIZATION` env variables with the real values
- activate your environment with `  `
- download necessary data with `python -m nltk.downloader all`
- run the server with `flask --app main run --debug`

The server should answer on http://localhost:5000

You can deactivate the environment with `deactivate`.

## Adding librairies

if you need to use a new librairies, you can do it with pip
`pip install [library name]` or `pip3 install [library name]`
# Site-Pricer
