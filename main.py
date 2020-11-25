import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
from streamlit_agraph import agraph, TripleStore, Node, Edge, Config
from layout import footer
import json

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
  footer()
  st.title("Graph Example")
  st.sidebar.title("Welcome")
  query_type = st.sidebar.selectbox("Query Tpye: ", ["Inspirationals", "Marvel"]) # could add more stuff here later on or add other endpoints in the sidebar.
  config = Config(height=600, width=700, nodeHighlightBehavior=True, highlightColor="#F7A7A6", directed=True,
                  collapsible=True)

  if query_type=="Inspirationals":
    st.subheader("Inspirationals")
    with st.spinner("Loading data"):
      store = get_inspired()
      st.write("Nodes loaded: " + str(len(store.getNodes())))
    st.success("Done")
    agraph(list(store.getNodes()), (store.getEdges() ), config)

  if query_type=="Marvel":
    #based on http://marvel-force-chart.surge.sh/
    with open("./marvel.json", encoding="utf8") as f:
      marvel_file = json.loads(f.read())
      marvel_store = TripleStore()
      for sub_graph in marvel_file["children"]:
        marvel_store.add_triple(marvel_file["name"], "has_subgroup", sub_graph["name"], picture=marvel_file["img"])
        for node in sub_graph["children"]:
          node1 = node["hero"]
          link = "blongs_to"
          node2 = sub_graph["name"]
          pic = node["img"]
          marvel_store.add_triple(node1, link, node2, picture=pic)
      agraph(list(marvel_store.getNodes()), (marvel_store.getEdges()), config)


if __name__ == '__main__':
    app()
