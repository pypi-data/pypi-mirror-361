from requests import post
import pypdf as pdf
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from os.path import exists
from .vector_database import DataBase
from .chunk_tool import Chunk
from colorama import init , Fore , Style

init(True)

class PDF:
    """
# 📄 PDF

easily extract ,and use your pdf content by this class

## Quick start

PDF class needs four parameters 

`pdf_path -> The path of your pdf file as string`

`use_for_telegram -> Set this option True if you use this for a telegram bot (False as default)`

### ⚠️ If you use this pdf to asking ai relative questions , you need to pass collection_name and collection_directory

`collection_name -> Set this for vector database`

`collection_directory -> Set this for vector database folder`

## ----------------------------------------------------

## Get pdf content example :

```
#import from our module
from Aiology import PDF

#variables
pdf_path = "YOUR_PDF_FILE_PATH"

#define your pdf
pdf = PDF(pdf_path)

#read pdf content
result = pdf.get_pdf_content()

#print result
print(result)
```

## Ask pdf question from ai :

⚠️ WARNING : before asking questions from ai , you need to run *prepare_for_ai* function 

```
#import from our module
from Aiology import PDF , AI

#variables
pdf_path = "YOUR_PDF_FILE_PATH"
gemini_api_key = "YOUR_GEMINI_API_KEY"

#define your pdf
pdf = PDF(pdf_path) # <----- (You can pass collection_name ,and collection_directory parameters now)
pdf.prepare_for_ai(1000) # <----- (Convert your pdf content to small pieces and save them in database collection)

#AI
ai = AI(gemini_api_key)

#ask your question
result = ai.ask_pdf_question("YOUR_QUESTION_TEXT",pdf)

#print result
print(result)
```
    """
    def __init__(self,pdf_path : str,use_for_telegram : bool = False,collection_name : str = "Documents",collection_directory : str = "Database"):
        if not exists(pdf_path):
            raise Exception(f"There is no pdf file in {pdf_path} address !!")
        
        self.telegram_usage = use_for_telegram
        self.collection_name = collection_name
        self.collection_folder = collection_directory
        self.reader = pdf.PdfReader(pdf_path)
        self.pdf_pages_num = self.reader.get_num_pages()
        self.content = ""

        for i in range(self.pdf_pages_num):
            if self.telegram_usage:
                self.content += self.reader.get_page(i).extract_text()
            else:
                self.content += get_display(reshape(self.reader.get_page(i).extract_text()))

    def get_pdf_content(self):
        """
## Get pdf content

This function gets your pdf content and return them back

`get_pdf_content() -> pdf content` 
        """
        return self.content
    
    def get_pdf_page_content(self,page_num : int):
        """
## Get pdf page content

This function gets your pdf content by its page number and return them back

`get_pdf_page_content(page_number : int) -> pdf content of that page` 
        """
        if page_num > self.pdf_pages_num:
            raise Exception(f"This pdf has {self.pdf_pages_num} page(s) , you can't have page {page_num} content !!")
        elif page_num > 0:
            if self.telegram_usage:
                return self.reader.get_page(page_num-1).extract_text()
            else:
                return get_display(reshape(self.reader.get_page(page_num-1).extract_text()))
        else:
            raise Exception(f"{page_num} is an invalid page number !!")
        
    def chunk_pdf_content(self,chunk_size : int = 1000,page_num : int = None):
        """
## make pdf content chunks

This function is used to make chunks of your pdf content

`chunk_pdf_content(chunk_size : int = 1000,page_num : int = None) -> chunks of the pdf (page) content` 
        """
        if page_num != None:
            chunk_content = self.get_pdf_page_content(page_num=page_num)
        else:
            chunk_content = self.content
        
        chunker = Chunk(content=chunk_content , chunk_size=chunk_size)
        return chunker.make_chunk()
    
    def prepare_for_ai(self,chunk_size : int = 1000,chunks_ids : list[str] = None,page_num : int = None):
        """
## Prepare this pdf information for ai

This function is used to prepare this pdf information for ai in database

💡 TIP : Use this function when you wanna ask question about this pdf from ai 

`prepare_for_ai() -> None` 
        """
        chunks = self.chunk_pdf_content(chunk_size=chunk_size , page_num=page_num)
        database = DataBase(collection_name=self.collection_name,database_path=self.collection_folder)
        database.add_collection(chunked_content=chunks,ids=chunks_ids)
    
