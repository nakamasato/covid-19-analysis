# Covid-19 Analysis

## Run

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python visualize.py
```

![](docs/image-01.png)

## Data

1. [新型コロナワクチンの接種状況](https://info.vrs.digital.go.jp/dashboard): data/prefecture.ndjson
1. [日本の超過および過少死亡数ダッシュボード](https://exdeaths-japan.org/graph/weekly/):
    1. 観測死亡者数: data/exdeath-japan-observed.csv
    1. 予測死亡者数: data/exdeath-japan-estimates.csv
    1. 都道府県マスター: data/prefecture_master.csv
        ```
        cat data/exdeath-japan-observed.csv| cut -f1,2,3 -d, | sort -n| uniq > data/prefecture_master.csv
        ```

## Reference
1. https://plotly.com/python/figure-structure/
1. https://dash.plotly.com/basic-callbacks
