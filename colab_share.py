import os
import sys
from github import Github
from tqdm import tqdm
from googletrans import Translator
import json
from nbconvert import HTMLExporter
from nbformat.v4 import to_notebook
import markdown

def list_files(repo, path):
    for file in repo.get_contents(path):
        if file.type == "dir":
            list_files(repo, file.path)
        else:
            print(file.path,file.html_url)
            
            
def add_link_colab(html_link):
    colab={
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\""+html_link+"\" target=\"_blank\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    }
    return colab

def add_link_colab_local(html_link):
    colab={
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/"+html_link+"\" target=\"_blank\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    }
    return colab    


def translate_text(liste):
    translator = Translator()
    return [translator.translate(i,dest='fr').text+"\n" for i in liste]

def remove_colab(js_file,trans=False):
    # translator = Translator()
    cpt=0
    if "metadata" in js_file:
        if 'colab' in js_file['metadata']:
            del js_file['metadata']['colab']
        elif "colab_type" in js_file['cells'][0]['metadata']:
            js_file['cells']=js_file['cells'][1:]
    for cell in tqdm(js_file['cells'],ascii=True,desc='remove_colab'):
        if cell['cell_type'] == "markdown" and trans :
            cell['source'] = translate_text(cell['source'])
            # print(cell.source)
            
            
def make_dir_file_git(lien_except):
    return [{"url":i,"path":'./'+"".join(i.replace('https://github.com/','').split('blob/main/'))} for i in lien_except]
def make_file(lien_except):
    return [i.update({"file":'/'.join(i['path'].split('/')[:-1]),'ipynb':'./'+i['path'].split('/')[-1]}) for i in lien_except]


def update_github(repo,path,ipynb):
    for file in tqdm(repo.get_contents(path),ascii=True,desc=f'Epoch {file.path}'):
        try :
            if file.path.endswith(ipynb):
                # print("except 2",file.path)
                html_test=file.html_url.replace('https://',"https://colab.research.google.com/")
                html_test=html_test.replace('github.com',"github")
                file_content = repo.get_contents(file.path).decoded_content.decode(encoding='UTF-8',errors='strict')
                json_object = json.loads(file_content)
                
                remove_colab(json_object,trans=False)

                json_object['cells'].insert(0,add_link_colab(html_test))
                
                # pour update le repo github documente cette ligne
                repo.update_file(file.path, "one file",json.dumps(json_object,indent=4) , file.sha)

                print(ipynb," done")

            else :
                print("erreur")
        except :
            print('kooo')
            pass

def all_job(repo, path):

    for file in tqdm(repo.get_contents(path),ascii=True,desc='all_job'):
        try :
            if file.type == "dir":
                all_job(repo, file.path)
            elif file.path.endswith(".ipynb"):
                print("1- ",file.name)
                html_test=file.html_url.replace('https://',"https://colab.research.google.com/")
                html_test=html_test.replace('github.com',"github")
                file_content = repo.get_contents(file.path).decoded_content.decode(encoding='UTF-8',errors='strict')
                json_object = json.loads(file_content)
                
                remove_colab(json_object,trans=False)

                json_object['cells'].insert(0,add_link_colab(html_test))
                
                # pour update le repo github documente cette ligne
                repo.update_file(file.path, "auto colab",json.dumps(json_object,indent=4) , file.sha)
                html_job(repo,file,file_content)
                
            
        except :
            print("except 2",file.path)

        
def html_job(repo,file,file_content):
    
    file_name=file.path.replace('ipynb','html')
    exporter = HTMLExporter()
    file_content = to_notebook(json.loads(file_content))
    body, resources = exporter.from_notebook_node(file_content)
    try:
        # file = repo_html.get_contents(file_name)
        
        repo.update_file("Machine-Learning/"+file_name, "update md", body, file.sha)
        print('update',file_name)
    except:
        print('create',file_name)
        repo.create_file("Machine-Learning/"+file_name, "create md", body)
        print('create Done')


def main(repo='',path='',ipynb=''):
    """il faut modifier le nom_user si tu veux changer de user et 
    specifier le repo_name si tu veux specifier un repo en particulier

    Args:
        repo (str, optional): _description_. Defaults to ''.
        path (str, optional): _description_. Defaults to ''.
        ipynb (str, optional): _description_. Defaults to   ''.
    """
    # specifier le nom du repo.
    repo_name = "kplr-training/Machine-Learning"

    # mettre votre clé github
    g = Github("###############")
    user = g.get_user()
       
    repo = g.get_repo(repo_name)           
    all_job(repo, "")


if __name__ == "__main__":

    main(sys.argv)
