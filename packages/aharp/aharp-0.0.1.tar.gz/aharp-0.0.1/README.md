# AHARP

**A**nalytics & **H**istory **A**uto-**R**eport **P**rinter

AHARP is a free, offline Python toolkit for exploring one or more tabular datasets using natural-language queries.  Under the hood, it leverages Pandas, NumPy, and a lightweight fuzzy‐matching layer to give you:

- **Multi-dataset sessions**: load multiple CSVs (e.g. `load sales.csv as sales`)
- **Exportable reports**: transcript → Markdown or HTML
- **Time-series awareness**: resample, rolling avg, line plots
- **Fuzzy matching**: tolerate typos (`nulll`→`null`)

## 📦 Installation

```bash
cd aharp
pip install -e ".[full]"
```

## 🚀 CLI Usage

```bash
python -m aharp sample_data/people.csv
```

**Commands**:

- `load FILE.csv as ALIAS` — load another dataset
- `ask ALIAS question` or just type a question if only one dataset is loaded
- `export markdown report.md`
- `export html report.html`
- `help`
- `exit`

## 📝 Examples

```bash
aharp> load sample_data/products.csv as products
aharp> ask main mean of income
aharp> ask products most common product
aharp> type of age
aharp> plot date vs sales
aharp> export markdown session.md
aharp> exit
```

## 📊 Time-Series Commands

- `ask main resample date by month`
- `rolling average of temperature over 7 days`
- `plot date vs sales` (line chart)

---

## ❓ Supported Question Categories

### Dataset Shape

- How many rows?
- Number of rows?
- Row count
- How many columns?
- Column count

### Schema & Types

- What are the column types?
- Type of each column
- What type is `age`?
- Describe column types
- Schema summary
- Show data structure
- Dataset info

### Missing / Nulls

- Any missing data?
- Are there nulls?
- Missing values?
- Null counts?
- How many nulls per column?
- Which columns have missing?

### Zero Values

- Count zeros in column
- Zero values in inventory?
- How many zeros?
- Zero count

### Statistical Summaries

- Top / Mode values
- Mean / Average / Compute mean
- Median / Std / Standard deviation
- Range / Min & Max
- Unique / Distinct counts
- Sample values / Examples

### Viewing & Exporting Rows

- Show sample rows
- Show top 5 rows / Head
- Show last rows / Tail
- Any duplicates? / Duplicate count
- Drop duplicates / Remove duplicate rows

### Time-Series & Plots

- Plot `age` vs `income`
- Create scatter of `price` vs `inventory`
- Plot distribution / Histogram / Bar chart / Pie chart

### Advanced

- Find rows where `city` = NY
- Search column `city` for LA
- Favorite column?

## 🧪 Run Tests

```bash
pytest
```

## 🚩 Sample Data

- `sample_data/people.csv`
- `sample_data/products.csv`
