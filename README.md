# Metabolic Health and Sleep Cross Analysis

Sleep, or lack of, can highly impact your metabolic health.
If you track your sleep with Whoop and glucose with Levels, 
this [app](https://share.streamlit.io/jbpauly/glucose-sleep-analysis/main/src/app.py) 
enables you to cross analyze your sleep metrics glucose data.

## Try it out!
1. [Launch the app](https://share.streamlit.io/jbpauly/glucose-sleep-analysis/main/src/app.py)
2. Download your [Freestyle Libre glucose data](https://www.libreview.com/)
3. Download your [Whoop sleep summary data](https://docs.google.com/spreadsheets/d/1q9tU4tkBLUi6oFsdLsO9HnOuMC-TEkrBXNoNXvLQt3Q/edit#gid=1913656685)
    - Follow the [How To video](https://www.youtube.com/watch?v=x19G39cXkoM)
    - Download **only** the 'Whoop' sheet as a CSV

#### Learn more about the [Whoop api](https://github.com/pelo-tech/whoop-api-spec)
Thank you [Pelo-Tech](https://github.com/pelo-tech) and [DovOps](https://github.com/DovOps)
for creating the api and GUI!

## How to run in your own environment
The app requires Python 3.7. **Create a new virtual environment**, then run:

```
git clone https://github.com/jbpauly/glucose-sleep-analysis.git
cd glucose-sleep-analysis
pip install -r requirements.txt
cd src
streamlit run main.py
```

## Roadmap
1. Close out code coverage with tests.
2. Integrate with [whoop-api-spec](https://github.com/pelo-tech/whoop-api-spec) 
so users can request Whoop sleep data directly from app instead using the [google-sheet GUI](https://docs.google.com/spreadsheets/d/1q9tU4tkBLUi6oFsdLsO9HnOuMC-TEkrBXNoNXvLQt3Q/edit#gid=1913656685)
3. Add option to download analysis dataset.
4. Add data dictionary and clean up parameter names.

## Questions, comments, or suggestions?
This app new and will likely break at some point. 
It has not be tested with a large number of unique datasets,
Please let me know if you run into problems by submitting an [Issue](https://github.com/jbpauly/glucose-sleep-analysis/issues)