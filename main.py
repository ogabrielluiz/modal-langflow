from langflow import main
from langflow.database.base import create_db_and_tables
from langflow.interface.utils import setup_llm_caching

from pathlib import Path

import fastapi
import fastapi.staticfiles

from modal import Mount, Stub, asgi_app, Image

# Create a stub for the image and install Langflow
image = Image.debian_slim(python_version="3.10").pip_install("langflow")


stub = Stub("langflow", image=image)

app = main.create_app()

assets_path = Path(main.__file__).parent / "frontend"


@stub.function(mounts=[Mount.from_local_dir(assets_path, remote_path="/assets")])
@asgi_app()
def wrapper():
    app.mount("/", fastapi.staticfiles.StaticFiles(directory="/assets", html=True))
    # Events are not triggered automatically so we need to run them manually
    create_db_and_tables()
    setup_llm_caching()
    return app
