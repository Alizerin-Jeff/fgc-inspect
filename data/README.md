# Data

This directory should contain `attacks.jsonl`, the same 682-row dataset used in the FGC experiment.

Two ways to populate it:

1. **Copy from FGC** (fastest):
   ```bash
   cp ../filter-generator-complementarity/data/attacks.jsonl ./attacks.jsonl
   ```

2. **Regenerate from JailbreakBench** (cleaner, makes this repo standalone):
   ```bash
   uv run -m data.build_dataset
   ```
   This requires porting the `build_dataset.py` from FGC. Do this if you plan to share fgc-inspect as a standalone repo.

The file is gitignored. Each row is a JSON object with a `prompt_text` string, a `prompt_id`, an `is_benign` flag, and `attack_algorithm` / `harm_category` / `source` labels — see FGC's `src/schema.py` for the full `Prompt` model.
