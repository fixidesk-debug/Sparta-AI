import pandas as pd
from app.services.data_cleaner import DataCleaner


def test_clean_text_basic():
    df = pd.DataFrame({'text': [" Hello \n World "]})
    cleaner = DataCleaner()
    out = cleaner.clean_text(df, columns=['text'], lowercase=True, strip_whitespace=True)
    # Expected: leading/trailing whitespace removed and text lowercased
    assert out['text'].iloc[0] == 'hello \n world'
