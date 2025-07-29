
import pandas as pd
from aharp import ask

df = pd.DataFrame({
    'age': [20, 30, 40, 50],
    'income': [2000, 3000, 4000, 5000],
    'city': ['NY', 'LA', 'NY', 'SF']
})

def test_null_variants():
    assert 'No missing values' in ask(df, 'null?')
    assert 'No missing values' in ask(df, 'Null')

def test_scoped_type_and_top():
    assert 'age: int64' == ask(df, 'what type is age')
    assert 'city: NY' == ask(df, 'most common city')

def test_direct_ask_default():
    # simulate CLI default dataset
    # here ask('', ...) is direct, so we test underlying ask
    assert '4 rows' == ask(df, 'how many rows')

