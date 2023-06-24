# MixedPartition
This repository has three files:

**1**：Contains an input loop.

**READ.md**: Introduce the whole repository.

**init.py**: Code of mixed partition scheme.

**loops.md**: Shows all experimental loops.

## **How  to wirte input file**

The input file needs three lines:

First line: All variables of the loop.

Second line: All constraint statements of the loop.

Third line: All assignment statements of the loop.

 An example of an input file:

```
x y
x>=y 
x1==2*x y1==y+1
```

## **How  to use**

First: Download the file 1 and init.py

Second: Input the loop in file 1 and run command "python init.py"

Then the program will return the result of termination analysis.

## Experimental Results

All experimental loops are shown in file *loops.md*. Loops in this file come from the following websites and article :

1.Ben-Amram A, Genaim S. On multiphase-linear ranking functions [C]//2017:601-620

2.http://loopkiller.com/irankfinder

3.https://github.com/MinghaiQingtong/PPL_Project/blob/master/Experiments/NestTASLCCom.md

This file shows the comparison of our mixed partition scheme with iRankFinder and LassoRanker. The column "Result" aas three types of records, which "T" represents the loop is termination, "F" represents the loop is non-termination, "U" represents the loop can't be determined by the tool. The column "time" show the full process of a loop  determined. For loops that have the results "F", we do not record the time.
