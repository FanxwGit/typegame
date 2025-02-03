## Environment

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Before starting, you need to initialize the database, which will load the data from the files in the data folder.

```bash
cd typegame
python /db/db.py
```

To start the Flask application

```bash
python app.py
```

Then, simply enter the student ID from the /data/userinfo.txt file to start the game.


## Commit Message Format

Please use the following commit type

```bash
Feat: Add new feature

Fix: Fix bug

Docs: Update documentation

Style: Adjust code style without functional changes

Refactor: Refactor code without fixing bugs or adding new features

Test: Add or modify test code
```
