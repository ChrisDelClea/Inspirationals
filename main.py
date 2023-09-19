import streamlit as st
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON
from streamlit_agraph import agraph,   Config, Node, TripleStore, Edge
#from node import Node
from layout import footer
import json
import introspector



config = Config(
  # height=200, width=400,
  
  #maxZoom=2,
#minZoom=0.1,
  #initialZoom=1.5,
  
  nodeHighlightBehavior=True,
  #highlightColor="#F7A7A6",
  directed=True,
  collapsible=True)

import streamlit as st
import streamlit.components.v1 as components

from typing import List, Set


  
# class Node:
#   def __init__(self,
#               id,
#               title=None, # displayed if hovered
#               label=None, # displayed inside the node
#               color=None,
#               shape="dot",
#               size=25,
#               **kwargs
#                ):
#     self.id=id
#     if not title:
#       self.title=id
#     else:
#      self.title=title
#     self.label = label
#     self.shape=shape # # image, circularImage, diamond, dot, star, triangle, triangleDown, hexagon, square and icon
#     self.size=size
#     self.color=color #FDD2BS #F48B94 #F7A7A6 #DBEBC2
#     self.__dict__.update(**kwargs)

#   def to_dict(self):
#     return self.__dict__
  
# class Edge:
#   """
#   https://visjs.github.io/vis-network/docs/network/edges.html
#   """
#   def __init__(self,
#                source,
#                target,
#                color="#FFF7A6",
#                arrows_to=True,
#                arrows_from=False,
#                **kwargs
#                ):
#     self.source=source
#     self.__dict__['from']=source
#     self.to=target
#     self.color=color
#     self.arrows={"to": arrows_to, "from": arrows_from}
#     self.__dict__.update(**kwargs)

#   def to_dict(self):
#     return self.__dict__

# class Triple:
#   def __init__(self, subj: Node, pred: Edge, obj:Node ) -> None:
#     self.subj = subj
#     self.pred = pred
#     self.obj = obj

# class TripleStore:
#   def __init__(self) ->None:
#     self.nodes_set: Set[Node] = set()
#     self.edges_set: Set[Edge] = set()
#     self.triples_set: Set[Triple] = set()

#   def add_triple(self, node1, link, node2, image=""):
#     nodeA = Node(id=node1, image=image)
#     nodeB = Node(id=node2)
#     edge = Edge(source=nodeA.id, target=nodeB.id, title=link)  # linkValue=link
#     triple = Triple(nodeA, edge, nodeB)
#     self.nodes_set.update([nodeA, nodeB])
#     self.edges_set.add(edge)
#     self.triples_set.add(triple)

#   def getTriples(self)->Set[Triple]:
#     return self.triples_set

#   def getNodes(self)->Set[Node]:
#     return self.nodes_set

#   def getEdges(self)->Set[Edge]:
#     return self.edges_set

def load_graph_json(intr_file):
    nodes = []
    edges = []
    intr_store = TripleStore()
    alink = ""
    if 'link' in intr_file:
      alink = f"<a href=\"{intr_file['link']}\">LINKE</a>"
    m =  Node(id=intr_file["name"],
              label=intr_file["name"] ,
              title=alink,
              shape="circularImage",
              image=intr_file["img"])    
    nodes.append(m )
    for sub_graph in intr_file["children"]:
      nodes.append(Node(id=sub_graph["name"]))
      edges.append(Edge(source=sub_graph["name"], target=intr_file["name"], label="subgroup_of"))
      for node in sub_graph["children"]:
        nodes.append(
          Node(id=node["hero"],
               title=node["link"],
               shape="circularImage",
               image=node["img"],
               group=sub_graph["name"],
               )
        )
        d = Edge(source=node["hero"], target=sub_graph["name"], label="blongs_to")
        #st.write(d)
        edges.append(d)
        # st.dataframe(nodes)    
    return nodes, edges


def load_graph_data(filename):
    nodes = []
    edges = []
    with open(filename, encoding="utf8") as f:
      intr_file = json.loads(f.read())
      return load_graph_json(intr_file)

