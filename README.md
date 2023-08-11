# Basic ML Model Backend
Basic backend for handling ML-tasks, connected to resource-intensive models.
Primarily meant for future experiments around abstraction/representation, interfaces and scalability.
Secundarily meant for utility prototyping.

## Code entrypoints:
- `src/interfaces/backend_interface.py` holds the main FastAPI backend
- `src/interfaces/client_interface.py` will hold a client representation
- `src/utility/` holds hierarchical utility scripts (from bronze~general to gold~specific)

## Usage:
- Dockerization is not finished yet, since backend is WIP.

### Manual setup
0. Install Anaconda or Miniconda
1. Create Conda environment based on Python 3.10 (e.g. `conda create -y -k --prefix venv python=3.10`)
2. Activate the Conda environment (e.g. `conda activate venv/`)
3. Download, build and install the appropriate cuda-enabled pytorch packages (e.g. `conda install -y -k pytorch[version=2,build=py3.10_cuda11.7*] torchvision torchaudio pytorch-cuda=11.7 cuda-toolkit ninja git -c pytorch -c nvidia/label/cuda-11.7.0 -c nvidia`)
4. Install the pip requirements (`pip install -r requirements.txt`)
5. start the backend (e.g. `python start_backend.py`) - the FastAPI-Backend, via which LLM and vectorstore functinality is accessed. The backend can already be accessed via the logged uvicorn URL + /docs (Swagger UI)
6. start the streamlit app(s) (e.g. `streamlit run streamlit_main.py`) - the streamlit prototype app(s) will be started and a browser window should automatically open
7. (optional) start the umbrella flask app (e.g. `python flask_main.py`) - the flask app which integrates the streamlit apps will be started and can be accessed via the logged URL


## TODO
- implement parameterized model loading
- implement model search, downloading and metadata handling
    - implement model merging and finetuning ?
- encorporate models into LLMPool

- experiment around resource detection and planning
- experiment around containered LLM services with scheduling and priority support
