# -*- coding: utf-8 -*-
"""CS522_InternationalRelations.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ippK-0KooFpsI1-wR30jzQZPAcjaRwKi
"""

# import packages
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from networkx import edge_betweenness_centrality as betweenness
from networkx.algorithms.community.centrality import girvan_newman
from networkx.algorithms.community import kernighan_lin_bisection
from networkx.algorithms import community
import networkx.algorithms.community as nx_comm
#from networkx.algorithms.community import louvain_communities
import itertools

alliance_net=pd.read_csv('alliance_v4.1_by_dyad_yearly.csv')
enemy_net=pd.read_csv('dyadic_mid_4.02.csv')
countryCodes=pd.read_csv('COW country codes.csv')

countryCodes.head()

countryCodesDict={}
for i in range(len(countryCodes)):
  key=countryCodes['StateAbb'][i]
  val=countryCodes['StateNme'][i]
  countryCodesDict[key]=val
countryCodesDict['USR']='Russia'
countryCodesDict['UGD']='Uganda'

def getAllianceDataByYear(year):
    alliance_net_year= alliance_net[alliance_net['year']==year]
    return alliance_net_year.reset_index().drop(columns='index')

def getEnemyDataByYear(year):
    enemy_net_year= enemy_net[enemy_net['year']==year]
    return enemy_net_year.reset_index().drop(columns='index')

def getAllianceGraph(alliance_data_year):
  # get edges
  edgeList=[]
  edgeStrength={}
  for i in range(len(alliance_data_year)):
    u=alliance_data_year['state_name1'][i]
    v=alliance_data_year['state_name2'][i]
    w1,w2,w3,w4=4,3,2,1
    edgeStrength[(u,v)]=w1*float(alliance_data_year['defense'][i])+w2*float(alliance_data_year['neutrality'][i])+w3*float(alliance_data_year['nonaggression'][i])+w4*float(alliance_data_year['entente'][i])
    edgeList.append((u,v,edgeStrength[(u,v)]))

  #print(edgeList)
  #create graph
  G=nx.Graph()
  G.add_weighted_edges_from(edgeList)
  return G,edgeStrength

def getSignedGraph(year):
  ady=getAllianceDataByYear(year)
  G,posEdgeStrength=getAllianceGraph(ady)
  enemy_data_year=getEnemyDataByYear(year)
  #print('pos',posEdgeStrength)
  hostilityLevel={
      0:1, #No militarized action (1)
      1:2, #Threat to use force (2)
      2:2, #Threat to blockade (2)
      3:2, #Threat to occupy terr. (2)
      4:2, #Threat to declare war (2)
      5:2, #Threat to use CBR weapons(2)
      6:2, #Threat to join war (2)
      7:3, #Show of force (3)
      8:3, #Alert (3)
      9:3, #Nuclear alert (3)
      10:3, #Mobilization (3)
      11:3, #Fortify border (3)
      12:4, #Border violation (4)
      13:4, #Blockade (4)
      14:4, #Occupation of territory (4)
      15:4, #Seizure (4)
      16:4, #Attack (4)
      17:4, #Clash (4)
      18:4, #Declaration of war (4)
      19:4, #Use of CBR weapons (4)
      20:5, #Begin interstate war (5)
      21:5 #Join interstate war (5)
  }
  negEdgeStrength={}
  edgeList=[]
  for i in range(len(enemy_data_year)):
    uu=enemy_data_year['namea'][i]
    vv=enemy_data_year['nameb'][i]
    u=countryCodesDict[uu]
    v=countryCodesDict[vv]
    negEdgeStrength[(u,v)]=-1*hostilityLevel[enemy_data_year['mid5hiact'][i]]
    edgeList.append((u,v,-1*hostilityLevel[enemy_data_year['mid5hiact'][i]]))
  #print('neg',negEdgeStrength)
  G.add_weighted_edges_from(edgeList)
  posEdgeStrength.update(negEdgeStrength)
  #print('comb',edgeStrength)
  return G,posEdgeStrength


def visualizeGraph(G,edgeLabel,layout='circular'):
  if layout=='planar':
    nx.draw_planar(G,with_labels=True)
    pos=nx.planar_layout(G)
    if edgeLabel!='':
      nx.draw_networkx_edge_labels(G,pos,edge_labels=edgeLabel)

  elif layout=='kk':
    nx.draw_kamada_kawai(G,with_labels=True)
    pos=nx.kamada_kawai_layout(G)
    if edgeLabel!='':
      nx.draw_networkx_edge_labels(G,pos,edge_labels=edgeLabel)
  else:
    nx.draw_circular(G,with_labels=True)
    pos=nx.circular_layout(G)
    if edgeLabel!='':
      nx.draw_networkx_edge_labels(G,pos,edge_labels=edgeLabel)
  plt.show()

def visualizeSigns(G,edgeStrength):
  nx.draw_kamada_kawai(G,with_labels=True)
  edgeLabel={}
  for key,val in edgeStrength.items():
    if val>=0:
      edgeLabel[key]='+'
    else :
      edgeLabel[key]='-'
  pos=nx.kamada_kawai_layout(G)
  nx.draw_networkx_edge_labels(G,pos,edge_labels=edgeLabel)
  plt.show()

