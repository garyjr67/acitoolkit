"""
REST API service wrapper for the Intersite tool
"""
from flask import Flask, request, abort, make_response, jsonify
from intersite import execute_tool, get_arg_parser
import json
from flask.ext.httpauth import HTTPBasicAuth

DEFAULT_PORT = '5000'
DEFAULT_IPADDRESS = '127.0.0.1'

auth = HTTPBasicAuth()

parser = get_arg_parser()
parser.add_argument('--ip',
                    default=DEFAULT_IPADDRESS,
                    help='IP address to listen on.')
parser.add_argument('--port',
                    default=DEFAULT_PORT,
                    help='Port number to listen on.')

args = parser.parse_args()
collector = execute_tool(args, test_mode=True)
app = Flask(__name__)


@auth.get_password
def get_password(username):
    """
    Get the password
    :param username: String containing the username
    :return: String containing the password for the user or None if the user does not exist
    """
    if username == 'admin':
        return 'acitoolkit'
    return None


@auth.error_handler
def unauthorized():
    """
    Error handler for attempted unauthorized access
    :return: 401 Error Response
    """
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@app.route('/config', methods=['GET'])
@auth.login_required
def get_config():
    """
    Get the current configuration
    :return: JSON dictionary containing the current configuration
    """
    return json.dumps(collector.config.get_config(), indent=4, separators=(',', ':'))


@app.route('/config', methods=['POST', 'PUT'])
@auth.login_required
def set_config():
    """
    Set the current configuration
    :return: JSON dictionary with a Status of OK if successful
    """
    if not request.json:
        abort(400)
    resp = collector.save_config(request.json)
    if resp != 'OK':
        abort(400)
    collector.reload_config()
    return json.dumps({'Status': 'OK'}, indent=4, separators=(',', ':'))

if __name__ == '__main__':
    app.run(debug=False, host=args.ip, port=int(args.port))
