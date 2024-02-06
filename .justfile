run:
    source ./venv/bin/activate
    source ./.env && python virtualpi.py pdfs

reset:
    rm ./pdfs/docs.pkl
    just run
    just run