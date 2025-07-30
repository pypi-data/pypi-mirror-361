# ScoutML

Scout ML research papers with intelligent agents. A powerful command-line interface for discovering, analyzing, and implementing ML research.

## Installation

```bash
pip install scoutml
```

Or install from source:

```bash
git clone https://github.com/prospectml/scoutml
cd scoutml
pip install -e .
```

## Configuration

Set your API key using one of these methods:

### Option 1: Environment Variable
```bash
export SCOUTML_API_KEY="your-api-key-here"
```

### Option 2: Configuration File
Create a `.env` file in your working directory:
```
SCOUTML_API_KEY=your-api-key-here
```

### Option 3: CLI Configuration Command
```bash
scoutml configure --api-key your-api-key-here
```

## Quick Start

```bash
# Search for papers
scoutml search "transformer models computer vision" --limit 10

# Get implementation guide for a paper
scoutml agent implement 2010.11929 --framework pytorch

# Compare multiple papers
scoutml compare 1810.04805 2005.14165 1910.10683

# Generate a literature review
scoutml review "few-shot learning" --year-min 2020

# Find similar papers
scoutml similar --paper-id 1810.04805 --limit 5
```

## Commands Overview

### Search Commands

#### `search` - Semantic Search
Search papers using natural language queries with advanced filtering.

```bash
scoutml search "your query" [OPTIONS]

Options:
  --limit INTEGER          Number of results (default: 20)
  --year-min INTEGER       Minimum publication year
  --year-max INTEGER       Maximum publication year
  --min-citations INTEGER  Minimum citation count
  --venue TEXT            Filter by venue (e.g., "CVPR", "NeurIPS")
  --sota-only             Only show state-of-the-art papers
  --domain TEXT           Filter by domain (e.g., "computer vision")
  --output FORMAT         Output format: table/json/csv (default: table)
  --export PATH           Export results to file

Example:
  scoutml search "vision transformers" --year-min 2021 --sota-only
```

#### `method-search` - Search by Method
Find papers using specific methods or techniques.

```bash
scoutml method-search METHOD [OPTIONS]

Options:
  --limit INTEGER      Number of results (default: 20)
  --sort-by TEXT      Sort by: citations/year/novelty (default: citations)
  --year-min INTEGER  Minimum year
  --year-max INTEGER  Maximum year
  --output FORMAT     Output format: table/json/csv

Example:
  scoutml method-search "BERT" --sort-by citations --limit 10
```

#### `dataset-search` - Search by Dataset
Find papers that use specific datasets.

```bash
scoutml dataset-search DATASET [OPTIONS]

Options:
  --limit INTEGER               Number of results (default: 20)
  --include-benchmarks          Include benchmark results
  --no-benchmarks              Exclude benchmark results
  --year-min INTEGER           Minimum year
  --year-max INTEGER           Maximum year
  --output FORMAT              Output format: table/json/csv

Example:
  scoutml dataset-search "ImageNet" --include-benchmarks --year-min 2020
```

### Paper Analysis Commands

#### `paper` - Get Paper Details
Get detailed information about a specific paper.

```bash
scoutml paper ARXIV_ID [OPTIONS]

Options:
  --similar/--no-similar    Include similar papers (default: no)
  --similar-limit INTEGER   Number of similar papers (default: 5)

Example:
  scoutml paper 1810.04805 --similar --similar-limit 10
```

#### `compare` - Compare Papers
AI-powered comparison of multiple papers.

```bash
scoutml compare PAPER_ID1 PAPER_ID2 [PAPER_ID3...] [OPTIONS]

Options:
  --from-file PATH    Read paper IDs from file (one per line)
  --output FORMAT     Output format: rich/json/markdown (default: rich)

Example:
  scoutml compare 1810.04805 2005.14165 1910.10683 --output markdown
```

#### `similar` - Find Similar Papers
Find papers similar to a given paper or abstract.

```bash
scoutml similar [OPTIONS]

Options:
  --paper-id TEXT         ArXiv ID of source paper
  --abstract TEXT         Abstract text to match
  --abstract-file PATH    File containing abstract
  --limit INTEGER         Number of results (default: 10)
  --threshold FLOAT       Similarity threshold 0-1 (default: 0.7)
  --output FORMAT         Output format: table/json

Example:
  scoutml similar --paper-id 1810.04805 --limit 20
  scoutml similar --abstract "We propose a new method for..." --threshold 0.8
```

### Research Synthesis Commands

#### `review` - Generate Literature Review
Generate an AI-synthesized literature review on a topic.

```bash
scoutml review TOPIC [OPTIONS]

Options:
  --year-min INTEGER       Minimum year
  --year-max INTEGER       Maximum year
  --min-citations INTEGER  Minimum citations (default: 0)
  --limit INTEGER         Max papers to analyze (default: 50)
  --output FORMAT         Output format: rich/markdown/json
  --export PATH           Export review to file

Example:
  scoutml review "few-shot learning" --year-min 2020 --limit 100 --export review.md
```

### Intelligent Agent Commands

#### `agent implement` - Implementation Guide
Generate a step-by-step implementation guide for a paper.

```bash
scoutml agent implement ARXIV_ID [OPTIONS]

Options:
  --framework CHOICE     Target framework: pytorch/tensorflow/jax/other (default: pytorch)
  --level CHOICE        Experience level: beginner/intermediate/advanced (default: intermediate)
  --output FORMAT       Output format: rich/json (default: rich)

Example:
  scoutml agent implement 2010.11929 --framework pytorch --level intermediate
```

#### `agent critique` - Research Critique
Get comprehensive research critique and peer review analysis.

