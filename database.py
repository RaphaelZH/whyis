# -*- coding:utf-8 -*-

import flask_ld as ld
from rdflib import *
SPARQL_NS = Namespace('http://www.w3.org/2005/sparql-results#')
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore, _node_to_sparql, POST
from SPARQLWrapper import *

import requests

import collections

def node_to_sparql(node):
    if isinstance(node, BNode):
        return '<bnode:b%s>' % node
    return _node_to_sparql(node)

#def node_from_result(node):
#    if node.tag == '{%s}uri' % SPARQL_NS and node.text.startswith("bnode:"):
#        return BNode(node.text.replace("bnode:",""))
#    else:
#        return _node_from_result(node)

def create_query_store(store):
    new_store = SPARQLStore(endpoint=store.endpoint,
                            default_query_method=POST,
                            returnFormat=JSON,
                            node_to_sparql=node_to_sparql)
    new_store._defaultReturnFormat=JSON
    new_store.setReturnFormat(JSON)
    return new_store

memory_graphs = collections.defaultdict(ConjunctiveGraph)
        
def engine_from_config(config, prefix):
    defaultgraph = None
    if prefix+"defaultGraph" in config:
        defaultgraph = URIRef(config[prefix+"defaultGraph"])
    if prefix+"queryEndpoint" in config:
        store = SPARQLUpdateStore(queryEndpoint=config[prefix+"queryEndpoint"],
                                  update_endpoint=config[prefix+"updateEndpoint"],
                                  default_query_method=POST,
                                  returnFormat=JSON,
                                  node_to_sparql=node_to_sparql)
        def publish(data, *graphs):
            s = requests.session()
            s.keep_alive = False
            result = s.post(store.endpoint,
                            data=data,
#                            params={"context-uri":graph.identifier},
                            headers={'Content-Type':'application/x-trig'})

        store.publish = publish

        store._defaultReturnFormat=JSON
        store.setReturnFormat(JSON)
        graph = ConjunctiveGraph(store,defaultgraph)
    elif prefix+'store' in config:
        graph = ConjunctiveGraph(store='Sleepycat',identifier=defaultgraph)
        graph.store.batch_unification = False
        graph.store.open(config[prefix+"store"], create=True)
    else:
        graph = memory_graphs[prefix]
        def publish(data, *graphs):
            for nanopub in graphs:
                graph.addN(nanopub.quads())
        graph.store.publish = publish

        
    return graph

