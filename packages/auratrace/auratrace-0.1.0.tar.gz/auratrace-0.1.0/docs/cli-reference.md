# CLI Reference

This guide documents all command-line interface (CLI) commands for [AuraTrace](https://github.com/Cosmos-Coder-Ray/AuraTrace.git).

## Usage

```bash
auratrace [COMMAND] [OPTIONS]
```

## Commands

### `run`
Trace and analyze a Python script or pipeline.

```bash
auratrace run script.py [--output OUTPUT] [--quality-rules RULES] [--verbose]
```

- `script.py`: Path to your Python script.
- `--output, -o`: Output file for the report (optional).
- `--quality-rules, -q`: Path to a YAML file with quality rules (optional).
- `--verbose, -v`: Enable verbose output.

**Example:**
```bash
auratrace run examples/simple_pipeline.py --output results.json
```

---

### `view`
View the results and lineage of a run.

```bash
auratrace view [SESSION_ID or session.json] [--output OUTPUT]
```

- `SESSION_ID` or `session.json`: Session file or ID to view.
- `--output, -o`: Output file for visualization (optional).

**Example:**
```bash
auratrace view session.json
```

---

### `ask`
Ask the AI assistant a question about your pipeline.

```bash
auratrace ask [SESSION_ID or session.json] "Your question" [--provider PROVIDER] [--model MODEL] [--api-key API_KEY]
```

- `SESSION_ID` or `session.json`: Session file or ID to analyze.
- `"Your question"`: The question to ask.
- `--provider`: LLM provider (openai, huggingface, custom, local, user).
- `--model`: Model name or path.
- `--api-key`: API key for the provider.

**Example:**
```bash
auratrace ask session.json "What operations were performed?" --provider huggingface --model mistralai/Mistral-7B-Instruct-v0.2
```

---

### `check`
Check data quality using a set of rules.

```bash
auratrace check script.py --quality-rules rules.yml
```

- `script.py`: Path to your Python script.
- `--quality-rules, -q`: Path to a YAML file with quality rules.

**Example:**
```bash
auratrace check examples/simple_pipeline.py --quality-rules examples/quality_rules.yml
```

---

### `compare`
Compare two pipeline runs to detect drift and changes.

```bash
auratrace compare --run-a RUN_A --run-b RUN_B
```

- `--run-a, -a`: First run to compare (session ID or 'latest').
- `--run-b, -b`: Second run to compare (session ID or 'previous').

**Example:**
```bash
auratrace compare --run-a session1.json --run-b session2.json
```

---

### `init`
Initialize AuraTrace configuration in your project.

```bash
auratrace init
```

Creates a default configuration file and sample quality rules.

---

## Tips
- Use `--help` with any command for detailed options.
- All commands support both file paths and session IDs.
- For more, see the [GitHub repo](https://github.com/Cosmos-Coder-Ray/AuraTrace.git). 