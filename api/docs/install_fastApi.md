### Initialize venv

```bash
source .venv/bin/activate
```

### Install Requirements

```bash
pip install -r requirements.txt
```

### Install FastAPI

```bash
pip install "fastapi[standard]"
```

### Start the server

```bash
fastapi dev main.py --port 8080 --reload
```

#### INIT

```bash
uvicorn main:app --port 8080 --reload
```