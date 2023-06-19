import ppl
import numpy as np
import z3
import time

def readfile(textfile):
#read file and get loop
  file=open(textfile,mode='r')
  lines=file.readlines()
  vars=lines[0].split()
  cons=lines[1].split()
  trans=lines[2].split()
  return vars,cons,trans

def matchvars(vars,varlist):
#find vars in list
  pplnum1=[]
  pplnum2=[]
  for i in vars: 
    for j in list(range(0,len(varlist))):
      if i == varlist[j]:
         pplnum1.append(j)
  for i in pplnum1:
    pplnum2.append(i+9)
  pplnum=pplnum1+pplnum2
  return pplnum

def toeq(cons,trans):
#trans string to ppl.eq
  #for i in cons:
   # conslist.append(eval(i))
  #for i in trans:
   # e=i.split("==")
    #if(len(e)==2):
     # e1=e[0]+">="+e[1]
      #e2=e[0]+"<="+e[1]
      #conslist.append(eval(e1))
      #conslist.append(eval(e2))
    #else:
     # conslist.append(eval(i))  
  lp=cons+trans
  for i in lp:
    e=i.split("==")
    if(len(e)==2):
      e1=e[0]+">="+e[1]
      e2=e[0]+"<="+e[1]
      conslist.append(eval(e1))
      conslist.append(eval(e2))
    else:
      conslist.append(eval(i))  
  return 


def getcslist_str(constlist):
#trans ppl.eq to str
  for i in constlist:
    list_str.append(i.__str__())
  return
  

def getconsnum(str):
#get coeff of constant
  num=""
  le=len(str)
  for i in list(range(0,le)):
    if(str[i]=='+' or str[i]=='-'):
      no=i
      num+=str[i]
      for j in list(range(no+1,le)):
        if(str[j].isdigit()):
          num+=(str[j])
        elif (str[j]=='>'):
          break
        else:
          num=""
          break
  if num == "":
    num="0"
  return int(num)

def getallconsnum(list_str):
#get all coeff of constants
  for i in list_str:
    numlist.append(getconsnum(i))
  return

def getallvarsnum(conslist,numlist,pplnum):
#build matrix for loop
  col=0
  row=0
  n=2*vn
  m=len(conslist)
  ls = np.zeros((m,n+1),int)
  for i in conslist:
    coeff.append(i.coefficients())
  for i in coeff:
    for num in pplnum:
      if(len(i)<=num):
        col=0
        break
      elif (i[num] is None):
        col=0
        break
      else:
        ls[row][col]=i[num]
        col+=1 
    col=0
    row+=1     
  row=0
  for i in numlist:
    ls[row][n]=i
    row+=1
  #print(ls)
  row=0
  return ls

def initclist():
  cl=[]
  for i in list(range(0,2*vn)):
    cl.append(plc[i])
    i+=1
  return cl

def initlmdlist(s,ls):
  lmdlist=[]
  if s=="bound":
    for i in list(range(0,len(ls))):
      try :
        lmdlist.append(pllmd[i])
        i+=1
      except Exception as e:
        return False
  if s=="decrease":
    for i in list(range(0,len(ls))):
      try :
        lmdlist.append(pllmd[i+60])
        i+=1
      except Exception as e:
        return False
  return lmdlist

def farkas(ls,lmdlist):
  res=np.dot(lmdlist,ls) 
  return res

def csinsert(ls,lmdl,type):
#insert cons to constraint system
  if (type=="bound"):
    for i in list(range(0,vn)):
      cs.insert(plc[i]==ls[i])
    for i in list(range(vn,2*vn)):
      cs.insert(ls[i]==0)
    cs.insert(D>=ls[-1])
  if (type=="decrease"):
    for i in list(range(0,2*vn)):
      cs.insert(plc[i]==ls[i]) 
    for i in list(range(0,vn)):
      cs.insert(plc[i]==-plc[i+vn])
    cs.insert(-1>=ls[-1])
  for i in lmdl:
    cs.insert(i>=0)
  return

def getgenerators():
  raylist=getgenerators_ray()
  return raylist
 
def getgenerators_ray():
  raylist=[]
  poly=ppl.C_Polyhedron(cs)
  #print(poly.generators())
  for i in poly.generators():
    if (i.is_ray()):
      #print(i)
      raylist.append(i.coefficients())
  return raylist

