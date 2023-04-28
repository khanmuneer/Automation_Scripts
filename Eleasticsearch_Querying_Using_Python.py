#This script allows you to query your elasticsearch system and retrieve data for analysis. 
#Kibana allows you to do analysis but the options are limited. 
#With this you can create a DataFram and do a lot more data science, data enginerring and data analysis taks.


import elasticsearch
import pandas as pd

#this is the query stored elsewhere. It contains a lucene script[https://www.elastic.co/guide/en/kibana/current/lucene-query.html] which is used to retireve data.
from Search_Parameter_GTE import search_param


# Define the Elasticsearch client and search for documents
apikey = 'YOUR API KEY'
uri = 'YOUR URI'
es = elasticsearch.Elasticsearch([uri], api_key=apikey)

#cat.indices --> Returns all indices that match a pattern
indices = es.cat.indices(index="shrink-*.prod-filebeat-*", h="index").split()


results = es.search(index=indices,  body = search_param)

def extract_data(doc):
  #extract data from the Elasticsearch response
  hits = doc.get('hits', {}).get('hits', [])
  result = []
  for hit in hits:
      source = hit.get('_source', {})
      gte = source.get('backend', {}).get('audit', {})
      email = gte.get('subject', None)
      timestamp = source.get('@timestamp', None)
      if email and timestamp:
          result.append({'email': email, 'timestamp': timestamp})
  return result

data = extract_data(results)
df = pd.DataFrame(data)


import elasticsearch
import pandas as pd
from Search_Parameter_GTE import search_param

# Define the Elasticsearch client and search for documents
apikey = 'YOUR API KEY'
uri = 'YOUR URI'
es = elasticsearch.Elasticsearch([uri], api_key=apikey)

# cat.indices --> Returns all indices that match a pattern
# Retrieve the list of Elasticsearch indices that match a specific pattern
indices = es.cat.indices(index="shrink-*.prod-filebeat-*", h="index").split()

# Search for documents in the specified Elasticsearch indices
results = es.search(index=indices,  body = search_param)

def extract_data(doc):
  # Retrieve the relevant fields from each Elasticsearch document
  hits = doc.get('hits', {}).get('hits', [])
  result = []
  for hit in hits:
      source = hit.get('_source', {})
      gte = source.get('backend', {}).get('audit', {})
      email = gte.get('subject', None)
      timestamp = source.get('@timestamp', None)
      if email and timestamp:
          result.append({'email': email, 'timestamp': timestamp})
  return result

# Extract the relevant data from the Elasticsearch search results
data = extract_data(results)

# Convert the extracted data into a pandas DataFrame
df = pd.DataFrame(data)
