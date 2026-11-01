# Scam Token Classifier

Classify potentially malicious ERC-20 token contracts from their Ethereum bytecode using machine learning.

This Python research project treats EVM opcodes as text: it converts opcode sequences into TF-IDF features and compares **Logistic Regression**, **Random Forest**, and **XGBoost**. A Gradio interface accepts a contract address and returns a separate score and classification from each model.

**Research prototype:** predictions are screening signals. A `valid` result does not establish that a token is safe, and a `malicious` result requires further investigation.

## How it works

1. Fetch the contract's deployed bytecode from an Ethereum JSON-RPC endpoint using Web3.py.
2. Disassemble it with `pyevmasm` and retain opcode names, discarding instruction operands.
3. Transform the opcode sequence with a saved TF-IDF vectorizer using **1- to 4-grams**.
4. Run the three classifiers independently and return their malicious-class scores.

Source code and an ABI are not required for inference. The demo reads chain data; it does not require a wallet or private key.

## Quick start

The notebooks were saved with **Python 3.11.3**. Python 3.11 is the starting point for reproducing the original environment.

### 1. Clone and create an environment

```bash
git clone https://github.com/EthWiz/ml2-project.git
cd ml2-project
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

On Windows, activate with `.venv\Scripts\activate`.

### 2. Install dependencies

The checked-in [requirements.txt](requirements.txt) is an export of the original environment. It contains `file:///home/conda/...` references that will not resolve on another machine, as well as the legacy `sklearn` package alias.

To install its portable entries while replacing those local references with notebook tooling and `python-dotenv`, run this from the repository root:

```bash
python -c "from pathlib import Path; lines = Path('requirements.txt').read_text().splitlines(); Path('requirements-portable.txt').write_text('\n'.join(line for line in lines if line.strip() and ' @ file:' not in line and not line.startswith('sklearn==')) + '\n')"
python -m pip install -r requirements-portable.txt
python -m pip install "python-dotenv==1.0.0" notebook ipykernel
```

This keeps the original portable pins, including `scikit-learn==1.2.2`, `xgboost==1.7.5`, `web3==6.4.0`, and `gradio==3.32.0`. It is a setup workaround, not a fully locked or independently validated environment. Newer platforms may need additional dependency adjustments. Use an isolated environment for these historical packages.

### 3. Configure Ethereum access

Create a `.env` file in the repository root:

```dotenv
INFURA_URL=https://mainnet.infura.io/v3/YOUR_API_KEY
```

Supply your own Ethereum mainnet RPC URL. The variable is named `INFURA_URL`, but the code passes it to Web3's HTTP provider, so another compatible provider can be used.

The repository ignores `.env`. Keep provider credentials private; no private key or seed phrase is needed.

### 4. Launch the classifier

```bash
python -m notebook infere.ipynb
```

