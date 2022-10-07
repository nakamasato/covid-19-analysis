# Covid-19 Analysis

## Run

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python visualize.py
```

![](docs/image-02.png)

## Data

1. [新型コロナワクチンの接種状況](https://info.vrs.digital.go.jp/dashboard): data/prefecture.ndjson
1. [日本の超過および過少死亡数ダッシュボード](https://exdeaths-japan.org/graph/weekly/):
    1. 観測死亡者数: data/exdeath-japan-observed.csv
    1. 予測死亡者数: data/exdeath-japan-estimates.csv
    1. 都道府県マスター: data/prefecture_master.csv
        ```
        cat data/exdeath-japan-observed.csv| cut -f1,2,3 -d, | sort -n| uniq > data/prefecture_master.csv
        ```
1. [日本の超過及び過小死亡数ダッシュボード (死因別死亡数)](https://exdeaths-japan.org/graph/weekly_cause): data/exdeath-japan-cause
1. [人口動態調査](https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00450011&tstat=000001028897&cycle=1&year=20220&tclass1=000001053058&tclass2=000001053060&cycle_facet=tclass1%3Atclass2%3Acycle&tclass3val=0)
    1. [人口動態統計速報(令和４年７月分)](https://www.mhlw.go.jp/toukei/saikin/hw/jinkou/geppo/s2022/dl/202207.pdf)
    1. [人口動態調査2022年](https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00450011&tstat=000001028897&cycle=1&year=20220&tclass1=000001053058&tclass2=000001053059&cycle_facet=tclass1%3Atclass2%3Acycle&tclass3val=0)
1. 簡易生命表: 日本における日本人について、令和３年１月から 12 月の１年間の死亡状況が今後変化しないと仮定したときに、各年齢の者が１年以内に死亡する確率や、平均してあと何年生きられるかという期待値などを、死亡率や平均余命などの指標によって表したもの
    1. [令和２年簡易生命表](https://www.mhlw.go.jp/toukei/saikin/hw/life/life20/dl/life18-15.pdf)
        -> 令和２年簡易生命表のダウンロード [42KB] （生命表を.xlsx形式でダウンロードできます）からデータ作成
    1. [令和３年簡易生命表](https://www.mhlw.go.jp/toukei/saikin/hw/life/life21/dl/life18-15.pdf)
1. [人口推移](https://www.stat.go.jp/data/jinsui/2.html)
## Reference
1. https://plotly.com/python/figure-structure/
1. https://dash.plotly.com/basic-callbacks
