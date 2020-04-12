# SQL-Generation-from-Natural-Language

This project uses Spacy, Microsoft SQL Server, Docker, tkinter.

## How it works?
Step 1: Replace keywords such as total number with count or total with sum etc.<br>
Step 2: Remove stop words.<br>
Step 3: Identify text from preloaded words.<br>
Step 4: Process string using Spacy.<br>
Step 5: Lemmatized string creation.<br>
Step 6: Match the sentence with exsisting tables and columns and with synonyms given in the configuration.<br>
Step 7: Split the string using splitter config.<br>
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;a). Create spacy documents for splitted phrases.<br>
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;b). Find entities and columns.<br>
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;c). Find if aggregation is required for entities and columns.<br>
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;d). Use named entities identified earlier to correct the values.<br>
Step 8: Build dictionary and pass dictionary to SQL generator.<br>
Step 9: SQL generator will generate query based on entity column dictionary.<br>
Step 10: Use the generated query to fetch result.<br>

### How to run?
``` python test.py ```<br>
***Note: tkinter must be installed for the gui.***<br>

### Sample Queries
```
students in class 12 and mark 30 in english subject
Show all students with marks greater than 30
students in class 12 and marks less than 50 in english subject in year greater than 2018
students in class 12 and marks less than 50 in english subject
average marks of students in english subject in class 12
average marks in english subject in class 12
student with maximum marks in english subject in class 12
minimum marks in english subject in class 12
total marks of students in class 12 in year 2019
students in class 12 with marks less than 60 in english subject
total marks in class 12 in year 2019
maximum marks in class 12 in year 2019
students in class 12 and 69 marks in english subject
students in class 12 and marks less than 50 in english subject
marks of Manoj Garg student in english subject
student with biology in class 12
marks of Lokesh Lal in english in class 12
maximum marks of vishal gupta in all subject
students with less than 50 marks in class 12
```
### Result
