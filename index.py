from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask_caching import Cache
import requests
import data
import urllib.parse
import calendar
import time

app = Flask(__name__)
# cache = Cache(app, config={'CACHE_TYPE': 'simple',
#               'CACHE_DEFAULT_TIMEOUT': 60})

articles = []

a = {'statussalida': '',
     'registros': '',
     'camposseguros': '',
     'ctimestamp': '',
     }


def data_test():
    json_articulos = data.articulosWeb
    json_categoriasArticulosWeb = data.categoriasArticulosWeb

    articles = json_articulos['registros']

    categorias_dict = {f"{categoria['marca']}-{categoria['codigo']}":
                       categoria for categoria in json_categoriasArticulosWeb['registros']}

    for i in articles:
        key = f"{i['marca']}-{i['codigo']}"
        if key in categorias_dict:
            i['categoria'] = categorias_dict[key]

    articles = [item for item in articles if 'categoria' in item]
    return articles


def search_products(data, parametros):
    current_time = time.gmtime()
    time_stamp = calendar.timegm(current_time)
    match parametros:
        case parametros if parametros['search'] != '' and parametros["search"] != None:
            searched_articles = [
                item for item in data if f'{parametros["search"].lower()}' in item['descripcion'].lower()]
            a['ctimestamp'] = time_stamp
            a['registros'] = searched_articles
            json_searched = jsonify(a)
            response = make_response(json_searched, 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        case parametros if parametros['categoria'] != '' and parametros['categoria'] != None:
            searched_categorias = [item for item in data if
                                   int(parametros['categoria']) == int(item['categoria']['categoria'])]
            a['ctimestamp'] = time_stamp
            a['registros'] = searched_categorias
            json_searched = jsonify(a)
            response = make_response(json_searched, 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        case _:
            mensaje = {
                "mensaje": 'Parametros vacios',
                "registros": []
            }
            mensaje = jsonify(mensaje)
            response = make_response(mensaje, 404)
            response.headers['Content-Type'] = 'application/json'
            return response


@app.route('/', methods=['GET'])
# @cache.cached(timeout=3600)
def search_articles():
    global articles
    categoria = request.args.get('categoria')
    s = request.args.get('s')
    # print(f"search: {s} - categoria: {categoria}")
    # path = request.full_path
    # parsed_url = urllib.parse.urlparse(path)
    # params = urllib.parse.parse_qs(parsed_url.query)

    # params_categoria = params.get('categoria', [''])[0]
    # params_search = params.get('s', [''])[0]
    parametros = {
        "search": s,
        "categoria": categoria
    }
    try:
        if len(articles) == 0:
            articles = data_test()
            return search_products(articles, parametros)

        return search_products(articles, parametros)

    except Exception as e:
        return f"Ocurrio un error: {e}"


if __name__ == '__main__':
    # app.config['datos'] = data_test()
    app.run(debug=True, host='192.168.0.130', port=8003)
