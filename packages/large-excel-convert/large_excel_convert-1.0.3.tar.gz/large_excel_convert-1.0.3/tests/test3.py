# python_calamine 
from pandas import read_excel
from python_calamine.pandas import pandas_monkeypatch


pandas_monkeypatch()

df = read_excel("X101SC24096049-Z01-M-2597066-CP_Compounds.xlsx", engine="calamine")