```bash
scoutml agent critique ARXIV_ID [OPTIONS]

Options:
  --aspects TEXT        Aspects to critique (can specify multiple):
                       methodology/experiments/claims/reproducibility
  --output FORMAT      Output format: rich/json

Example:
  scoutml agent critique 1810.04805 --aspects methodology --aspects experiments
```

#### `agent solve-limitations` - Limitation Solver
Get solutions for paper limitations with practical approaches.

```bash
scoutml agent solve-limitations ARXIV_ID [OPTIONS]

Options:
  --focus TEXT         Specific limitation to focus on
  --tradeoffs TEXT     Acceptable tradeoffs (can specify multiple):
                      accuracy/speed/memory/complexity/data_requirements/quality
  --output FORMAT     Output format: rich/json

Example:
  scoutml agent solve-limitations 1810.04805 --focus computational --tradeoffs speed
```

#### `agent design-experiment` - Experiment Designer
Design experiments to validate or extend research hypotheses.

```bash
scoutml agent design-experiment BASE_PAPER HYPOTHESIS [OPTIONS]

Options:
  --gpu-hours INTEGER    Available GPU hours
  --datasets TEXT        Available datasets (can specify multiple)
  --output FORMAT        Output format: rich/json

Example:
  scoutml agent design-experiment 2010.11929 "ViT works on small datasets with augmentation" \
    --gpu-hours 100 --datasets CIFAR-10 --datasets CIFAR-100
```

### Research Intelligence Commands

#### `insights reproducibility` - Reproducibility Analysis
Analyze papers ranked by reproducibility score.

```bash
scoutml insights reproducibility [OPTIONS]

Options:
  --domain TEXT        Filter by domain
  --year-min INTEGER   Minimum year
  --year-max INTEGER   Maximum year
  --limit INTEGER      Number of results (default: 20)
  --output FORMAT      Output format: rich/json/csv

Example:
  scoutml insights reproducibility --domain "computer vision" --year-min 2021
```

#### `insights compute` - Compute Requirements Analysis
Analyze GPU/compute trends across papers.

```bash
scoutml insights compute [OPTIONS]

Options:
  --method TEXT        Filter by method/technique
  --year-min INTEGER   Minimum year
  --year-max INTEGER   Maximum year
  --output FORMAT      Output format: rich/json/csv

Example:
  scoutml insights compute --method transformer --year-min 2020
```

#### `insights funding` - Funding Analysis
Analyze funding sources and their impact.

```bash
scoutml insights funding [OPTIONS]

Options:
  --institution TEXT   Filter by institution
  --source TEXT       Filter by funding source
  --year-min INTEGER  Minimum year
  --year-max INTEGER  Maximum year
  --limit INTEGER     Number of top sources (default: 20)
  --output FORMAT     Output format: rich/json/csv

Example:
  scoutml insights funding --source NSF --institution MIT
```

## Advanced Examples

### Complex Search with Multiple Filters
```bash
# Find recent SOTA transformer papers in computer vision
scoutml search "vision transformer" \
  --year-min 2022 \
  --min-citations 50 \
  --sota-only \
  --domain "computer vision" \
  --venue "CVPR" \
  --export sota_transformers.json
```

### Complete Paper Analysis Pipeline
```bash
# 1. Find a paper
scoutml search "BERT" --limit 1

# 2. Get implementation guide
scoutml agent implement 1810.04805 --framework pytorch

# 3. Get research critique
scoutml agent critique 1810.04805

# 4. Find and compare similar papers
scoutml similar --paper-id 1810.04805 --limit 3 > similar_ids.txt
scoutml compare 1810.04805 1906.08237 1907.11692
```

### Literature Review Workflow
```bash
# Generate comprehensive review with export
scoutml review "federated learning privacy" \
  --year-min 2020 \
  --year-max 2024 \
  --min-citations 20 \
  --limit 75 \
  --output markdown \
  --export federated_learning_review.md
```

### Batch Processing
```bash
# Create a file with ArXiv IDs
cat > papers.txt << EOF
1810.04805
2005.14165
1910.10683
2010.11929
EOF

# Compare all papers
scoutml compare --from-file papers.txt --output markdown > comparison.md

# Get implementation guides for all
while read -r paper_id; do
  echo "=== Implementation guide for $paper_id ===" >> implementations.txt
  scoutml agent implement "$paper_id" --output json >> implementations.txt
done < papers.txt
```

## Output Formats

- **table** (default): Rich terminal tables with colors and formatting
- **json**: Structured JSON for programmatic use
- **csv**: Comma-separated values for spreadsheet analysis
- **markdown**: Formatted markdown for documentation
- **rich**: Enhanced terminal output with panels and formatting

## Tips and Best Practices

1. **API Key Security**: Never commit your API key to version control. Use environment variables or `.env` files.

2. **Efficient Searching**: Start with broader queries and use filters to narrow results rather than overly specific initial queries.

3. **Batch Operations**: When analyzing multiple papers, use `--from-file` options or shell scripts for efficiency.

4. **Output Formats**: Use `--output json` when piping to other tools or for programmatic processing.

5. **Export Results**: Use `--export` to save results for later analysis or sharing.

## Error Messages

The CLI provides helpful error messages:

- **Missing API Key**: Clear instructions on how to set your API key
- **Invalid Paper ID**: Suggests checking the ArXiv ID format
- **No Results Found**: Suggests broadening search terms or adjusting filters
- **Rate Limiting**: Shows when to retry the request

## Support

- Documentation: https://docs.scoutml.com
- Issues: https://github.com/prospectml/scoutml/issues
- Email: support@prospectml.com

## License


MIT License - see [LICENSE](LICENSE) file.