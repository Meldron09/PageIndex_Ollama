# PageIndex_Ollama

A document indexing tool that processes PDFs and Markdown files to generate hierarchical tree structures for intelligent retrieval using LLMs.

## Features

- PDF document indexing with table-of-contents extraction and concurrent title verification
- Markdown document parsing with tree structure generation
- Tree thinning for Markdown (merges small nodes to reduce complexity)
- Configurable LLM-based title verification and summary generation
- Context-aware retrieval for question answering
- Support for both OpenAI GPT and Ollama models (deepseek-r1, etc.)
- Configurable output options (node IDs, summaries, document description, text content)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config/config.yaml` to customize:

- Default model (GPT-4o or Ollama models like deepseek-r1:8b)
- Page/token limits for node processing
- Output options (node IDs, summaries, document description)

## Usage

### Index a PDF

```bash
python -m scripts.run_pageindex --pdf_path data/document.pdf
```

### Index a Markdown file

```bash
python -m scripts.run_pageindex --md_path data/document.md
```

### Query a document

```bash
python -m scripts.retrieval --md data/document.md --tree results/document_structure.json --query "What is..."
```

## CLI Options

### Common Options

| Option | Default | Description |
|--------|---------|-------------|
| `--model` | `gpt-4o-2024-11-20` | Model to use (OpenAI or Ollama) |
| `--if-add-node-id` | `yes` | Whether to add node ID to each node |
| `--if-add-node-summary` | `yes` | Whether to add summary to each node |
| `--if-add-doc-description` | `no` | Whether to add document-level description |
| `--if-add-node-text` | `no` | Whether to include text content in nodes |

### PDF Options

| Option | Default | Description |
|--------|---------|-------------|
| `--pdf_path` | - | Path to the PDF file (required) |
| `--toc-check-pages` | `20` | Number of pages to check for table of contents |
| `--max-pages-per-node` | `10` | Maximum number of pages per node |
| `--max-tokens-per-node` | `20000` | Maximum number of tokens per node |

### Markdown Options

| Option | Default | Description |
|--------|---------|-------------|
| `--md_path` | - | Path to the Markdown file (required) |
| `--if-thinning` | `no` | Whether to apply tree thinning |
| `--thinning-threshold` | `5000` | Minimum token threshold for tree thinning |
| `--summary-token-threshold` | `200` | Token threshold for generating summaries |

### Example: Markdown with Tree Thinning

```bash
python scripts/run_pageindex.py \
  --md_path data/document.md \
  --if-thinning yes \
  --thinning-threshold 3000 \
  --summary-token-threshold 150
```

### Example: Using Ollama Model

```bash
python scripts/run_pageindex.py \
  --md_path data/document.md \
  --model deepseek-r1:8b
```

## Output Format

The indexed documents are saved as JSON with the following structure:

```json
{
  "doc_name": "document",
  "structure": [
    {
      "title": "Section Title",
      "node_id": "node_001",
      "summary": "Brief summary of the section",
      "prefix_summary": "Summary of preceding content",
      "text": "Full text content (if enabled)",
      "line_num": 1,
      "nodes": [
        {
          "title": "Subsection",
          "node_id": "node_001_001",
          "summary": "...",
          "nodes": []
        }
      ]
    }
  ]
}
```

## Project Structure

```
.
├── pageindex/          # Main package source
│   ├── page_index.py   # PDF indexing with TOC extraction
│   ├── page_index_md.py # Markdown parsing with tree generation
│   └── utils.py        # Shared utilities (LLM calls, JSON helpers)
├── config/             # Configuration files
├── scripts/            # CLI entry points
│   ├── run_pageindex.py # Indexing CLI
│   └── retrieval.py     # Query CLI
├── data/               # Sample documents
├── tests/              # Test suite
├── logs/               # Processing logs
└── results/            # Generated JSON outputs
```

## Dependencies

See `requirements.txt`

## License
