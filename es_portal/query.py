import functools
import json
import requests
import re
from dotenv import dotenv_values
from requests.auth import HTTPBasicAuth

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    current_app
)

bp = Blueprint('query', __name__, url_prefix='/query')
config = dotenv_values(".env")
basic = HTTPBasicAuth(config['ELASTIC_USER'], config['ELASTIC_USER_PASSWORD'])

if 'default_index' in config:
    default_index = config['default_index']
elif 'DEFAULT_INDEX' in config:
    default_index = config['DEFAULT_INDEX']
else:
    default_index = 'bookmark_sample'

@bp.route('/search', methods=('GET', 'POST'))
def search():
    index = default_index
    if request.method == 'POST':

        error = None
        response = None
        records = None

        base_url = current_app.config['ELASTICSEARCH_BASE_URL']
        search_url = base_url + "/" + index + "/_search/"

        if request.form.get('search_type') == 'by_id':
            id_value = request.form.get('original_id')
            search_url = base_url + "/" + index + "/_doc/" + id_value
            response = requests.get(search_url, auth=(basic))
            raw_json = response.json()
            if 'found' in raw_json and raw_json['found']:
                records = [raw_json]
        elif request.form.get('search_type') == 'by_title':
            post_data = wildcard_search_json(request.form, "title")
        elif request.form.get('search_type') == 'by_path':
            post_data = wildcard_search_json(request.form, "path")
        elif request.form.get('search_type') == 'by_uri':
            post_data = wildcard_search_json(request.form, "uri")
        elif request.form.get('search_type') == 'by_keyword':
            post_data = wildcard_search_json(request.form, "keyword")
        elif request.form.get('search_type') == 'by_tags':
            post_data = wildcard_search_json(request.form, "tags")
        else:
            error = "Invalid search type"
            flash(error)

        if response is None:
            response = requests.post(search_url, auth=(basic), json=post_data)
            raw_json = response.json()
            records = standardize_records(raw_json)

        if 'error' in raw_json:
            current_app.logger.error(raw_json)

            if 'reason' in raw_json['error']:
                error = raw_json['error']['reason']
            else:
                error = 'Unknown application error'

            flash(error, 'error')
            return render_template('query/search.html')

        if records is not None:
            return render_template("query/results.html", records=records)
        else:
            error = "No records found"
            flash(error, 'info')
            return render_template('query/search.html')

    else:
        return render_template('query/search.html')

def wildcard_search_json(form, field):
    field_name = field + ".keyword"
    results = {
        "query": {
            "wildcard": {
                field_name: {
                    "value": form.get(field),
                    "boost": 1.0,
                    "rewrite": "constant_score"
                }
            }
        }
    }
    return results

def standardize_records(json_results):
    records = None
    if 'hits' in json_results:
        if 'hits' in json_results['hits']:
            if len(json_results['hits']['hits']):
                records = json_results["hits"]["hits"]
    return records
