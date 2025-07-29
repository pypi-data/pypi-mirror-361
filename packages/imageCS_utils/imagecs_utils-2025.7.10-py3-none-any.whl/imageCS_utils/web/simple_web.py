"""An example flask web"""
from flask import Flask

def start_simple_web(context:str, port:int, host:str="127.0.0.1"):
    """start a simple web

    Args:
        context (str): web html context
        port (int): listent port
        host (str): listent ip
    """
    app = Flask("simple web")

    @app.route('/')
    def web_root():
        return context
    
    app.run(host=host, port=port)
