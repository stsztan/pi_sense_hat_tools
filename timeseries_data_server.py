from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import pathlib
import urllib
import json
import configargparse
import requests


# globals
current_file = __file__
app = Flask(__name__)
CORS(app)


# consts
server_endpoint = 'json_content'


# defaults
default_encoding = 'UTF-8'
default_port = 9533
default_json_retrieval_server_base = 'http://localhost:9577'
default_timestamp_identifier = 'timestamp'
default_data_container = 'data'
default_key_identifier = 'key'
default_value_identifier = 'value'


def config_param(param, *args, **kwargs):
    # handling configuration parameters
    config_file_stem = pathlib.Path(current_file).stem
    config_file = f'{config_file_stem}.conf'
    p = configargparse.ArgParser(
        default_config_files=[config_file]
    )
    p.add(*args, **kwargs)
    arg, unknown = p.parse_known_args()
    param = getattr(arg, param)
    return param


@app.route("/csv_content/<start_dt_str>/<end_dt_str>")
@cross_origin()
def csv_content(start_dt_str, end_dt_str):
    try:
        # handling configuration parameters
        config_file_stem = pathlib.Path(current_file).stem
        p = configargparse.ArgParser(
            default_config_files=[f'{config_file_stem}.conf']
        )
        p.add('-s', '--server', help='json retrieval server base')
        p.add('-c', '--encoding', help='default encoding of json data')
        p.add('-t', '--timestamp', help='json timestamp identifier')
        p.add('-d', '--data', help='json data container structure identifier')
        p.add('-k', '--key', help='json structure key identifier')
        p.add('-v', '--value', help='json structure value identifier')
        args, unknown = p.parse_known_args()
        json_retrieval_server_base = args.server or \
            default_json_retrieval_server_base
        encoding = args.encoding or default_encoding
        timestamp_identifier = args.timestamp or default_timestamp_identifier
        data_container = args.data or default_data_container
        key_identifier = args.key or default_key_identifier
        value_identifier = args.value or default_value_identifier

        collected_data = {}
        # get json from server
        json_retrieval_server_url = urllib.parse.urljoin(
            json_retrieval_server_base,
            f'{server_endpoint}/{start_dt_str}/{end_dt_str}'
        )
        response = requests.get(json_retrieval_server_url)
        merged_data = json.loads(
            response.content.decode(encoding)
        )
        for item in merged_data:
            timestamp = item[timestamp_identifier]
            ts_data = {}
            for ccy in item[data_container]:
                key = ccy[key_identifier]
                value = ccy[value_identifier]
                ts_data[key] = value
            collected_data[timestamp] = ts_data
    except Exception as e:
        return str(e)
    return jsonify(collected_data)


if __name__ == '__main__':
    # handling configuration parameters
    port = config_param('port', '-p', '--port', help='listening port')
    try:
        port = int(port)
    except (ValueError, TypeError):
        port = default_port
    app.run(host='0.0.0.0', port=port)