class AI:
    """
## 🤖 AI

You can easily exteract your pdf files data , then ask the ai everything
about your pdf content by using AI , and it will answer your question immediately

## Quick start

AI class needs two parameters 

`api_key -> The ai api_key , this module only supports Gemini api_keys !!`

`use_for_telegram -> Set this option True if you use this for a telegram bot (False as default)

## ------------------------------------------------------------------------------
```
#import from our module
from Aiology import PDF , AI

#variables
pdf_path = "YOUR_PDF_FILE_PATH"
gemini_api_key = "YOUR_GEMINI_API_KEY"

#define your pdf
pdf = PDF(pdf_path) # <----- (You can pass collection_name ,and collection_directory parameters now)
pdf.prepare_for_ai(1000) # <----- (Convert your pdf content to small pieces and save them in database collection)

#AI
ai = AI(gemini_api_key)

#ask your question
result = ai.ask_pdf_question("YOUR_QUESTION_TEXT",[pdf])

#print result
print(result)
```
    """
    def __init__(self,api_key : str,use_for_telegram : bool = False):
        self.api_key = api_key
        self.telegram_usage = use_for_telegram

    def ask_question(self,text):
        """
## Ask question from ai

By this function , you can send your question ,and receive its answer

`ask_question(text : str) -> response text`
        """
        header = {"Content-Type":"application/json"}

        data = {"contents":[
                        {"parts":
                            [
                                {"text":text},
                            ]
                        }
                    ]}
        
        try:
            res = post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}",
                    headers=header,json=data)
        except:
            raise Exception(f"Internet connection error !!")
        
        if res.ok:
            final_text = ""
            result = res.json()
            for texts in result["candidates"][0]["content"]["parts"]:
                if self.telegram_usage:
                    final_text += texts["text"]
                else:
                    final_text += get_display(reshape(texts["text"]))

            return final_text
        else:
            raise Exception(f"Unexpected error happened !! your error code is {res.status_code}\nContent : {res.content}")

    def ask_pdf_question(self,text : str,pdf_list : list[PDF],language : str = "English",sensivity : int = 6):
        """
## Ask question about your pdf

By this function , you can easily pass your pdf ,and ask different questions about it

`ask_pdf_question(self,text : str,pdf_list : list[PDF],language : str = "English",sensivity : int = 6) -> response text`
        """
        content = ""

        for pdf in pdf_list:
            database = DataBase(collection_name=pdf.collection_name,database_path=pdf.collection_folder)
            query_result = database.get_query_data(search_text=text,n_results=sensivity)
            
            for result in query_result["documents"][0]:
                if content != "":
                    content += f"-{result}"
                else:
                    content += result
            
        print(f"{Style.BRIGHT}{Fore.GREEN}Please wait for ai answer ...")

        prompt = f"""
        You are a helpful bot which can answer my questions using text.
        I'm a non-technical audience , please answer my question comprehensive ,and be sure to break down strike a friendly
        and converstional tone.
        If the context is irrelative to the answer , you may ignore it.
        
        QUESTION : '{text}'
        CONTEXT : '{get_display(reshape(content))}'

        PLEASE ANSWER THIS QUESTION IN {language} WITHOUT ANY EXTRA INFORMATION
        """

        header = {"Content-Type":"application/json"}

        data = {"contents":[
                        {"parts":
                            [
                                {"text":prompt},
                            ]
                        }
                    ]}
        
        try:
            res = post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}",
                    headers=header,json=data)
        except:
            raise Exception(f"Internet connection error !!")
            
        if res.ok:
            final_text = ""
            result = res.json()
            for texts in result["candidates"][0]["content"]["parts"]:
                if self.telegram_usage:
                    final_text += texts["text"]
                else:
                    final_text += get_display(reshape(texts["text"]))

            return final_text
        else:
            raise Exception(f"Unexpected error happened !! your error code is {res.status_code}\nContent : {res.content}")