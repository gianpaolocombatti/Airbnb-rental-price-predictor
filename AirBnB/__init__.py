from .predictions import create_app

APP = create_app()

APP.run_server(debug=True)
