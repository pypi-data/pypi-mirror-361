"""
## Aiology

Aiology is a package which pressents you four modules :

## 📄 PDF module

This module uses to extract data from pdf files ,or uses pdf data to ask question from ai 
(This module can extract Persian texts too !!)

## 🤖 AI module

You can commiunicate with ai by this module ,this module is a text base module which only 
supported text input ,and output

## 🗃️ Tools modules

By this tools you can make chunks of text ,or document content , and store them in a vector database

You can use database information to ask ai about them

## Author

✍️ Seyed Moied Seyedi

😁 I will be glad to see your tricks 
"""
from .main import PDF
from .main import AI
from .chunk_tool import Chunk
from .vector_database import DataBase