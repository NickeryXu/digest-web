from app import app

if __name__ == '__main__':
    # config_logging()
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'], threaded=True)