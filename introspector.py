import streamlit as st
import urllib.parse        
import requests
from rdflib import Graph
from streamlit_agraph import TripleStore, agraph

import urllib
import urllib.parse        

#grab the first value of each parameter
oparams = st.experimental_get_query_params()
params = {
    x: oparams[x][0]  for x in oparams
}

def resolver(url):
    data2 =  requests.get(url)
    value =   data2.text
    return value

def get_input():
    store = TripleStore()
    q= st.experimental_get_query_params()

    #if "text-input" in q:
    #    return q["text-input"]
    if "messages" in q:
        for item in q["messages"]:
            new1 = urllib.parse.unquote(item)
            graph = Graph()
            if new1.startswith("http"):
                graph.parse(new1,format=q.get("format",["ttl"])[0])
            else:
                st.code(new1)
                graph.parse(data=new1,format=q.get("format",["ttl"])[0])
                
            for subj, pred, obj in graph:
                store.add_triple(subj, pred, obj, "")
    return store
    
#agraph(list(store.getNodes()), list(store.getEdges()), config)
