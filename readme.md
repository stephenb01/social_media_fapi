Make sure the environment is running:
source .venv/bin/activate

Got to WAT_Django/social_media_fapi/social_media_fapi and run this:
`uvicorn social_media_fapi.main:app --port 8002 --reload`


Install the requirements for dev and the site:
pip install -r requirements-dev.txt
pip install -r requirements.txt


Upgrade all packactes run:
pip install --upgrade -r requirements.txt