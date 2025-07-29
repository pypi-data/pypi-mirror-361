
import os
import pandas as pd
from aharp.session import Session

def test_load_and_ask(tmp_path):
    # create temp CSV
    df = pd.DataFrame({'x':[1,2],'y':[3,4]})
    file = tmp_path / "t.csv"
    df.to_csv(file, index=False)
    s = Session()
    s.load(str(file), 't')
    assert 't' in s.datasets
    resp = s.ask('t', 'how many rows')
    assert '2 rows' in resp

def test_export(tmp_path):
    s = Session()
    s.transcript = [('Q','A')]
    md = tmp_path / "r.md"
    s.export_markdown(str(md))
    assert md.read_text().startswith("**Q**:")
    html = tmp_path / "r.html"
    s.export_html(str(html))
    assert "<strong>Q:</strong>" in html.read_text()
