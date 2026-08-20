import json

with open('notebooks/msmarco_xi_ingestion_colab.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# VaaniRAG Offline Ingestion Pipeline\n",
            "\n",
            "This notebook is the reproducible environment to run the pipeline."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Clone repository and cd into it\n",
            "!git clone https://github.com/yashvyas101/Vaani.git || echo 'Already cloned'\n",
            "%cd Vaani/vaani-rag\n",
            "\n",
            "# Install requirements\n",
            "!pip install -r requirements.txt"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Verify T4 GPU\n",
            "import torch\n",
            "assert torch.cuda.is_available() and 'T4' in torch.cuda.get_device_name(0), 'Please enable a T4 GPU in Colab Runtime Settings'\n",
            "print('T4 GPU is available')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Load Secrets\n",
            "import os\n",
            "from google.colab import userdata\n",
            "os.environ['PINECONE_API_KEY'] = userdata.get('PINECONE_API_KEY')\n",
            "print('Loaded Pinecone API key')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Inspect Dataset\n",
            "!python scripts/inspect_dataset.py"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Test BGE-M3\n",
            "!python scripts/test_embedding.py"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 100 rows per language dry run\n",
            "!python -m ingestion.pipeline --languages en,hi,mr --max-rows 100 --strategy adaptive --dry-run"
        ]
    }
]

nb['cells'] = new_cells

with open('notebooks/msmarco_xi_ingestion_colab.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook rewritten.")
