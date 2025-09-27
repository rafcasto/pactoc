from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = app.config['PORT']
    debug = app.config['DEBUG']
    
    app.run(host='0.0.0.0', port=port, debug=debug)