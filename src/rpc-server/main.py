import signal
import sys
from lxml import etree
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

import functions.documents as document
import functions.queries as queries
from functions.csv_to_xml_converter import CSVtoXMLConverter

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


with SimpleXMLRPCServer(('0.0.0.0', 9000), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    def signal_handler(signum, frame):
        print("\nReceived signal")
        server.server_close()

        print("\nExiting gracefully")
        sys.exit(0)
            
    """ FILES NAME """
    csv_file = "/data/data.csv"
    xml_file = "/data/data.xml"
    xsd_file = "/data/schemas/data.xsd"

    """ CALLED CONVERTION & VALIDATION FUNCTION """
    converter = CSVtoXMLConverter(csv_file)
    file = converter.to_xml_str(xml_file, xsd_file)

    # signals
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    """ FUNCTION REGISTRATION """
    server.register_function(document.import_document_database)
    server.register_function(document.list_documents)
    server.register_function(document.remove_documents)

    """ select all """
    server.register_function(queries.fetch_brands)
    server.register_function(queries.fetch_models)
    server.register_function(queries.fetch_market_categories)

    """ selects by text """
    server.register_function(queries.fetch_most_valuable_cars)
    server.register_function(queries.fetch_models_by_brand)
    server.register_function(queries.fetch_vehicles_by_year)
    server.register_function(queries.fetch_brands_by_country)

    """ selects stats / count """
    server.register_function(queries.fetch_model_percentage)
    server.register_function(queries.fetch_model_percentage_by_brand)

    print("\nStarting the RPC Server...")
    server.serve_forever()