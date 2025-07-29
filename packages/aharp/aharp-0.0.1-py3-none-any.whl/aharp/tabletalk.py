import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import random
from rapidfuzz import process, fuzz

def analyze(df):
    stats = {}
    for col in df.columns:
        d = df[col]
        zero_cnt = int((d == 0).sum()) if pd.api.types.is_numeric_dtype(d) else None
        stats[col] = {
            "dtype":    str(d.dtype),
            "nulls":    int(d.isnull().sum()),
            "unique":   int(d.nunique()),
            "top":      d.mode().iloc[0] if not d.mode().empty else None,
            "min":      d.min()    if pd.api.types.is_numeric_dtype(d) else None,
            "max":      d.max()    if pd.api.types.is_numeric_dtype(d) else None,
            "mean":     d.mean()   if pd.api.types.is_numeric_dtype(d) else None,
            "median":   d.median() if pd.api.types.is_numeric_dtype(d) else None,
            "std":      d.std()    if pd.api.types.is_numeric_dtype(d) else None,
            "zeros":    zero_cnt,
            "sample":   d.dropna().unique()[:3].tolist()
        }
    return stats

# ——————————————————— Q_* handlers ———————————————————

def Q_rows(df,s):   return f"{len(df)} rows"
def Q_cols(df,s):   return f"{len(df.columns)} columns"

def Q_types(df,s):
    return "\n".join(f"{c}: {s[c]['dtype']}" for c in s)

def Q_missing(df,s):
    lines = [f"{c}: {s[c]['nulls']} nulls" for c in s if s[c]['nulls']>0]
    return "\n".join(lines) if lines else "No missing values"

def Q_zeros(df,s):
    lines = [f"{c}: {s[c]['zeros']} zeros" for c in s if s[c]['zeros']]
    return "\n".join(lines) if lines else "No zero values"

def Q_top(df,s):
    return "\n".join(f"{c}: {s[c]['top']}" for c in s)

def Q_mean(df,s):
    return "\n".join(f"{c}: {s[c]['mean']:.2f}" for c in s if s[c]['mean'] is not None)

def Q_median(df,s):
    return "\n".join(f"{c}: {s[c]['median']:.2f}" for c in s if s[c]['median'] is not None)

def Q_std(df,s):
    return "\n".join(f"{c}: {s[c]['std']:.2f}" for c in s if s[c]['std'] is not None)

def Q_range(df,s):
    return "\n".join(f"{c}: {s[c]['min']} to {s[c]['max']}" for c in s if s[c]['min'] is not None)

def Q_unique(df,s):
    return "\n".join(f"{c}: {s[c]['unique']} unique" for c in s)

def Q_sample(df,s):
    return "\n".join(f"{c}: {s[c]['sample']}" for c in s)

def Q_describe(df,s):
    return "\n".join(
        f"{c}: type={s[c]['dtype']}, nulls={s[c]['nulls']}, unique={s[c]['unique']}"
        for c in s
    )

def Q_head(df,s):
    return df.head().to_string(index=False)

def Q_tail(df,s):
    return df.tail().to_string(index=False)

def Q_duplicates(df,s):
    dup = df.duplicated().sum()
    return f"{dup} duplicate rows"

def Q_drop(df,s):
    before = len(df)
    after = len(df.drop_duplicates())
    return f"Dropped {before-after} duplicates"

def Q_favorite(df,s):
    col = random.choice(list(s.keys()))
    return f"My favorite column is '{col}'!"

def Q_search(df,s,col,term):
    if col not in df.columns:
        return f"Column '{col}' not found."
    mask = df[col].astype(str).str.contains(term, case=False, na=False)
    return df[mask].to_string(index=False) if mask.any() else f"No matches for '{term}' in '{col}'"

def Q_resample(df,s,date_col,freq):
    df2 = df.copy()
    df2[date_col] = pd.to_datetime(df2[date_col])
    res = df2.resample(freq.upper(), on=date_col).mean()
    return res.to_string()

def Q_rolling(df,s,col,window):
    if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
        return f"Cannot do rolling average on '{col}'"
    roll = df[col].rolling(window=int(window)).mean()
    return roll.to_string(index=False)

