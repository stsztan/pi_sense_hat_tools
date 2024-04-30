from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import json
from sense_hat import SenseHat


port = 9533
s = SenseHat()
app = Flask(__name__)
CORS(app)


@app.route("/ledmatrix/<led_matrix_input>")
@cross_origin()
def rec_list(led_matrix_input):
    try:
        lst = json.loads(led_matrix_input)
        s.set_pixels(lst)
    except Exception as e:
        return str(e)
    return jsonify(lst)


if __name__ == '__main__':
    s.clear()
    app.run(host='0.0.0.0', port=port)