def getgenerators_line():
  raylist=[]
  poly=ppl.C_Polyhedron(cs)
  for i in poly.generators():
    if (i.is_line()):
      raylist.append(i.coefficients())
  return raylist

def getgenerators_point():
  raylist=[]
  poly=ppl.C_Polyhedron(cs)
  for i in poly.generators():
    if (i.is_point()):
      raylist.append(i.coefficients())
  return raylist

def cleanraylist(raylist,type):
  rl=[]
  rls=[]
  col=0
  row=0
  m=len(raylist)
  ls = np.zeros((m,2*vn+1),int)
  for i in raylist:
    for num in list(range(18,18+2*vn)):
      fxt=i[num]
      ls[row][col]=fxt
      col+=1
    if(type=="bound"):
      ls[row][col]=i[-1] 
    col=0
    row+=1     
  row=0
  #print(ls)
  #print("generators:")
  #print("***********************")
  l1=ls[[not np.all(ls[i]==0) for i in range(ls.shape[0])],:]
  #print(l1)
  #print("***********************")
  cs.clear()
  return l1

def tclean(raylist):
  rl=[]
  rls=[]
  col=0
  row=0
  m=len(raylist)
  ls = np.zeros((m,2*vn+1),int)
  for i in raylist:
    for num in list(range(18,18+2*vn)):
      fxt=i[num]
      ls[row][col]=fxt
      col+=1
    ls[row][col]=0
    col=0
    row+=1     
  row=0
  #print(ls)
  #print("generators:")
  #print("***********************")
  l1=ls[[not np.all(ls[i]==0) for i in range(ls.shape[0])],:]
  #print(l1)
  #print("***********************")
  cs.clear()
  if(len(l1)==0):
    l1 = np.zeros((1,2*vn+1),int)
  return l1


def getvarpl():
  for i in pn:
    varpl.append(plvar[i])
  varpl.append(1)
  return

def bddiv(r1,r2,r3,ls):
  #r1-ray r2-poinit
  for i in r1:
    rls=np.array(i)
    #print("**************")
    for j in list(range(0,vn)):
      rls[j+vn]=0
      rls[j]=-rls[j]
    rls[-1]=-rls[-1] 
    rls=np.array([rls])
    ls=np.append(ls,rls,axis=0)
  for i in r3:
    rls=np.array(i)
    for j in list(range(0,vn)):
      rls[j+vn]=0
    rls[-1]=-rls[-1] 
    #rls=np.array([rls])
    #ls=np.append(ls,rls,axis=0)
    rls1=rls[:]
    for j in list(range(0,vn)):
      rls1[j]=-rls1[j]
    rls=np.array([rls])
    ls=np.append(ls,rls,axis=0)
    rls1=np.array([rls1])
    ls=np.append(ls,rls1,axis=0)
  for i in r2:
    rls=np.array(i)
    for j in list(range(0,vn)):
      rls[j+vn]=0
      rls[j]=-rls[j]
    rls[-1]=-10  #10 is a variable
    rls=np.array([rls])
    ls=np.append(ls,rls,axis=0)
  ls=ls[[not np.all(ls[i]==0) for i in range(ls.shape[0])],:]
  #print("bound divided:")
  #print("***********************")
  #print(ls)
  #print("***********************")
  return ls 

def dediv(rl,ls):
  for i in rl:
    rls=np.array(i)
    #print(rls)
    for j in list(range(0,vn)):
      rls[j+vn]=rls[j]
      rls[j]=-rls[j]
    rls[-1]=0
    rls=np.array([rls])
    #print(rls)
    ls=np.append(ls,rls,axis=0)
  l1=ls[[not np.all(ls[i]==0) for i in range(ls.shape[0])],:]
  #print("decrease divided:")
  #print("***********************")
  ls=ls[[not np.all(ls[i]==0) for i in range(ls.shape[0])],:]
  #print(ls)
  #print("***********************")
  return ls

def isempty(pn,ls):
  x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14,x15,x16,x17=z3.Reals('x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 x16 x17')
  s1=z3.Solver()
  pv=[]
  for i in list(range(0,2*vn)):
    pv.append(plvar[pn[i]])
  pv.append(1)
  for i in ls:
    res=np.dot(i,pv)
    a=[res>=0]
    ev=str(a)
    s1.add(eval(ev))
  rs=s1.check()
  return rs

     