def Q_bar(df,s,col):
    if col not in df.columns:
        return f"Column '{col}' not found."
    vc = df[col].value_counts()
    vc.plot(kind="bar", title=f"Bar chart of {col}")
    fname = f"{col}_bar.png"
    plt.savefig(fname); plt.close()
    return f"Plot saved as {fname}"

def Q_pie(df,s,col):
    if col not in df.columns:
        return f"Column '{col}' not found."
    vc = df[col].value_counts()
    vc.plot(kind="pie", autopct="%1.1f%%", title=f"Pie chart of {col}")
    fname = f"{col}_pie.png"
    plt.savefig(fname); plt.close()
    return f"Plot saved as {fname}"

def Q_hist(df,s,col):
    if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
        return f"Cannot plot histogram for '{col}'"
    df[col].plot(kind="hist", title=f"Histogram of {col}")
    fname = f"{col}_hist.png"
    plt.savefig(fname); plt.close()
    return f"Plot saved as {fname}"

def Q_art(df, s):
    # pick a fun emoji/snippet based on dataset size or random
    arts = [
        "(\\_/)\n(•_•)\n/ >🍪",                # bunny cookie
        "🐍 Python says hi!",
        "¯\\_(ツ)_/¯",                        # shrug
        "📊📈📉 Data vibes!",                 # chart emojis
        "  _\n (°v°)\n<( )> Data Bird!",     # little ASCII bird
    ]
    return random.choice(arts)

# ——————————————————— Intent mapping & matching ———————————————————

PRESET = {
    "rows": Q_rows, "row count": Q_rows,
    "columns": Q_cols, "column count": Q_cols,
    "types": Q_types, "data types": Q_types,
    "missing": Q_missing, "nulls": Q_missing, "null": Q_missing,
    "zeros": Q_zeros, "zeroes": Q_zeros, "zero count": Q_zeros,
    "mode": Q_top, "top": Q_top, "most common": Q_top, "most frequent": Q_top,
    "mean": Q_mean, "average": Q_mean,
    "median": Q_median,
    "std": Q_std, "standard deviation": Q_std,
    "range": Q_range, "min": Q_range, "max": Q_range,
    "unique": Q_unique, "distinct": Q_unique,
    "sample": Q_sample, "example": Q_sample,
    "describe": Q_describe, "summary": Q_describe,
    "schema": Q_describe, "overview": Q_describe, "info": Q_describe,
    "head": Q_head, "show top 5": Q_head, "first rows": Q_head,
    "tail": Q_tail, "show last rows": Q_tail, "last rows": Q_tail,
    "duplicates": Q_duplicates, "duplicate count": Q_duplicates,
    "drop duplicates": Q_drop, "remove duplicate rows": Q_drop,
    "favorite column": Q_favorite, "favourite column": Q_favorite,
}

def match_intent(q):
    keys = list(PRESET.keys())
    match, score, _ = process.extractOne(q, keys, scorer=fuzz.partial_ratio)
    return match if score > 60 else None

# ——————————————————— The master ask() ———————————————————

