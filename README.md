# Tiny Museum

Tiny Museum is a visual gallery for everyday objects and their stories. Add an object with an emoji, color, memory, and location. Then draw playful prompts that help you notice it differently.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Test

```bash
python -m unittest discover -s tests
```

Data stays in the local `tiny_museum.db` file.