def rf(bls,dls,blmdl,dlmdl):
  s=z3.Solver()
  for i in list(range(0,vn)):
    eq=[plc[i]==bls[i]]
    a=str(eq)
    s.add(eval(a))
  for i in list(range(vn,2*vn)):
    eq=[bls[i]==0]
    a=str(eq)
    s.add(eval(a))
  eq1=[D>=bls[-1]]
  a1=str(eq1)
  s.add(eval(a1))
  for i in list(range(0,2*vn)):
    eq=[plc[i]==dls[i]]
    a=str(eq)
    s.add(eval(a)) 
  for i in list(range(0,vn)):
    eq=[plc[i]==-plc[i+vn]]
    a=str(eq)
    s.add(eval(a)) 
  eq2=[-1>=dls[-1]]
  a2=str(eq2)
  s.add(eval(a2))
  for i in blmdl:
    eq=[i>=0]
    a=str(eq)
    s.add(eval(a)) 
  for i in dlmdl:
    eq=[i>=0]
    a=str(eq)
    s.add(eval(a))
  res=s.check()
  #print(res)
  if (res==z3.sat):
    #print(s.model())
    rf=1
    #print(s.model())
    #rf=0
    #print(s.model().eval(x17))
    #print(s.model().eval(x18))
    #t=[]
    #t.append(s.model().eval(x17).as_long())
    #t.append(s.model().eval(x18).as_long())
    #t.append(s.model().eval(x19).as_long())
    #t.append(s.model().eval(x20).as_long())
    #print(t)
    #for i in t:
     # if i!=0:
      #  rf=1
    #print("rf:")
    #print(rf)
  else:
    rf=0
  return rf

def findrf(cls):
  #print(cls)
  cl=initclist()
  blmdl=initlmdlist("bound",cls)
  bls=farkas(cls,blmdl)
  dlmdl=initlmdlist("decrease",cls)
  dls=farkas(cls,dlmdl)
  if(blmdl==False or dlmdl==False):
    return 0
  res=rf(bls,dls,blmdl,dlmdl) 
  return res

def prepare():
  getvarpl()
  toeq(cons,trans)
  getcslist_str(conslist)
  getallconsnum(list_str)
  return

def gens(ls,cl,lmdl):
  fc=farkas(ls,lmdl)
  csinsert(fc,lmdl,"bound")
  raylist=getgenerators()
  rl=cleanraylist(raylist,"bound")
  return rl

def tgens(ls,cl,lmdl):
  fc=farkas(ls,lmdl)
  csinsert(fc,lmdl,"decrease")
  rl1=getgenerators_ray()
  rl2=getgenerators_point()
  rl3=getgenerators_line()
  r1=tclean(rl1)
  r2=tclean(rl2)
  r3=tclean(rl3)
  print(r3)
  return r1,r2,r3

def samir(n,ls):
  num=0
  cl=initclist()
  lmdl=initlmdlist("bound",conslist)
  if(lmdl==False):
    print("unknown")
    return 0
  rl=gens(ls,cl,lmdl)
  ls=dediv(rl,ls)
  #print(ls)
  res=findrf(ls)
  if(res!=0):
    num+=1
    print("divided num:",num)
    num=n
    return 0
  else:
    num+=1
  while (num<n):
    cl=initclist()
    lmdl=initlmdlist("bound",ls)
    if(lmdl==False):
      print("unknown")
      return 0
    rl=gens(ls,cl,lmdl)
    ls=dediv(rl,ls)
    #print(ls)
    res=findrf(ls)
    if(res!=0):
      num+=1
      print("divided num:",num)
      num=n
    else:
      num+=1
  print("unknownsamir")
  return

def taslc(n,ls):
  num=0
  cl=initclist()
  lmdl=initlmdlist("decrease",conslist)
  if(lmdl==False):
    print("unknown")
    return 0
  r1,r2,r3=tgens(ls,cl,lmdl)
  ls=bddiv(r1,r2,r3,ls)
  rs=isempty(pn,ls)
  if(rs!=z3.sat):
    print("yes")
    num+=1
    print("divided num:",num)
    num=n
    return 0
  res=findrf(ls)
  if(res!=0):
    num+=1
    print("divided num:",num)
    num=n
  else:
    num+=1
  while (num<n):
    cl=initclist()
    lmdl=initlmdlist("bound",ls)
    if(lmdl==False):
      print("unknown")
      return 0
    r1,r2,r3=tgens(ls,cl,lmdl)
    bddiv(r1,r2,r3,ls)
    ls=bddiv(r1,r2,r3,ls)
    rs=isempty(pn,ls)
    if(rs!=z3.sat):
      print("yes")
      return 0
    res=findrf(ls)
    if(res!=0):
      num+=1
      print("divided num:",num)
      num=n
      return 0
    else:
      num+=1
  print(num)
  return

  
