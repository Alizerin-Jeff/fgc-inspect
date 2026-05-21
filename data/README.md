# Data

This directory should contain `attacks.jsonl`, the same 682-row dataset used in the FGC experiment.

Two ways to populate it:

1. **Copy from FGC** (fastest):

   Can use the Filter-Generator_Repository, which has the same dataset.

   ```bash
   git clone https://github.com/Alizerin-Jeff/filter-generator-complementarity.git
   ```

2. **Regenerate from JailbreakBench** (cleaner, makes this repo standalone):
   ```bash
   uv run -m data.generate_data.py
   ```
   This will generate a fresh JSONL file.  While this likely will be the same as FGC, 
   updates to the JailBreakBench artifacts can change it over time.

Each row is a JSON object with a `prompt_text` string, a `prompt_id`, an `is_benign` flag, and `attack_algorithm` / `harm_category` / `source` labels — see `schema.py` for the full `Prompt` model.
