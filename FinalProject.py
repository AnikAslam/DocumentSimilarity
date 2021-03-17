import sys
import numpy as np
import urllib.request
import re
import string
import random
from itertools import combinations

#We first load the required libraries and the files containing the documents.
infile = open(str(sys.argv[1]),"r") #doc_file argument
#keeping document in memory
docs = []
for line in infile: 
  docs.append(str(line.strip()).lower())
#print("Number of documents: %d"%len(docs))
#print(docs)
infile.close()

#Document into  𝑘 -shingles, and we hash them to their integer values
k = 5 #k for shingles

shingle_id = {}
id_shingle = []
m = []
ids = 0

total_shingles = 0

for d in docs:
  #removing whitespace
  d_new = ''.join(c for c in d if c.isalnum())
  char_shing = [d_new[i:i+k] for i in range(len(d_new)-k+1)]
  total_shingles += len(char_shing)
  sid = set()
  for sh in char_shing:
    if sh not in shingle_id:
      shingle_id[sh]=ids
      id_shingle.append(sh)
      ids=ids+1
    sid.add(shingle_id[sh])
  m.append(sid)

#Defining Jaccord Similarity
def jaccardSimilarity(d1, d2):
  if len(d1)==0 or len(d2)==0:
    return 0.0
  else:
    intersection = d1.intersection(d2)
    union = d1.union(d2)
    return float(len(intersection))/float(len(union))

#Min-Hashing signature matrix for a given number  𝑛  of permutations.Implementing similarity estimation based on min-hash (permutation)
def minHash(doc, perm):
  for d in perm:
    if d in doc: return d

def genSignatureMatrix(m, n):
  perm = list(range(len(id_shingle)))
  S = []
  for i in range(n):
    S.append([])
    random.shuffle(perm)
    for doc in m:
      mh = minHash(doc,perm)
      S[i].append(mh)
  return S

def minHashSimilarity(S,d1,d2):
  n = len(S)
  c = 0
  for i in range(n):
    if S[i][d1]==S[i][d2]: c += 1
  return float(c)/float(n)

n = 200

S = genSignatureMatrix(m,n)

for d1 in range(len(m)):
	for d2 in range(len(m)):
		mh_sim = minHashSimilarity(S,d1,d2)
		j_sim = jaccardSimilarity(m[d1],m[d2])
		#if mh_sim != 0 and j_sim != 0:
		#print ('d%d-d%d min-hash %f jaccard %f'%(d1,d2,mh_sim,j_sim))


#LSH - Locality sensitive hashing
bucketMembers = {}
candidatePairs = [] #Pairs that hash to the same bucket

def bandsToString(bands):
  if len(bands) == 1:
    return [bands[i] for i in range(len)]
  else:
    res = []
    for i in range(len(m)):
      st = ''.join([str(bands[j][i])+ '-' for j in range(len(bands)-1)])
      st += str(bands[len(bands)-1][i])
      if (st not in bucketMembers):
        bucketMembers[st] = [i]
      else:
        bucketMembers[st].append(i)
        candidatePairs.append(st)
      res.append(st)
    return res

bands = [ S[i:i+3] for i in range(0, len(S), 3) ] #Converting signature to bands , number of rows = 3
str_bands = [bandsToString(bands[i]) for i in range(len(bands))]
stored = []
for i in candidatePairs:
  combination = list(combinations(bucketMembers[i], 2))
  for i, j in combination:
    mh_sim = minHashSimilarity(S,i,j)
    j_sim = jaccardSimilarity(m[i],m[j])
    if (j_sim>float(sys.argv[2]) and mh_sim>float(sys.argv[2]) and i != j):
        value = str(i)+" "+str(j)+" "+str(mh_sim)
        value_1 = str(j)+" "+str(i)+" "+str(mh_sim)
        if (value not in stored) and (value_1 not in stored):  #To remove the duplications
            stored.append(value)

stored.sort()
for value in stored:
    print(value)

print()
print('total pairs: %d'%len(stored))