def pal(n,ls):
  num=0
  cl=initclist()
  lmdl1=initlmdlist("bound",conslist)
  if(lmdl1==False):
    print("unknown")
    return 0
  rl=gens(ls,cl,lmdl1)
  lmdl2=initlmdlist("decrease",conslist)
  if(lmdl2==False):
    print("unknown")
    return 0
  r1,r2,r3=tgens(ls,cl,lmdl2)
  ls1=dediv(rl,ls)
  ls=bddiv(r1,r2,r3,ls1)
  #print(ls)
  rs=isempty(pn,ls)
  if(rs!=z3.sat):
    print("yes")
    num+=1
    print("divided num:",num)
    num=n
    return 0
  res=findrf(ls)
  if(res!=0):
    num+=1
    print("divided num:",num)
    num=n
  else:
    num+=1
  while (num<n):
    cl=initclist()
    lmdl1=initlmdlist("bound",ls)
    if(lmdl1==False):
      num+=1
      print("divided num:",num)
      print("unknown")
      return 0
    rl=gens(ls,cl,lmdl1)
    lmdl2=initlmdlist("decrease",ls)
    if(lmdl2==False):
      num+=1
      print("divided num:",num)
      print("unknown")
      return 0
    r1,r2,r3=tgens(ls,cl,lmdl2)
    ls1=dediv(rl,ls)
    ls=bddiv(r1,r2,r3,ls1)
    rs=isempty(pn,ls)
    if(rs!=z3.sat):
      print("yes")
      num+=1
      print("divided num:",num)
      num=n
      return 0
    res=findrf(ls)
    if(res!=0):
      num+=1
      print("divided num:",num)
      num=n
    else:
      num+=1
  return

def st(n,ls):
  num=0
  cl=initclist()
  lmdl1=initlmdlist("bound",conslist)
  if(lmdl1==False):
    print("unknown")
    return 0
  rl=gens(ls,cl,lmdl1)
  ls1=dediv(rl,ls)
  lmdl2=initlmdlist("decrease",ls1)
  if(lmdl2==False):
    print("unknown")
    return 0
  r1,r2,r3=tgens(ls1,cl,lmdl2)
  ls=bddiv(r1,r2,r3,ls1)
  rs=isempty(pn,ls)
  if(rs!=z3.sat):
    print("yes")
    num+=1
    print("divided num:",num)
    num=n
    return 0
  res=findrf(ls)
  if(res!=0):
    num+=1
    print("divided num:",num)
    num=n
  else:
    num+=1
  while (num<n):
    cl=initclist()
    lmdl1=initlmdlist("bound",ls)
    if(lmdl1==False):
      print("divided num:",num)
      print("unknown")
      return 0
    rl=gens(ls,cl,lmdl1)
    ls1=dediv(rl,ls)
    lmdl2=initlmdlist("decrease",ls1)
    if(lmdl2==False):
      num+=1
      print("divided num:",num)
      print("unknown")
      return 0
    r1,r2,r3=tgens(ls1,cl,lmdl2)
    ls1=dediv(rl,ls)
    ls=bddiv(r1,r2,r3,ls1)
    rs=isempty(pn,ls)
    if(rs!=z3.sat):
      print("yes")
      num+=1
      print("divided num:",num)
      num=n
      return 0
    res=findrf(ls)
    if(res!=0):
      num+=1
      print("divided num:",num)
      num=n
    else:
      num+=1
  return

