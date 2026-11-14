#This file is meant to contain any code to make highly repetitive tasks 
# done throughout the app take up much less space in the main code.

#Written by Nicholas Baker

from contextlib import chdir
import os
from PySide6.QtWidgets import QWidget
import sqlite3

#Takes a 2d list of SQLite queries (str) and their parameters (tuple) and executes them.
#Think of it like passing in the parameters for cursor.execute, but for multiple calls.
# 
# Example: [["select * from table where x = ?", ("3",)], ["delete from table", ()]] 
#
#Returns a 2d list containing the results of each query.
def executeQueries(queries):
    results = list()

    with chdir(os.path.dirname(__file__)):
        try:
            conn = sqlite3.connect("SettingsDB.db")
            cursor = conn.cursor()
            for q in queries:
                data = cursor.execute(q[0], q[1])
                results.append(data.fetchall())
            conn.commit()
        except sqlite3.Error as e:
            print(e)
            if len(results) == 0: 
                return []
        finally:
            conn.close()
    return results

#Accepts a QWidget and returns the first ancestor
#of the widget that is an instance of parentClass  
def getAncestor(widget, targetAncestor):
    currAncestor = widget.parent()
    while currAncestor.__class__.__name__ != targetAncestor:
        print(currAncestor.__class__.__name__)
        currAncestor = currAncestor.parent()
    return currAncestor