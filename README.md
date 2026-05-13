# COMP2073 Project by RinChord

- [Project brief](documents/GroupProject26_Zh-CN.pdf)
- [Pokemon dataset reference](documents/pokemon属性详情.pdf)

## Exploratory data analysis

1. 属性分析：哪种属性（Type 1）的宝可梦最多
2. 属性与强度的关系：哪种属性的宝可梦平均攻击力最高
3. 特征相关性：攻击力（Attack）和速度（Speed）之间是否有正相关
4. 比较传奇宝可梦（`is_legendary`）与非传奇宝可梦在攻击、防御、速度等方面的平均差异

## Visualization

Streamlit app: 选择需要绘制的图表 tab，即可查看对应可视化结果。

```
streamlit run src/data_visualization/main.py
```

## Clustering (TODO)

K-Means 聚类宝可梦战斗定位，把它们分成刺客、坦克、法师等直观类别。