def ts(n,ls):
  num=0
  cl=initclist()
  lmdl2=initlmdlist("decrease",conslist)
  if(lmdl2==False):
    print("divided num:",num)
    print("unknown")
    return 0
  r1,r2,r3=tgens(ls,cl,lmdl2)
  ls1=bddiv(r1,r2,r3,ls)
  lmdl1=initlmdlist("bound",ls1)
  if(lmdl1==False):
    print("divided num:",num)
    print("unknown")
    return 0
  rl=gens(ls1,cl,lmdl1)
  ls=dediv(rl,ls1)
  rs=isempty(pn,ls)
  if(rs!=z3.sat):
    print("yes")
    num+=1
    print("divided num:",num)
    num=n
    return 0
  res=findrf(ls)
  if(res!=0):
    num+=1
    print("divided num:",num)
    num=n
  else:
    num+=1
  while (num<n):
    cl=initclist()
    lmdl2=initlmdlist("decrease",ls)
    if(lmdl2==False):
      print("divided num:",num)
      print("unknown")
      return 0
    r1,r2,r3=tgens(ls,cl,lmdl2)
    ls1=bddiv(r1,r2,r3,ls)
    lmdl1=initlmdlist("bound",ls1)
    if(lmdl1==False):
      num+=1
      print("divided num:",num)
      print("unknown")
      return 0
    rl=gens(ls1,cl,lmdl1)
    ls=dediv(rl,ls1)
    rs=isempty(pn,ls)
    if(rs!=z3.sat):
      print("yes")
      num+=1
      print("divided num:",num)
      num=n
      return 0
    res=findrf(ls)
    if(res!=0):
      num+=1
      print("divided num:",num)
      num=n
    else:
      num+=1
  return

def checkun(ls):
  x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14=z3.Reals('x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14')
  pl=[x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14]
  vl1=[]
  vl2=[]
  for i in list(range(0,2*vn)):
    vl1.append(pl[i])
  vl1.append(1)
  for i in list(range(vn,3*vn)):
    vl2.append(pl[i])
  vl2.append(1)
  ls1=[]
  ls2=[]
  for i in ls:
    ls1.append((np.dot(i,vl1)>=0))
  #ls1.append(-x1>=0)
  for i in ls:
    ls2.append((np.dot(i,vl2)>=0))
  #ls2.append(-x3>=0)
  r1=z3.And(ls1)
  r2=z3.And(ls2)
  r=z3.Implies(r1,r2)
  #print(r) #output imply
  s=z3.Solver()
  if(vn==1):
    t=z3.ForAll([x0,x1],z3.Exists(x2,r))
    s.add(t)
  if(vn==2):
    t=z3.ForAll([x0,x1,x2,x3],z3.Exists([x4,x5],r))
    s.add(t)
  if(vn==3):
    t=z3.ForAll([x0,x1,x2,x3,x4,x5],z3.Exists([x6,x7,x8],r))
    s.add(t)
  if(vn==4):
    t=z3.ForAll([x0,x1,x2,x3,x4,x5,x6,x7],z3.Exists([x8,x9,x10,x11],r))
    s.add(t)
  if(vn==5):
    t=z3.ForAll([x0,x1,x2,x3,x4,x5,x6,x7,x8,x9],z3.Exists([x10,x11,x12,x13,x14],r))
    s.add(t)
  return s.check()

def checkpal(n,ls,cl,num):
  sr=isempty(pn,ls)
  if(sr!=z3.sat):
    print("termination")
    num=n
    return 0
  rs=checkun(ls)
  if(rs==z3.sat):
    print("untermination")
    num=n
    return 0
  else:
    num+=1
  while (num<n):
    lmdl1=initlmdlist("bound",ls)
    if(lmdl1==False):
      num+=1
      print("divided num:",num)
      print("unknown")
      return 0
    rl=gens(ls,cl,lmdl1)
    lmdl2=initlmdlist("decrease",ls)
    if(lmdl2==False):
      num+=1
      print("divided num:",num)
      print("unknown")
      return 0
    r1,r2,r3=tgens(ls,cl,lmdl2)
    ls1=dediv(rl,ls)
    ls=bddiv(r1,r2,r3,ls1)
    sr=isempty(pn,ls)
    if(sr!=z3.sat):
      print("termination")
      num=n
      return 0
    rs=checkun(ls)
    if(rs==z3.sat):
      print("untermination")
      num=n
      return 0
    else:
      num+=1
  print("unknwonpal")
  return 

