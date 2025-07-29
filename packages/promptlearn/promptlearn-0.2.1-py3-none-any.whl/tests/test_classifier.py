import pandas as pd
from promptlearn import PromptClassifier
import numbers


def test_zero_row_classifier_runs():
    X = pd.DataFrame(columns=["country_name"])
    y = pd.Series(name="has_blue_in_flag", dtype=int)

    clf = PromptClassifier(verbose=True)
    clf.fit(X, y)

    result = clf.predict(pd.DataFrame([{"country_name": "France"}]))
    assert isinstance(result[0], numbers.Integral)