Select the Python environment you just created and run all cells in order. Use the Gradio interface shown in the notebook, or open the local URL printed by Gradio, typically [http://127.0.0.1:7860](http://127.0.0.1:7860).

Enter an Ethereum mainnet contract address or select one of the notebook's examples. Those examples reflect the project's original labels, not a current assessment of those contracts.

**Run notebooks from the repository root.** The inference notebook loads all four files in `weights/` using relative paths. Pretrained artifacts are included, so retraining and data collection are optional.

## Understanding the output

Each model returns:

| Field | Meaning |
| --- | --- |
| `prediction` | The model's `predict_proba` score for class `1` (malicious), between 0 and 1. |
| `classification` | `valid` for scores below `0.5`; `malicious` for scores at or above `0.5`. |

Illustrative output only; these values are not a measured prediction:

```json
{
  "Logistic Regression": {
    "prediction": 0.72,
    "classification": "malicious"
  },
  "Random Forest": {
    "prediction": 0.43,
    "classification": "valid"
  },
  "XGBoost": {
    "prediction": 0.61,
    "classification": "malicious"
  }
}
```

The models can disagree. The interface does not combine their predictions into an ensemble verdict, and the scores have not been established as calibrated real-world scam probabilities.

## Repository guide

| Path | Purpose |
| --- | --- |
| [infere.ipynb](infere.ipynb) | Load pretrained artifacts, fetch bytecode, and serve the classification demo. |
| [train.ipynb](train.ipynb) | Build TF-IDF features, evaluate models, fit them on the full dataset, and export artifacts. |
| [prepair_data.ipynb](prepair_data.ipynb) | Fetch bytecode for labeled addresses and generate the training CSV. |
| [data/](data/) | Prepared opcode dataset and input address lists. |
| [weights/](weights/) | Saved TF-IDF vectorizer and three classifiers. |
| [scripts/](scripts/) | Supporting data and opcode experiments. `scripts/app.py` displays opcodes; use the inference notebook for classification. |
| [requirements.txt](requirements.txt) | Original environment export. |

Filenames retain the spelling used in the repository.

## Reproduce training

### Use the included dataset

Open [train.ipynb](train.ipynb) from the repository root and run its cells in order:

```bash
python -m notebook train.ipynb
```

The notebook reads `data/small_dataset.csv`, using `Opcodes` as input and `Label` as the target:

- `0`: valid, according to the input labels.
- `1`: malicious, according to the input labels.

It fits a `TfidfVectorizer(ngram_range=(1, 4))` and evaluates the three classifiers with five-fold stratified cross-validation. SMOTE runs inside the evaluation pipeline to address class imbalance.

The final cells fit the three classifiers on the full dataset **without SMOTE** and overwrite:

```text
weights/
├── logistic_model.pkl
├── rf_model.pkl
├── tfidf.pkl
└── xgb_model.pkl
```

Keep the vectorizer and models from the same training run together. Training can use substantial memory because the opcode n-gram feature space is large.

### Optional: rebuild the dataset

Add an RPC endpoint under the separate variable used by [prepair_data.ipynb](prepair_data.ipynb):

```dotenv
FAST_NODE_URL=https://YOUR_ETHEREUM_MAINNET_RPC_ENDPOINT
```

Then run that notebook from the repository root. It reads `data/valdiated_addresses.json` and `data/malicious_addresses.npy`, selects the first 2,000 entries from the valid-address list and all malicious addresses, fetches their bytecode, removes empty opcode sequences, and writes `data/small_dataset.csv`.

This makes many network requests and overwrites the included CSV. Provider availability, rate limits, and changes in on-chain bytecode can affect the result.

## Recorded evaluation

The committed output in [train.ipynb](train.ipynb) reports the following five-fold means. Precision, recall, and F1 are for the malicious class.

| Model | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Logistic Regression | 0.816 | 0.271 | 0.651 | 0.322 |
| Random Forest | 0.953 | 0.560 | 0.532 | 0.491 |
| XGBoost | 0.954 | 0.529 | 0.478 | 0.459 |

These are historical notebook outputs, not newly reproduced benchmarks. High accuracy alone is insufficient for this imbalanced task.

**Evaluation caveats:**

- TF-IDF is fitted on the full dataset before cross-validation, allowing validation-fold information into the feature representation. A stronger evaluation would fit the vectorizer separately inside each fold.
- SMOTE is used for cross-validation but not for the final exported models, so the evaluation and final training procedures differ.
- The notebook does not fix random seeds for SMOTE or the classifiers; repeated runs can differ.
- The workflow does not establish performance on a separate, recent holdout set or demonstrate that related contract bytecodes are kept in separate folds.

## Limitations and troubleshooting

- **Coverage:** static opcode features do not inspect liquidity, ownership activity, transaction history, or token economics. Proxy contracts may expose only proxy bytecode rather than the implementation's behavior.
- **Input validation:** the demo does not verify ERC-20 compliance or reject empty bytecode before scoring. Use a deployed contract on the configured network; results for wallets or empty code are not meaningful.
- **RPC errors:** check the endpoint, credentials, network, and provider limits. Invalid addresses can fail checksum conversion.
- **Missing artifacts:** confirm the working directory is the repository root and all four `weights/` files are present.
- **Model loading errors:** the artifacts use Python pickle and depend on compatible library versions. Load only trusted artifacts; prefer the original model-library versions or retrain and export all artifacts together.
- **New contracts:** the historical disassembler and training data may not represent newer EVM instructions or scam patterns. A prediction is not a security audit.

## Sources and acknowledgments

The original project references Forta's work and labeled datasets:

- [How Forta's predictive ML models detect attacks before exploitation](https://forta.org/blog/how-fortas-predictive-ml-models-detect-attacks-before-exploitation/)
- [Forta malicious smart contract ML starter kit](https://github.com/forta-network/starter-kits/tree/main/malicious-smart-contract-ml-py)
- [Forta labeled datasets](https://github.com/forta-network/labelled-datasets)
- [Forta dataset tutorial](https://docs.forta.network/en/latest/luabase-examples-tutorials/#malicious-smart-contract-detection-dataset)
- [Referenced Forta bot: malicious smart contract detection](https://explorer.forta.network/bot/0x0b241032ca430d9c02eaa6a52d217bbff046f0d1b3f3d2aa928e42a97150ec91)
- [Additional referenced Forta bot](https://explorer.forta.network/bot/0x887678a85e645ad060b2f096812f7c71e3d20ed6ecf5f3acde6e71baa4cf86ad)