def checkst(n,ls,cl,num):
  sr=isempty(pn,ls)
  if(sr!=z3.sat):
    print("termination")
    num=n
    return 0
  rs=checkun(ls)
  if(rs==z3.sat):
    print("untermination")
    num=n
    return 0
  else:
    num+=1
  while (num<n):
    lmdl1=initlmdlist("bound",ls)
    if(lmdl1==False):
      num+=1
      print("divided num:",num)
      print("unknown")
      return 0
    rl=gens(ls,cl,lmdl1)
    ls1=dediv(rl,ls)
    lmdl2=initlmdlist("decrease",ls1)
    if(lmdl2==False):
      num+=1
      print("divided num:",num)
      print("unknown")
      return 0
    r1,r2,r3=tgens(ls1,cl,lmdl2)
    ls1=dediv(rl,ls)
    ls=bddiv(r1,r2,r3,ls1)
    sr=isempty(pn,ls)
    if(sr!=z3.sat):
      print("termination")
      num=n
      return 0
    rs=checkun(ls)
    if(rs==z3.sat):
      print("untermination")
      num=n
      return 0
    else:
      num+=1
  print("unknwonst")
  return

def checkts(n,ls,cl,num):
  sr=isempty(pn,ls)
  if(sr!=z3.sat):
    print("termination")
    num=n
    return 0
  rs=checkun(ls)
  if(rs==z3.sat):
    print("untermination")
    num=n
    return 0
  else:
    num+=1
  while (num<n):
    lmdl2=initlmdlist("decrease",ls)
    if(lmdl2==False):
      num+=1
      print("divided num:",num)
      print("unknown")
      return 0
    r1,r2,r3=tgens(ls,cl,lmdl2)
    ls1=bddiv(r1,r2,r3,ls)
    lmdl1=initlmdlist("bound",ls1)
    if(lmdl1==False):
      num+=1
      print("divided num:",num)
      print("unknown")
      return 0
    rl=gens(ls1,cl,lmdl1)
    ls=dediv(rl,ls1)
    sr=isempty(pn,ls)
    if(sr!=z3.sat):
      print("termination")
      num=n
      return 0
    rs=checkun(ls)
    if(rs==z3.sat):
      print("untermination")
      num=n
      return 0
    else:
      num+=1
  print("unknownts")
  return

def fp(ls,vn):
  x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14=z3.Reals('x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14')
  pl=[x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14]
  vl1=[]
  for i in list(range(0,2*vn)):
    vl1.append(pl[i])
  vl1.append(1)
  ls1=[]
  for i in ls:
    ls1.append((np.dot(i,vl1)>=0))
  for i in list(range(0,vn)):
    ls1.append(pl[i]==pl[i+vn])
  s=z3.Solver()
  for i in ls1:
    s.add(i)
  res=s.check()
  return res

def untermination(type,n,ls):
  num=0
  cl=initclist()
  FP=fp(ls,vn)
  if(FP==z3.sat):
    print("untermination:has fixedpoint")
    return 0
  else:
    if(type==pal):
      checkpal(n,ls,cl,num)
    if(type==ts):
      checkts(n,ls,cl,num)
    if(type==st):
      checkst(n,ls,cl,num)
    if(type==taslc):
      checkst(n,ls,cl,num)
    return 0
  return 


