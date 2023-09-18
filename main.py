import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
from streamlit_agraph import agraph,   Config, Node, TripleStore, Edge
#from node import Node
from layout import footer
import json
import introspector
# st.markdown( """
# <script>alert("hlel");</script>
# <script src="https://cdn.jsdelivr.net/npm/eruda"></script>
# <script>eruda.init();</script>
# """,
#             unsafe_allow_html=True)
            
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


def load_graph_data(filename):
    nodes = []
    edges = []
    with open(filename, encoding="utf8") as f:
      intr_file = json.loads(f.read())
      intr_store = TripleStore()
      #st.write(intr_file)
      #root
      #f"<br><a href="{ intr_file['link'] }">{intr_file["name"]}</a> ",
      alink = f"<a href=\"{intr_file['link']}\">LINKE</a>"

      m =         Node(id=intr_file["name"],
                       label=intr_file["name"] ,
                       title=alink,
                       #title=intr_file['link'],
                       shape="circularImage",
                       image=intr_file["img"])

      st.write(m)
      nodes.append(m    )
      for sub_graph in intr_file["children"]:
        nodes.append(Node(id=sub_graph["name"]))
        edges.append(Edge(source=sub_graph["name"], target=intr_file["name"], label="subgroup_of"))
        for node in sub_graph["children"]:
          nodes.append(Node(id=node["hero"],
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

  store = introspector.get_input()
  nodes = len(list(store.getNodes()))
  aorder = [    "Introspector",     "Message",   ]
  if nodes>1:
    aorder.reverse()
  aorder.extend(["Inspirationals", "Marvel",])
  
  query_type = st.sidebar.selectbox("Query Type: ", aorder,
                                    ) # could add more stuff here later on or add other endpoints in the sidebar.
  config = Config(
    # height=200, width=400,
                  
                  #maxZoom=2,
                  #minZoom=0.1,
                  #initialZoom=1.5,

                  nodeHighlightBehavior=True, highlightColor="#F7A7A6", directed=True,
                  collapsible=True)
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
    agraph(list(store.getNodes()), (store.getEdges() ), config)

  if query_type=="Marvel":
    #based on http://marvel-force-chart.surge.sh/
    nodes,edges = load_graph_data("./marvel.json")
    agraph(nodes,edges, config)
  if query_type=="Introspector":
    nodes,edges = load_graph_data("./introspector.json")
    agraph(nodes,edges, config)



if __name__ == '__main__':
    app()
