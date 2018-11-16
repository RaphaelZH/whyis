import nltk, re, pprint
import autonomic
from bs4 import BeautifulSoup
from rdflib import *
from slugify import slugify
import nanopub
from math import log10
import collections
import os
import javabridge

sioc_types = Namespace("http://rdfs.org/sioc/types#")
sioc = Namespace("http://rdfs.org/sioc/ns#")
sio = Namespace("http://semanticscience.org/resource/")
dc = Namespace("http://purl.org/dc/terms/")
prov = autonomic.prov
whyis = autonomic.whyis

class ConsistencyCheck(autonomic.UpdateChangeService):
    activity_class = whyis.ConsistencyCheck

    def getInputClass(self):
        return sioc.Post

    def getOutputClass(self):
        return URIRef("http://purl.org/dc/dcmitype/Text")

    def get_query(self):
        return '''select ?resource where { ?resource <http://rdfs.org/sioc/ns#content> [].}'''

    def process(self, i, o):
        javabridge.start_vm(class_path=javabridge.JARS+["/apps/whyis/jars/whyis-java-jar-with-dependencies.jar"],run_headless=True)
        try:
            javabridge.run_script('edu.rpi.tw.whyis.HermiTAgent.reason();',
                dict(greetee='world'))
        finally:
            javabridge.kill_vm()
