import json
import os
import pandas as pd
import geopandas as gpd
from loguru import logger

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

READ_DIR = 'annotations/'
TOP10_CSV = 'poi_top10.csv'
GEOCODING_CSV = 'poi_geocoding.csv'
POI_DESC_CSV = 'poi_desc_geom.csv'
DETAILED_GEOJSON = 'top_k_detailed_{case_id}.geojson'

WRITE_DIR = 'outputs/'
RECORD_FILE = 'annotations.json'
BACKUP_FILE = 'backup_annotation.json'

pois = pd.read_csv(os.path.join(READ_DIR, POI_DESC_CSV))
geocodings = pd.read_csv(os.path.join(READ_DIR, GEOCODING_CSV))
topk_df = pd.read_csv(os.path.join(READ_DIR, TOP10_CSV))



def get_annotation_data(case_id):
    # this will return geocoding+top_k for case_id
    # [{osm_type, osm_id, info, location}] 10 if there was something!
    logger.debug(f'getting annotation data - both geocodig and top k: {case_id}')
    geocoding_row = get_annotation_geocoding(case_id)
    topk_rows = get_annotation_topk(case_id)
    if geocoding_row is None:
        return topk_rows
    found = False
    for row in topk_rows:
        if row['osm_id'] == geocoding_row['osm_id'] and row['osm_type'] == geocoding_row['osm_type']:
            logger.debug(f'found the geocoding record in the topk - updating names')
            row['name'] = geocoding_row['name']
            row['full_name'] = geocoding_row['full_name']
            found = True
            break
    if found:
        return topk_rows
    return [geocoding_row] + topk_rows


def get_annotation_geocoding(case_id):
    # this will return geocoding for case_id
    # {osm_type, osm_id, info, location}
    logger.debug(f'getting annotation geocoding results - {case_id}')
    row = geocodings[geocodings['index'] == case_id]
    logger.debug(f'raw_results: {row}')
    if row.iloc[0].isna().osm_id:
        logger.debug(f'geocoding: row is empty - {case_id}')
        return None
    else:
        row_dict = row.to_dict(orient='records')[0]
        logger.debug(f'row dictionary: {row_dict}')
        return row_dict


def get_annotation_topk(case_id):
    # this will return top_k matches for case_id
    # [{osm_type, osm_id, info, location}]
    logger.debug(f'getting the top_k results for {case_id}')
    rows = topk_df[topk_df['index'] == case_id]
    rows.fillna('', inplace=True)
    logger.debug(f'raw_results:\n{rows}')
    rows_dict = rows.to_dict(orient='records')
    logger.debug(f'rows dictionary: {rows_dict}')
    return rows_dict


def get_case_information(case_id):
    # this will return information about the POI case
    # {title, description, link, location}
    logger.debug(f'reading the POI information {case_id}')
    poi = pois[pois['index'] == case_id]
    logger.debug(f'selected row: {poi}')
    title = poi.iloc[0].title
    summary = poi.iloc[0].summary
    lat = poi.iloc[0].lat
    lng = poi.iloc[0].lng
    link = f'https://www.openstreetmap.org/#map=18/{lat}/{lng}'
    logger.debug(f'link: {link}')
    case_information = {'title': title, 'description': summary, 'link': link, 'location': [lat, lng], 'page': case_id}
    logger.debug(f'case information: {case_information}')
    return case_information


def save_annotated_records(backup_every=10, force_save=False):
    logger.debug(f'writing annotations - {len(records)}')
    with open(os.path.join(WRITE_DIR, RECORD_FILE), 'w', encoding='utf-8') as fp:
        json.dump(records, fp)
    if len(records)%backup_every or force_save:
        logger.info('saving a backup file as well')
        with open(os.path.join(WRITE_DIR, BACKUP_FILE), 'w', encoding='utf-8') as fp:
            json.dump(records, fp)
    logger.info(f'annotation file save. Number of records: {len(records)}')


def read_annotated_records():
    if os.path.isfile(os.path.join(WRITE_DIR, RECORD_FILE)):
        with open(os.path.join(WRITE_DIR, RECORD_FILE)) as fp:
            records = json.load(fp)
        logger.info(f'annotation file found and loaded - #records: {len(records)}')
        return records
    return []

records = read_annotated_records()

def add_to_annotation(case_id, annotations):
    if case_id != len(records):
        logger.error('something is wrong as the annotation records do not match the case_id')
        raise RuntimeError()
    records.append(annotations)
    save_annotated_records()
    logger.info(f'annotation is successfully captured: #record: {len(records)}')


def edit_annotation(case_id, annotations):
    if len(records) <= case_id:
        logger.error(f'you cannot edit a record which is not captured yet! {len(records)} - {case_id}')
        raise RuntimeError()
    records[case_id] = annotations
    save_annotated_records(force_save=True)
    logger.info(f'annotation is successfully updated: #record: {len(records)}')


def return_bbox(location, get_data_output):
    epsilon = 0.001
    min_lat = location[0] - epsilon
    max_lat = location[0] + epsilon
    min_lng = location[1] - epsilon
    max_lng = location[1] + epsilon
    for d in get_data_output:
        if 'lat' not in d or 'lng' not in d:
            logger.error(d)
        if d['lat'] > max_lat:
            max_lat = d['lat'] + epsilon
        elif d['lat'] < min_lat:
            min_lat = d['lat'] - epsilon
        if d['lng'] > max_lng:
            max_lng = d['lng'] + epsilon
        elif d['lng'] < min_lng:
            min_lng = d['lng'] - epsilon
    return [min_lat, max_lat, min_lng, max_lng]


@app.route('/get-case-info')
def get_case_info(case_id=len(records)):
    page = int(request.args.get('page', -1))
    if page >= 0:
        case_id = page
    output = get_case_information(case_id)
    print(output)
    get_data_output = get_annotation_data(case_id)
    output['table'] = get_data_output
    print(output)
    return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True)