def cleanup(store): #clean up the store!
  ids = {}
  nodes =[]
  edges =[]
  for x in store.getNodes():
    if x.id not in ids:
      #st.write("OK",x)
      ids[x.id] =x
      nodes.append(x)
    else:
      #st.write("OK",x)
      pass
        
  for x in store.getEdges():        
    dd = x.__dict__
    ida = "|".join( [
      dd[k] for k in ["from","to","title"
                      ]
    ])
    if ida not in ids:
      ids[ida]=1
      #st.write(ida,x)
      edges.append(x)
      
  agraph(list(nodes), (edges ), config)

    
def get_inspired():
  sparql = SPARQLWrapper("http://dbpedia.org/sparql")

  query_string = """
  SELECT ?name_pe1_en ?rel_en ?name_pe2_en
  WHERE {
    {
         SELECT ?name_p1 ?rel ?name_p2
         WHERE {
             ?p1 a foaf:Person .
             ?p1 dbo:influencedBy ?p2 .
             ?p2 a foaf:Person .
             ?p1 foaf:name ?name_p1 .
             ?p2 foaf:name ?name_p2 .
            dbo:influencedBy rdfs:label ?rel .
            }
         LIMIT 100
    }
    UNION
    {
         SELECT ?name_p1 ?rel ?name_p2
         WHERE {
            ?p1 a foaf:Person .
            ?p1 dbo:influenced ?p2 .
            ?p2 a foaf:Person .
            ?p1 foaf:name ?name_p1 .
            ?p2 foaf:name ?name_p2 .
            dbo:influenced rdfs:label ?rel .
        }
     LIMIT 100
    }
    FILTER ( LANG(?name_p1) = "en" && LANG(?rel) = "en" && LANG(?name_p2) = "en" )
    BIND ( STR(?name_p1) AS ?name_pe1_en )
    BIND ( STR(?rel) AS ?rel_en )
    BIND ( STR(?name_p2) AS ?name_pe2_en )
  }
  """

  sparql.setQuery(query_string)
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  store = TripleStore()
  for result in results["results"]["bindings"]:
    node1 = result["name_pe1_en"]["value"]
    link = result["rel_en"]["value"]
    node2 = result["name_pe2_en"]["value"]
    store.add_triple(node1, link, node2)
  return store

def app():
  #footer()
  #st.title("Graph Example")
  #st.sidebar.title("Welcome")

  code = st.sidebar.text_area("code",key="code")
  if st.sidebar.button("json"):
    st.code(code)
    data = json.loads(code)
    nodes,edges = load_graph_json(data)
    agraph(nodes, edges, config)

  if st.sidebar.button("ttl"):
    st.code(code)
    graph = Graph()
    store = TripleStore()
    graph.parse(data=code,format="ttl")
    for subj, pred, obj in graph:
      store.add_triple(subj, pred, obj, "")

    return cleanup(store)
  #if st.sidebar.button("python"):
  #  eval(code)

  store = introspector.get_input()
  nodes = len(list(store.getNodes()))
  aorder = [    "Introspector",     "Message",   ]
  if nodes>1:
    aorder.reverse()
  aorder.extend(["Inspirationals", "Marvel",])
  
  query_type = st.sidebar.selectbox("Query Type: ", aorder,
                                    ) # could add more stuff here later on or add other endpoints in the sidebar.
  
  if query_type=="Inspirationals":
    st.subheader("Inspirationals")
    with st.spinner("Loading data"):
      store = get_inspired()
      st.write("Nodes loaded: " + str(len(store.getNodes())))
    st.success("Done")
    agraph(list(store.getNodes()), (store.getEdges() ), config)
  if query_type=="Message":
    st.subheader("Message")
    with st.spinner("Loading data"):
      store = introspector.get_input()
      st.write("Nodes loaded: " + str(len(store.getNodes())))
    st.success("Done")
    return cleanup(store)


  if query_type=="Marvel":
    #based on http://marvel-force-chart.surge.sh/
    nodes,edges = load_graph_data("./marvel.json")
    agraph(nodes,edges, config)
  if query_type=="Introspector":
    nodes,edges = load_graph_data("./introspector.json")
    agraph(nodes,edges, config)
    #return cleanup(store)

  
# st.write("You can find more examples in the [docs]()")

if __name__ == '__main__':
    app()
