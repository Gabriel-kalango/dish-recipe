from api import create_app
from flask_socketio import SocketIO
from api.config.config import config_dict


app = create_app(config=config_dict["dev"])
socket=SocketIO(app,cors_allowed_origins="*")

if __name__=="__main__":
    socket.run(app,debug=True)