def ask(df, question):
    user_q = re.sub(r"[^\w\s=]", "", question).strip().lower()
    stats = analyze(df)

    # Easter eggs & greetings
    if user_q == "i love you":
        return "I love you"
    if user_q == "happy birthday":
        return "Happy birthday!"
    if re.search(r"\b(hi|hello|hey|greetings)\b", user_q):
        return random.choice([
            "Hello! How can I help with your data?",
            "Hi there! Ready to explore?",
            "Hey! What data question do you have?"
        ])
    if "burrito recipe" in user_q:
        return (
            "Burrito Recipe:\n"
            "- 1 lb protein + taco seasoning\n"
            "- 1 cup rice, 1 can beans\n"
            "- Tortillas + cheese\n"
            "Cook, assemble & roll. Enjoy!"
        )

    # Missing/null
    if re.search(r"\bmissing\b|\bnulls?\b", user_q):
        return Q_missing(df, stats)

    # Type-of-column
    m = re.search(r"\btype (?:of|is) (\w+)\b", user_q)
    if m and m.group(1) in stats:
        return f"{m.group(1)}: {stats[m.group(1)]['dtype']}"

    # Most-common mode
    m2 = re.search(r"\bmost (?:common|frequent) (\w+)\b", user_q)
    if m2 and m2.group(1) in stats:
        return f"{m2.group(1)}: {stats[m2.group(1)]['top']}"

    # Head / Tail
    if re.search(r"\b(show top 5 rows|head|first rows)\b", user_q):
        return Q_head(df, stats)
    if re.search(r"\b(show last rows|tail|last rows)\b", user_q):
        return Q_tail(df, stats)

    # Duplicates / Drop duplicates
    if re.search(r"\b(drop duplicates|remove duplicate rows)\b", user_q):
        return Q_drop(df, stats)
    if re.search(r"\b(any duplicates|duplicate count|count duplicates|check duplicates)\b", user_q):
        return Q_duplicates(df, stats)

    # Find rows where col=val
    m7 = re.search(r"\bfind rows where (\w+)\s*=\s*(\w+)\b", user_q)
    if m7:
        return Q_search(df, stats, m7.group(1), m7.group(2))

    # Search column for term
    m8 = re.search(r"(?:find|search) (\w+) (?:for|=) (.+)", user_q)
    if m8:
        return Q_search(df, stats, m8.group(1), m8.group(2))

    # Resample time-series
    m_res = re.search(r"\bresample (\w+) by (\w+)\b", user_q)
    if m_res:
        return Q_resample(df, stats, m_res.group(1), m_res.group(2))

    # Rolling average
    m_roll = re.search(r"\brolling (?:avg|average) of (\w+)(?: over (\d+) days)?\b", user_q)
    if m_roll:
        window = int(m_roll.group(2)) if m_roll.group(2) else 3
        return Q_rolling(df, stats, m_roll.group(1), window)

    # Scatter variations
    m_sc = re.search(r"\b(?:scatter|create scatter) (\w+) vs (\w+)\b", user_q)
    if m_sc:
        return ask(df, f"plot {m_sc.group(1)} vs {m_sc.group(2)}")

    # Histogram / Distribution
    m_hist = re.search(r"\b(histogram|distribution)(?: of)? (\w+)\b", user_q)
    if m_hist:
        return Q_hist(df, stats, m_hist.group(2))

    # Bar chart
    m_bar = re.search(r"\bbar(?: chart)? of (\w+)\b", user_q)
    if m_bar:
        return Q_bar(df, stats, m_bar.group(1))

    # Pie chart
    m_pie = re.search(r"\bpie(?: chart)? of (\w+)\b", user_q)
    if m_pie:
        return Q_pie(df, stats, m_pie.group(1))

    # Generic plot X vs Y
    m11 = re.search(r"\bplot (\w+) vs (\w+)\b", user_q)
    if m11:
        x, y = m11.group(1), m11.group(2)
        if x in df.columns and y in df.columns and pd.api.types.is_numeric_dtype(df[x]) and pd.api.types.is_numeric_dtype(df[y]):
            plt.scatter(df[x], df[y])
            plt.xlabel(x)
            plt.ylabel(y)
            plt.title(f"Scatter plot of {x} vs {y}")
            fname = f"{x}_vs_{y}_scatter.png"
            plt.savefig(fname)
            plt.close()
            return f"Scatter plot saved as {fname}"
        else:
            return f"Cannot plot scatter for '{x}' vs '{y}'"

    # 16) Fuzzy intent mapping
    intent = match_intent(user_q)
    if intent:
        return PRESET[intent](df, stats)
        
    # Search a column for a value (e.g. “search city for LA”)
    m_search = re.search(r"\bsearch (\w+) for (.+)", user_q)
    if m_search:
        col, term = m_search.group(1), m_search.group(2)
        return Q_search(df, stats, col, term)

    # Plot distribution / histogram
    m_dist = re.search(r"\b(?:distribution|histogram) (?:of )?(\w+)\b", user_q)
    if m_dist:
        return Q_hist(df, stats, m_dist.group(1))

    # Bar chart
    m_bar = re.search(r"\bbar(?: chart)? of (\w+)\b", user_q)
    if m_bar:
        return Q_bar(df, stats, m_bar.group(1))

    # Pie chart
    m_pie = re.search(r"\bpie(?: chart)? of (\w+)\b", user_q)
    if m_pie:
        return Q_pie(df, stats, m_pie.group(1))

    # ASCII/Emoji art Easter egg
    if re.search(r"\b(ascii art|emoji art|show me art)\b", user_q):
        return Q_art(df, stats)
    
    # Fallback full describe
    return Q_art(df, stats)