def find_country_rank(G,centrality_measure):
  if centrality_measure=='pagerank':
    try:
      cnt_rank_dict=nx.pagerank(G,max_iter=10000,tol=1e-7)
      countries_sorted=sorted(cnt_rank_dict, key=cnt_rank_dict.get,reverse=True)
      return countries_sorted
    except:
      return []
  elif centrality_measure=='eigen':
    try:
      cnt_rank_dict=nx.eigenvector_centrality(G,max_iter=10000,tol=1e-7,weight='weight')
      countries_sorted=sorted(cnt_rank_dict, key=cnt_rank_dict.get,reverse=True)
      return countries_sorted
    except:
      return []

  elif centrality_measure=='info':
    try:
      cnt_rank_dict=nx.information_centrality(G,max_iter=10000,tol=1e-1)
      countries_sorted=sorted(cnt_rank_dict, key=cnt_rank_dict.get,reverse=True)
      return countries_sorted
    except:
      return []

  #more to be added    

def getWorldLeaderPlot(cnt_meas):
  years=[]
  leader=[]
  for y in range(1901,2013):
    data=getAllianceDataByYear(y)
    G,es=getAllianceGraph(data)
    #print(len(G.nodes()))
    #continue
    lst=find_country_rank(G,cnt_meas)
    years.append(y)
    if len(lst)>0:
      leader.append(lst[0])
      print(years[-1],lst[0:3])
    else: leader.append('')
  return leader


def getUnbalancedTris(G,type=''): # number or percentage (default)
  unstable_triangles=0
  total_triangles=0
  if len(G.nodes())>2: triangles_lt=[list(x) for x in itertools.combinations(G.nodes(),3)]  
  triangles_list=[]
  for tri in triangles_lt:
    u,v,w=tri[0],tri[1],tri[2]
    if G.has_edge(u,v) and G.has_edge(w,v) and G.has_edge(u,w):
      total_triangles+=1
      s1='+' if G[u][v]['weight']>=0 else '-' 
      s2='+' if G[w][v]['weight']>=0 else '-' 
      s3='+' if G[u][w]['weight']>=0 else '-' 
      signlist=[s1,s2,s3] 
      pos=signlist.count('+')
      if(pos==2 or pos==0):
        unstable_triangles+=1
        triangles_list.append([u,v,w])
  print(triangles_list)
  if type=='num':
    if total_triangles!=0: return unstable_triangles
    else: return 0
  if total_triangles!=0: return unstable_triangles/total_triangles
  else: return 0

worldLeaders=getWorldLeaderPlot('pagerank')

worldLeadersDict={}
for c in worldLeaders:
  if c in worldLeadersDict:
    worldLeadersDict[c]+=1
  else:
    worldLeadersDict[c]=1
worldLeadersDict

worldLeaders2=getWorldLeaderPlot('info')
#worldLeaders2

from networkx.algorithms.cluster import average_clustering
def most_central_edge(G):
    centrality = betweenness(G, weight="weight")
    return max(centrality, key=centrality.get)

def find_communities(G):
  comp=girvan_newman(G, most_valuable_edge=most_central_edge)
  return tuple(sorted(c) for c in next(comp))

def getAverageCCPlot():#clustering coefficient
  years=[]
  cc=[]
  for y in range(1901,2013):
    years.append(y)
    data=getAllianceDataByYear(y)
    G,es=getAllianceGraph(data)
    acc=average_clustering(G)
    cc.append(acc)

  plt.plot(years,cc)
  plt.xlabel('Years')
  plt.ylabel('Average Clustering Coefficient')
  plt.show()

getAverageCCPlot()

#G1 (WW1)
alliance_data_1913=getAllianceDataByYear(1913)
alliance_data_1913.head()

allyG_1913,edgeStrength=getAllianceGraph(alliance_data_1913)
#print(edgeStrength)
visualizeGraph(allyG_1913,edgeStrength)
visualizeGraph(allyG_1913,'')

find_country_rank(allyG_1913,'pagerank')
# edge weights impact pagerank a lot

find_communities(allyG_1913)

signed_1913,signedES_1913=getSignedGraph(1913)
visualizeGraph(signed_1913,signedES_1913)

print(signedES_1913)
#signed_1913.nodes()

find_communities(signed_1913)

kernighan_lin_bisection(allyG_1913,weight='weight')

yr=1914
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)

visualizeSigns(signed_1913,signedES_1913)

getUnbalancedTris(signed_1913)

time=[]
num_unstable_triangles=[]
for y in range(1901,2013):  #(1901 to 2012)
  print(y)
  time.append(y)
  G,es=getSignedGraph(y)
  tris=getUnbalancedTris(G)
  #print(tris)
  num_unstable_triangles.append(tris)

plt.plot(time,num_unstable_triangles)
plt.xlabel('Years')
plt.ylabel('% of Unbalanced Triangles')
plt.show()

for i in range(len(time)):
  print(time[i],num_unstable_triangles[i])

timeN=[]
num_unstable_trianglesN=[]
for y in range(1901,2013):  #(1901 to 2012)
  print(y)
  timeN.append(y)
  G,es=getSignedGraph(y)
  tris=getUnbalancedTris(G,'num')
  #print(tris)
  num_unstable_trianglesN.append(tris)

plt.plot(timeN,num_unstable_trianglesN)
plt.xlabel('Years')
plt.ylabel('Number of Unbalanced Triangles')
plt.show()

for i in range(len(time)):
  print(timeN[i],num_unstable_trianglesN[i])

yr=1914
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)

#G2 (WW2)

yr=1938
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)

yr=1939
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)
#kernighan_lin_bisection(grp,weight='weight')

yr=1940
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)



#G3 (Cold War Era)

yr=1987
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)

yr=1988
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)

yr=1989
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)

yr=1990
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)

yr=1991
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)

yr=1992
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)

yr=1999
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)

yr=2000
data=getAllianceDataByYear(yr)
grp,es=getAllianceGraph(data)
find_communities(grp)

