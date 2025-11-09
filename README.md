\# Skin Disease Treatment Advisor



AI-powered treatment suggestions for skin diseases.



\## Setup

1\. Clone repo

2\. `pip install -r requirements.txt`

3\. Add API keys to `.env` file

4\. Run `python skin\_disease\_helper.py`



\## Usage

```python

from skin\_disease\_helper import SkinDiseaseHelper



helper = SkinDiseaseHelper()

result = helper.complete\_analysis("Eczema", 89.5, "Mysuru")

print(result\['treatment\_advice']\['advice'])

```



\## Features

\- Treatment advice for ANY skin disease

\- Doctor finder (sorted by rating)

\- Confidence-based recommendations

