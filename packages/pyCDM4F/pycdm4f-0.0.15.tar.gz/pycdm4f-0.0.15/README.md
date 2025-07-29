# pyCDM4F: (p)ython (C)hill-(D)ay (M)odel (f)or (F)lowering date

## What is pyCDM4F?

[github](https://github.com/CSBL-urap/2024-summer-swkim)

pyCDM4F is Python package designed to guide the overall analysis procedure for **Budding & Flowering Prediction** specially tailored to **your target plant**. It offers useful functions including, **Downloading & Merging phenological and meteorological data, Key Parameter Examination, Visualization, Clustering**... and so on. The Chill-Day Model provided by this package demonstrates the highest prediction accuracy for Korean local areas among previously published models. Additionally, pyCDM4F has a broder objective: to become a generalized, open source tool for **accruate prediction of plant phenology** and to provide **insights and scientific research on phenological shift** in many regions affected by global warming.


What is **Chill-Day Model** and How to apply? (*References*)
- [Chilling and forcing model to predict bud-burst of crop and forest species](https://www.sciencedirect.com/science/article/pii/S0168192304000632)
- [Prediction of Blooming Dates of Spring Flowers by Using Digital Temperature Forecasts and Phenology Models](https://www.researchgate.net/publication/263399406_Prediction_of_Blooming_Dates_of_Spring_Flowers_by_Using_Digital_Temperature_Forecasts_and_Phenology_Models)


## Table of Contents

[How to use pyCDM4F?]()

[Main Features]()

[Description for Embedded Dataset]()

[Physiological Background for Plant Phenology]()

[Where to get it]()

[Useful Readings \& Links]()

[Contributing to pyCMD4F]()


## How to use pyCDM4F?

[Here](https://wikidocs.net/book/17034) is the detailed user guide of pyCDM4F.


## Main Features

pyCDM4F is designed to specialize in these areas.
- Contains sufficient [Embedded Data](https://wikidocs.net/272157) extracted from [**공공데이터포털**](https://www.data.go.kr/). 
- Easily [download and merge](https://wikidocs.net/272158) various types of phenological and meteorological data into the embedded data set or create your own. [Filter and Preprocess](https://wikidocs.net/272259) data to make it compatible with the package.
- [Predict **Bud-burst**](https://wikidocs.net/272309) and [Predict **Flowering**](https://wikidocs.net/272326) simultaneously for multiple regions with Chill-Day Model and Dataset. Highest accuracy for Korean local areas among previously published models.
- Simple application of [Hierarchical Clustering](https://wikidocs.net/272554) based on Chill-Day Model Temperature Time and [2D & 3D t-SNE method](https://wikidocs.net/272554#details-of-tsne_visualization) for future analysis.
- Select best key parameter sets with [Error Heatmap](https://wikidocs.net/272326#details-of-flowering_error_heatmap) and [Error Contourmap](https://wikidocs.net/272326#details-of-flowering_error_contourmap) visualization based on Mean Absolute Error(MAE) & Root Mean Squared Error(RMSE).
- After select the best fit parameter set, [line_graph & simple regression](https://wikidocs.net/272553#actual-shape-of-chill-day-model-graph) shows how you select parameters well.
- [Detailed shape of Chill-Day Model graph](https://wikidocs.net/272553#detailed-shape-of-chill-day-model) for each location & year and [Merged Chill-Day Model graph](https://wikidocs.net/272750#details-of-chillday_graph_merged) for each Cluster. 
- Contains [information](https://wikidocs.net/272757) about the years of occurrence of El Niño and La Niña in Korea, gives plot [how the prediction error shifts](https://wikidocs.net/272750#prediction-error-shift-under-climate-change) under climate change. 



## Description for Embedded Dataset

| Data | Division | Description | Period | Reference |
|----:|----:|----:|----:|-----:|
|daily_temperature_data|Daily|95 locations & 8 variables|1907-2025 (Maximum)|[Public Data Portal in Korea](https://www.data.go.kr/data/15043648/fileData.do)|
|daily_meteorological_data|Daily|95 locations & 39 variables|1907-2025 (Maximum)|[Public Data Portal in Korea](https://www.data.go.kr/data/15043648/fileData.do)|
|monthly_meteorological_data|Monthly|95 locations & 31 variables| 1907-2025 (Maximum)| [KMA](https://www.data.go.kr/data/15043648/fileData.do)|
|OBS_phenology_data|Animal, Plant, Meteorological Phenomena|Main Target Prunus(Budding date/Flowering date/Full Bloom date)| 1973-2025 (Observed Once A Year)| [KMA](https://data.kma.go.kr/data/seasonObs/seasonObsDataList.do?pgmNo=648)|
|Prunus_phenology_data|Prunus(budding/flowering/full bloom)|Extracted from OBS_phenology_data| 1973-2025 (Observed Once A Year)| [KMA](https://data.kma.go.kr/data/seasonObs/seasonObsDataList.do?pgmNo=648)|
|Apricot_phenology_data|Apricot(budding/flowering/full bloom)|Extracted from OBS_phenology_data| 1973-2025 (Observed Once A Year)| [KMA](https://data.kma.go.kr/data/seasonObs/seasonObsDataList.do?pgmNo=648)|
|Forsythia_phenology_data|Forsythia(budding/flowering/full bloom)|Extracted from OBS_phenology_data| 1973-2025 (Observed Once A Year)| [KMA](https://data.kma.go.kr/data/seasonObs/seasonObsDataList.do?pgmNo=648)|
|Pear_phenology_data|Pear(budding/flowering/full bloom)|Extracted from OBS_phenology_data| 1973-2025 (Observed Once A Year)| [KMA](https://data.kma.go.kr/data/seasonObs/seasonObsDataList.do?pgmNo=648)|
[Here]() is the full data set containing **39 variables** for extended daily_temperature_data and more than **15 species** of **계절관측 데이터**.



## Physiological Background for Plant Phenology

After summer, if the nutrition & weather conditions are satisfied, woody plants prepare next year flowering by differentiation to **flower buds**. But to prevent flower bud differentiate to flowers in cold winter condition because of transient warm temperature, flower buds come into **dormancy state** and their flowering control genes maintain bud statement until they get enough cold requirment. 

In the Phenology Model, we call the cold requirement as '*Chill-requirement(Cr)*'. If the woody plant get enough cold, dormancy releases. From this time, plant needs Heat to differentiate into flowers. After the heat accumulated same amount to Cr, the Budding event happens. We call that as **Bud burst**. Last, the amount of heat accumulation flower bud differentiate into flower, **flowering**, is called as '*Heat-requirement(Hr)*'.

- Dormancy initiation: The Day when minimum temperature reaches to 5-7℃. (Depends on species)
- Dormancy release: The first Day when Chill accumulation is lower than Chill-requirement. 
- Bud burst: Observed Day when 20% of total flower buds in Woody plant get into bud burst.
- Flowering: Observed Day when 3 flowers are observed in a branch. 
- Detailed definition and observation rules are [**guidelines**](https://data.kma.go.kr/data/publication/publicationGlList.do) of KMA(Korea Meteorological Administration).


## Where to get it

The source code is currently hosted on GitHub at:
[https://github.com/CSBL-urap/2024-summer-swkim](https://github.com/CSBL-urap/2024-summer-swkim)

Binary installers for the latest released version are available at the [Python Package Index (PyPI)]() and on [Conda]().

```python
# PyPI

pip install pyCMD4F
```


## Useful Readings & Links

- [기상자료개방포털](https://data.kma.go.kr/)
- [공공데이터포털](https://www.data.go.kr/)
- [중앙일보 기사: 벚꽃이 피는 날짜를 어떻게 미리 알 수 있을까](https://www.joongang.co.kr/article/23433131)
- [Chilling and forcing model to predict bud-burst of crop and forest species](https://www.sciencedirect.com/science/article/abs/pii/S0168192304000632)
- [Predicting Cherry Flowering Date Using a Plant Phonology Model](https://www.researchgate.net/publication/263643081_Predicting_Cherry_Flowering_Date_Using_a_Plant_Phonology_Model)



## Contributing to pyCMD4F

All questions, bug reports, bug fixes, enhancements, requests, and ideas are welcome.

Feel free to send an email. 
- **kimsongwon10@korea.ac.kr**
- **rsw147362@gmail.com**


