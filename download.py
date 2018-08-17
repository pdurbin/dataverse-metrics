import json
import sys
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
try:
    import urllib.request as urlrequest
except ImportError:
    import urllib as urlrequest
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def main():
    with open('config.json') as config_file:
        config = json.load(config_file)

    installations = config['installations']
    api_response_cache_dir = config['api_response_cache_dir']
    num_months_to_process = config['num_months_to_process']
    monthly_endpoints = config['endpoints']['monthly']
    single_endpoints = config['endpoints']['single']

    for installation in installations:
        process_monthly_endpoints(installation, monthly_endpoints, api_response_cache_dir, num_months_to_process)
        process_single_endpoints(installation, single_endpoints, api_response_cache_dir)


def process_monthly_endpoints(installation, monthly_endpoints, api_response_cache_dir, num_months_to_process):
    for endpoint in monthly_endpoints:
        process_monthly_endpoint(installation, endpoint, api_response_cache_dir, num_months_to_process)


def process_monthly_endpoint(installation, endpoint, api_response_cache_dir, num_months_to_process):
    for month in get_months(num_months_to_process):
        url = installation + '/api/info/metrics/' + endpoint + '/' + month
        response = urlrequest.urlopen(url)
        json_out = get_remote_json(response)
        o = urlparse(installation)
        hostname = o.hostname
        path = api_response_cache_dir + '/' + endpoint + '/' + month
        if not os.path.exists(path):
            os.makedirs(path)
        filename = hostname + '.json'
        with open(path + '/' + filename, 'w') as outfile:
            json.dump(json_out, outfile, indent=4)


def get_months(num_months_to_process):
    months = []
    for i in range(num_months_to_process):
        one_month_ago = datetime.today() - relativedelta(months=i)
        last_month = one_month_ago.strftime('%Y-%m')
        months.append(last_month)
    return months


def get_remote_json(response):
    if sys.version_info > (3, 0, 0):
        return json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))
    else:
        return json.loads(response.read())


def process_single_endpoints(installation, single_endpoints, api_response_cache_dir):
    for endpoint in single_endpoints:
        process_single_endpoint(installation, endpoint, api_response_cache_dir)


def process_single_endpoint(installation, endpoint, api_response_cache_dir):
    url = installation + '/api/info/metrics/' + endpoint
    response = urlrequest.urlopen(url)
    json_out = get_remote_json(response)
    o = urlparse(installation)
    hostname = o.hostname
    path = api_response_cache_dir + '/' + endpoint
    if not os.path.exists(path):
        os.makedirs(path)
    filename = hostname + '.json'
    with open(path + '/' + filename, 'w') as outfile:
        json.dump(json_out, outfile, indent=4)


if __name__ == '__main__':
    main()
