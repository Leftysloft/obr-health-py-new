import os
import flask
import dndbeyond

app = flask.Flask(__name__)
BASE_URL = "http://127.0.0.1:5000"

@app.route("/", methods=["GET"])
def index():
    return flask.Response("Widget website is running.")

#address for local <>
@app.route("/character_server", methods=["GET"])
def character_server():
    cid = flask.request.args.get("id", type=int)
    
#confirm validity of name and cid or abort
    if cid is None:
        return flask.abort(400)
    
#creates the html template
    return flask.render_template("character_server.html", cid=cid, base_url=BASE_URL)

#sets the .css file from the "css" folder
@app.route("/css/<file>.css", methods=["GET"])
def css(file):
    return flask.send_from_directory("css", f"{file}.css")

#sets the .js file from the "js" folder
@app.route("/js/<file>.js", methods=["GET"])
def js(file):
    return flask.send_from_directory("js", f"{file}.js")

@app.route("/api/character-hp/<character_id>")
def character_hp(character_id):
    try:
        client = dndbeyond.DnDBeyond(character_id)
        hp = client.get_character_hp()
        return flask.jsonify(hp)
    except Exception as e:
        return flask.jsonify({"error": str(e)})
    
if __name__ == "__main__":
    app.run()