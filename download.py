import requests
import urllib.parse
import os

class MvnReqError(Exception):
    pass

def search(query_list=[], format="json", rows=1):
    """ mvn search by resp api

    Args:
        query_list (list, optional): https://central.sonatype.org/search/rest-api-guide/ . Defaults to [].
        format (str, optional): resp format , must be json now. Defaults to "json".
        rows (int, optional): mvn return rows count, only use the first one. Defaults to 1.

    Raises:
        MvnReqError: _description_

    Returns:
        dict: a doc returned by mvn
              empty dict mines not found
    """
    if not query_list:
        return {}
    q_encode = " AND ".join(query_list)
    q_encode = urllib.parse.quote_plus(q_encode)
    url=f"https://search.maven.org/solrsearch/select?q={q_encode}&rows={rows}&wt={format}"
    r = requests.get(url=url)
    resp = {}
    try:
        resp = r.json()
    except:
        raise MvnReqError
    if resp["responseHeader"]["status"]!=0:
        raise MvnReqError
    if resp["response"]["numFound"]==0:
        return {}
    return resp["response"]["docs"][0]

def download_file(url, filepath):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)

def mvn_download(doc, download_path, source_subpath="../sources"):
    """download lib file and source file from mvn

    Args:
        doc (dict): mvn json doc
        download_path (str): download lib to the path
        source_subpath (str, optional): download sources to the path.
                                        Wont download sources if its null or empty.
                                        Defaults to "../sources".
    """
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    if source_subpath and not os.path.exists(source_subpath):
        os.makedirs(source_subpath)

    baseurl = "https://repo1.maven.org/maven2/"
    idpath = doc["g"].replace(".", "/") + "/" + doc["a"] + "/" + doc["v"] + "/"
    filename = doc["a"]+"-"+doc["v"]
    lib_filename = filename+".jar"
    source_filename = ""
    if not (source_subpath is None or source_subpath==""):
        if "-sources.jar" in doc["ec"]:
            source_filename = filename+"-sources.jar"
        elif "-source.jar" in doc["ec"]:
            source_filename = filename+"-source.jar"
    try:
        download_file(f"{baseurl}{idpath}{lib_filename}", f"{download_path}/{lib_filename}")
    except:
        print(f"[X] download {lib_filename} failed from url {baseurl}{idpath}{lib_filename}")
    
    if source_filename:
        try:
            download_file(f"{baseurl}{idpath}{source_filename}", f"{source_subpath}/{source_filename}")
        except:
            print(f"[X] download {source_filename} failed from url {baseurl}{idpath}{source_filename}")

def d4sha1(sha1, download_path):
    """download by lib sha1

    Args:
        sha1 (str): lib jar file sha1
        download_path (str): download lib jar to the path
    """
    sha1 = sha1.strip()
    doc = search([f"1:{sha1}"])
    if not doc:
        print(f"[X] not found for sha1 {sha1}")
        return
    mvn_download(doc, download_path)

def main():
    """demo
    """
    download_path = "."
    sha1list = open("/tmp/sha1.txt").readlines()
    for sha1 in sha1list:
        d4sha1(sha1, download_path)

if __name__ == '__main__':
    main()