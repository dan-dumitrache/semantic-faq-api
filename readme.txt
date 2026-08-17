Validate locally

Prepare the environment:

bash

cp .env.example .env

Edit '.env', then install and check:

bash

python3.12 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

ruff format .
ruff check .
mypy src
pytest

Start Docker:

bash

docker compose up --build

Test it:

bash

curl http://localhost:8000/health

bash

curl -X POST http://localhost:8000/v1/questions \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"Where can I download my invoices?"}'