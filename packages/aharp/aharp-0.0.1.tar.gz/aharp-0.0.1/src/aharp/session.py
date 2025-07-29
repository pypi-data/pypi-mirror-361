
import pandas as pd

class Session:
    def __init__(self):
        self.datasets = {}
        self.transcript = []

    def load(self, path, alias):
        df = pd.read_csv(path)
        self.datasets[alias] = df
        self.transcript.append((f"load {path} as {alias}", f"Loaded {alias} ({len(df)} rows, {len(df.columns)} columns)"))

    def ask(self, alias, question):
        df = self.datasets.get(alias)
        if df is None:
            return f"Dataset '{alias}' not found."
        from .tabletalk import ask as TQ
        answer = TQ(df, question)
        self.transcript.append((f"{alias}> {question}", answer))
        return answer

    def export_markdown(self, path):
        with open(path, "w") as f:
            for q,a in self.transcript:
                f.write(f"**Q**: {q}\n**A**: {a}\n\n")

    def export_html(self, path):
        md = []
        for q,a in self.transcript:
            md.append(f"<p><strong>Q:</strong> {q}<br><strong>A:</strong> {a}</p>")
        html = "<html><body>" + "\n".join(md) + "</body></html>"
        with open(path, "w") as f:
            f.write(html)