conslist=[]
list_str=[]
numlist=[]
coeff=[]
varcoeff=[]
varpl=[]
varlist=['x','y','z','n','p','q','a','b','c',
'x1','y1','z1','n1','p1','a1','b1','c1']
clist=['C1','C2','C3','C4']
llist=['l100','l101','l102','l103','l104','l105',
'l106','l107','l108','l109','l110','l111','l112','l113','l114',
'l200','l201','l202','l203','l204','l205','l206','l207','l208',
'l209','l210','l211','l212','l213','l214']
vars,cons,trans=readfile('1')
vn=len(vars)
x=ppl.Variable(0)
y=ppl.Variable(1)
z=ppl.Variable(2)
n=ppl.Variable(3)
p=ppl.Variable(4)
q=ppl.Variable(5)
a=ppl.Variable(6)
b=ppl.Variable(7)
c=ppl.Variable(8)
x1=ppl.Variable(9)
y1=ppl.Variable(10)
z1=ppl.Variable(11)
n1=ppl.Variable(12)
p1=ppl.Variable(13)
q1=ppl.Variable(14)
a1=ppl.Variable(15)
b1=ppl.Variable(16)
c1=ppl.Variable(17)
C1=ppl.Variable(18)
C2=ppl.Variable(19)
C3=ppl.Variable(20)
C4=ppl.Variable(21)
C5=ppl.Variable(22)
C6=ppl.Variable(23)
C7=ppl.Variable(24)
C8=ppl.Variable(25)
C9=ppl.Variable(26)
C10=ppl.Variable(27)
l100=ppl.Variable(28)
l101=ppl.Variable(29)
l102=ppl.Variable(30)
l103=ppl.Variable(31)
l104=ppl.Variable(32)
l105=ppl.Variable(33)
l106=ppl.Variable(34)
l107=ppl.Variable(35)
l108=ppl.Variable(36)
l109=ppl.Variable(37)
l110=ppl.Variable(38)
l111=ppl.Variable(39)
l112=ppl.Variable(40)
l113=ppl.Variable(41)
l114=ppl.Variable(42)
l115=ppl.Variable(43)
l116=ppl.Variable(44)
l117=ppl.Variable(45)
l118=ppl.Variable(46)
l119=ppl.Variable(47)
l120=ppl.Variable(48)
l121=ppl.Variable(49)
l122=ppl.Variable(50)
l123=ppl.Variable(51)
l124=ppl.Variable(52)
l125=ppl.Variable(53)
l126=ppl.Variable(54)
l127=ppl.Variable(55)
l128=ppl.Variable(56)
l129=ppl.Variable(57)
l130=ppl.Variable(58)
l131=ppl.Variable(59)
l132=ppl.Variable(60)
l133=ppl.Variable(61)
l134=ppl.Variable(62)
l135=ppl.Variable(63)
l136=ppl.Variable(64)
l137=ppl.Variable(65)
l138=ppl.Variable(66)
l139=ppl.Variable(67)
l140=ppl.Variable(68)
l141=ppl.Variable(69)
l142=ppl.Variable(70)
l143=ppl.Variable(71)
l144=ppl.Variable(72)
l145=ppl.Variable(73)
l146=ppl.Variable(74)
l147=ppl.Variable(75)
l148=ppl.Variable(76)
l149=ppl.Variable(77)
l150=ppl.Variable(78)
l151=ppl.Variable(79)
l152=ppl.Variable(80)
l153=ppl.Variable(81)
l154=ppl.Variable(82)
l155=ppl.Variable(83)
l156=ppl.Variable(84)
l157=ppl.Variable(85)
l158=ppl.Variable(86)
l159=ppl.Variable(87)
l200=ppl.Variable(88)
l201=ppl.Variable(89)
l202=ppl.Variable(90)
l203=ppl.Variable(91)
l204=ppl.Variable(92)
l205=ppl.Variable(93)
l206=ppl.Variable(94)
l207=ppl.Variable(95)
l208=ppl.Variable(96)
l209=ppl.Variable(97)
l210=ppl.Variable(98)
l211=ppl.Variable(99)
l212=ppl.Variable(100)
l213=ppl.Variable(101)
l214=ppl.Variable(102)
l215=ppl.Variable(103)
l216=ppl.Variable(104)
l217=ppl.Variable(105)
l218=ppl.Variable(106)
l219=ppl.Variable(107)
l220=ppl.Variable(108)
l221=ppl.Variable(109)
l222=ppl.Variable(110)
l223=ppl.Variable(111)
l224=ppl.Variable(112)
l225=ppl.Variable(113)
l226=ppl.Variable(114)
l227=ppl.Variable(115)
l228=ppl.Variable(116)
l229=ppl.Variable(117)
l230=ppl.Variable(118)
l231=ppl.Variable(119)
l232=ppl.Variable(120)
l233=ppl.Variable(121)
l234=ppl.Variable(122)
l235=ppl.Variable(123)
l236=ppl.Variable(124)
l237=ppl.Variable(125)
l238=ppl.Variable(126)
l239=ppl.Variable(127)
l240=ppl.Variable(128)
l241=ppl.Variable(129)
l242=ppl.Variable(130)
l243=ppl.Variable(131)
l244=ppl.Variable(132)
l245=ppl.Variable(133)
l246=ppl.Variable(134)
l247=ppl.Variable(135)
l248=ppl.Variable(136)
l249=ppl.Variable(137)
l250=ppl.Variable(138)
l251=ppl.Variable(139)
l252=ppl.Variable(140)
l253=ppl.Variable(141)
l254=ppl.Variable(142)
l255=ppl.Variable(143)
l256=ppl.Variable(144)
l257=ppl.Variable(145)
l258=ppl.Variable(146)
l259=ppl.Variable(147)
D=ppl.Variable(148)
plvar=[x,y,z,n,p,q,a,b,c,
x1,y1,z1,n1,p1,q1,a1,b1,c1]
plc=[C1,C2,C3,C4,C5,C6,C7,C8,C9,C10]
cnum=[18,19,20,21,22,23,24,25,26,27]
pllmd=[l100,l101,l102,l103,l104,l105,l106,l107,l108,l109,l110,l111,l112,l113,l114,l115,l116,l117,l118,l119,l120,l121,l122,l123,l124,l125,l126,l127,l128,l129,l130,l131,l132,l133,l134,l135,l136,l137,l138,l139,l140,l141,l142,l143,l144,l145,l146,l147,l148,l149,l150,l151,l152,l153,l154,l155,l156,l157,l158,l159,
l200,l201,l202,l203,l204,l205,l206,l207,l208,l209,l210,l211,l212,l213,l214,l215,l216,l217,l218,l219,l220,l221,l222,l223,l224,l225,l226,l227,l228,l229,l230,l231,l232,l233,l234,l235,l236,l237,l238,l239,l240,l241,l242,l243,l244,l245,l246,l247,l248,l249,l250,l251,l252,l253,l254,l255,l256,l257,l248,l259]
x18,x19,x20,x21,x22,x23,x24,x25,x26,x27,x28,x29,x30,x31,x32,x33,x34,x35,x36,x37,x38,x39,x40,x41,x42,x43,x44,x45,x46,x47,x48,x49,x50,x51,x52,x53,x54,x55,x56,x57,x58,x59,x60,x61,x62,x63,x64,x65,x66,x67,x68,x69,x70,x71,x72,x73,x74,x75,x76,x77,x78,x79,x80,x81,x82,x83,x84,x85,x86,x87,x88,x89,x90,x91,x92,x93,x94,x95,x96,x97,x98,x99,x100,x101,x102,x103,x104,x105,x106,x107,x108,x109,x110,x111,x112,x113,x114,x115,x116,x117,x118,x119,x120,x121,x122,x123,x124,x125,x126,x127,x128,x129,x130,x131,x132,x133,x134,x135,x136,x137,x138,x139,x140,x141,x142,x143,x144,x145,x146,x147,x148=z3.Reals('x18 x19 x20 x21 x22 x23 x24 x25 x26 x27 x28 x29 x30 x31 x32 x33 x34 x35 x36 x37 x38 x39 x40 x41 x42 x43 x44 x45 x46 x47 x48 x49 x50 x51 x52 x53 x54 x55 x56 x57 x58 x59 x60 x61 x62 x63 x64 x65 x66 x67 x68 x69 x70, x71 x72 x73 x74 x75 x76 x77 x78 x79 x80 x81 x82 x83 x84 x85 x86 x87 x88 x89 x90 x91 x92 x93 x94 x95 x96 x97 x98 x99 x100 x101 x102 x103 x104 x105 x106 x107 x108 x109 x110 x111 x112 x113 x114 x115 x116 x117 x118 x119 x120 x121 x122 x123 x124 x125 x126 x127 x128 x129 x130 x131 x132 x133 x134 x135 x136 x137 x138 x139 x140 x141 x142 x143 x144 x145 x146 x147 X148')
#x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14,x15,x16=z3.Reals('x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 x16')
x1,y1,z1,n1,p1,a1,b1,c1
pn=matchvars(vars,varlist)
cs=ppl.Constraint_System()
getvarpl()
toeq(cons,trans)
getcslist_str(conslist)
getallconsnum(list_str)
ls=getallvarsnum(conslist,numlist,pn)
#print("***********************")
#print("method:samir")
#print(findrf(ls))
#samir(5,ls)
#print("***********************")
#print("***********************")
#print("method:taslc")
#taslc(5,ls)
#untermination(taslc,5,ls)
#print("***********************")
s1=time.time()
print("***********************")
print("method:pal")
pal(5,ls)
#untermination(pal,5,ls)
s2=time.time()
print("time:")
print('%.3fs'% (s2-s1))
print("***********************")
print("***********************")
print("method:st")
st(5,ls)
#untermination(st,5,ls)
s3=time.time()
print('%.3fs'% (s3-s2))
print("***********************")
print("***********************")
print("method:ts")
ts(5,ls)
#untermination(ts,5,ls)
s4=time.time()
print('%.3fs'% (s4-s3))
print("***********************")
