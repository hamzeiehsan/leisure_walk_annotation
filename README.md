# Annotation Tool for Leisure Walking POIs
Annotation process includes two step:
- First checking the map and table to see if there is a match (if the description of the POI matching with one or more records in the table)
- Second step is too explore the map and double-check any entity that matches with the POI description. If there is a case, click on the link and use OSM feature identifier to collect type (Node, Way, Relation) and OSM_ID.

## Installation
Install `python==3.11.9`, and the following dependencies:

1. flask==2.2.5
2. pandas==2.2.1
3. loguru==0.7.2

Optional - you may need to install `geopandas` (if you are interested in using detailed geometries on the map).

## Research Project Abstract:
This paper studies leisure walking recommendations by exploring points of interest (POIs) within leisure walk descriptions. In contrast to destination-oriented walks, leisure walks emphasise experiencing the environment, engaging in activities, and discovering places through intermediate destinations called POIs. POIs have an important role in the process of recommending a leisure walk, yet a detailed analysis of POIs in the context of leisure walking is missing in the literature. This study extracts and annotates POIs of leisure walking recommendations available in \emph{WalkingMaps.com.au}, creating an annotated dataset for further analysis to address this research gap. Our own analysis includes classifying POIs, matching them with data available in OpenStreetMap, and comparing the selected POIs with nearby alternatives. The analysis aims to reveal patterns in POI selection, providing insights into why certain places are preferred during leisure walks, and evaluate the availability of rich data in OpenStreetMap for future automated leisure walking recommendation. This study contributes to automated systems for recommending leisure walks, tailoring suggestions based on available information in the spatial open data and presents an annotated dataset to facilitate future research in this field.

Source of the original data: WalkingMaps.com.au