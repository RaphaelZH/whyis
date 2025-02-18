from builtins import str
import sadi
import rdflib
import setlr
from datetime import datetime

from .update_change_service import UpdateChangeService
from nanopub import Nanopublication
from datastore import create_id
import flask
from flask import render_template
from flask import render_template_string
import logging

import sys, traceback

import database

import tempfile

from depot.io.interfaces import StoredFile

from whyis.namespace import *

setlr_handlers_added = False


class SETLr(UpdateChangeService):
    activity_class = setl.SemanticETL

    def __init__(self, depth=-1, predicates=[None]):
        self.depth = depth
        self.predicates = predicates

        global setlr_handlers_added
        if not setlr_handlers_added:
            def _whyis_content_handler(location):
                resource = self.app.get_resource(location)
                fileid = resource.value(self.app.NS.whyis.hasFileID)
                if fileid is not None:
                    return self.app.file_depot.get(fileid.value)

            setlr.content_handlers.insert(0, _whyis_content_handler)
            setlr_handlers_added = True

    def getInputClass(self):
        return setl.SemanticETLScript

    def getOutputClass(self):
        return whyis.ProcessedSemanticETLScript

    def get_query(self):
        return '''select distinct ?resource where { ?resource a %s.}''' % self.getInputClass().n3()

    def explain(self, nanopub, i, o):
        np_assertions = list(i.graph.subjects(rdflib.RDF.type, np.Assertion)) + [nanopub.assertion.identifier]
        activity = nanopub.provenance.resource(rdflib.BNode())
        activity.add(rdflib.RDF.type, i.identifier)
        nanopub.provenance.add((nanopub.assertion.identifier, prov.wasGeneratedBy, activity.identifier))
        for assertion in np_assertions:
            nanopub.provenance.add((activity.identifier, prov.used, assertion))
            nanopub.provenance.add((nanopub.assertion.identifier, prov.wasDerivedFrom, assertion))
            nanopub.pubinfo.add((nanopub.assertion.identifier, prov.wasAttributedTo, i.identifier))
            nanopub.pubinfo.add((nanopub.assertion.identifier, prov.wasAttributedTo, i.identifier))

    def process(self, i, o):
        query_store = self.app.db.store
        if hasattr(query_store, 'endpoint'):
            query_store = database.create_query_store(self.app.db.store)
        db_graph = rdflib.ConjunctiveGraph(store=query_store)
        db_graph.NS = self.app.NS
        setlr.actions[whyis.sparql] = db_graph
        setlr.actions[whyis.NanopublicationManager] = self.app.nanopub_manager
        setlr.actions[whyis.Nanopublication] = self.app.nanopub_manager.new
        setl_graph = i.graph
        #        setlr.run_samples = True
        resources = setlr._setl(setl_graph)
        # retire old copies
        old_np_map = {}
        to_retire = []
        for new_np, assertion, orig in self.app.db.query('''select distinct ?np ?assertion ?original_uri where {
                ?np np:hasAssertion ?assertion.
                ?assertion a np:Assertion;
                prov:wasGeneratedBy/a ?setl;
                prov:wasQuotedFrom ?original_uri.
            }''', initBindings=dict(setl=i.identifier), initNs=dict(prov=prov, np=np)):
            old_np_map[orig] = assertion
            to_retire.append(new_np)
            if len(to_retire) > 100:
                self.app.nanopub_manager.retire(*to_retire)
                to_retire = []
        self.app.nanopub_manager.retire(*to_retire)
        # print resources
        for output_graph in setl_graph.subjects(prov.wasGeneratedBy, i.identifier):
            print("output_graph", output_graph)
            if setl_graph.resource(output_graph)[rdflib.RDF.type:whyis.NanopublicationCollection]:
                self.app.nanopub_manager.publish(resources[output_graph])
            else:
                out = resources[output_graph]
                out_conjunctive = rdflib.ConjunctiveGraph(store=out.store, identifier=output_graph)
                to_publish = []
                triples = 0
                for new_np in self.app.nanopub_manager.prepare(out_conjunctive):
                    self.explain(new_np, i, o)
                    to_publish.append(new_np)

                # triples += len(new_np)
                # if triples > 10000:
                self.app.nanopub_manager.publish(*to_publish)
        for resource, obj in list(resources.items()):
            if hasattr(i, 'close'):
                print("Closing", resource)
                try:
                    i.close()
                except:
                    pass
