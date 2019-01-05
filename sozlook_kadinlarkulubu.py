from sozlook import BeautifulSoup, requests, ConsoleMessage, Entry, re, get_url, json, USER_AGENT, format_entry

HTML = None
TOPIC = None
URL = "http://www.kadinlarkulubu.com/"
FORUM_URL = "http://www.kadinlarkulubu.com/forum/"

def get_topic(topic, page_iter = False):
    global URL
    global HTML
    global TOPIC

    if not page_iter:
        TOPIC = topic
    link = URL + topic
    HTML = get_url(link)

def inject_post(query):
    headers = {
        "Host": "www.kadinlarkulubu.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.kadinlarkulubu.com/forum/",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "37",
        "Cookie": "xf_session=d4361b2dc4d409ab8ebedc790cca276c",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    body = {"_xfToken":"", "date":"", "keywords":query, "users":""}
    r = requests.post("https://www.kadinlarkulubu.com/forum/search/search", data = body, headers=headers)
    content = BeautifulSoup(r.text, "html.parser")
    return content

def kadinlarkulubu_parse_posts(html = None, tid = 0):
    global HTML
    if html is None:
        html = HTML
    entries = []
    print("Şimdi alınıyor: " + '"'+html.title.text+'"')
    if tid != 0:
        tag = html.find("li", id = "post-" + str(tid))
        author = tag["data-author"]
        date = tag.find("span", class_ = "DateTime")
        likes = tag.find("span", class_ = "LikeText")
        post = tag.find("blockquote", class_ = "messageText SelectQuoteContainer ugc baseHtml").text.replace("\n", "").replace("\t", "").replace("\xa0", "")
        if author and date and post != None:
            if likes != None:
                like_count = len(likes.find_all("a"))
            else:
                like_count = 0
            entry = Entry(author, 0, str(date.string), like_count, post, 0)
            entries.append(entry)
            return entries
    ol = html.find("ol", id = "messageList")
    if ol is not None:
        for li in ol.find_all("li"):
            if "id" in li.attrs:
                author = li.find("span", class_ = "style2")
                date = li.find("span", class_ = "DateTime")
                likes = li.find("span", class_ = "LikeText")
                post = li.find("blockquote", class_ = "messageText SelectQuoteContainer ugc baseHtml").text.replace("\n", "").replace("\t", "").replace("\xa0", "")
                if author and date and post != None:
                    if likes != None:
                        like_count = len(likes.find_all("a"))
                    else:
                        like_count = 0
                    entry = Entry(str(author.string), 0, str(date.string), like_count, post, 0)
                    entries.append(entry)
        return entries

def kadinlarklubu_parse_all_posts(html = None, url = ""):
    global HTML
    if html is None:
        html = HTML
    entries = []
    i = 1
    suffix = "page-"
    tmp = html.find("div", class_ = "PageNav")
    if tmp == None:
        entries.extend(kadinlarkulubu_parse_posts(html))
        return entries
    else:
        pages = tmp["data-last"]
    while i <= int(pages):  
        i += 1     
        entries.extend(kadinlarkulubu_parse_posts(html))      
        link = url+suffix+str(i)
        if i <= int(pages):
            html = BeautifulSoup((requests.get(link)).text, "html.parser")
    return entries
    
def kadinlarkulubu_search(query, t_list = [], page_count = 0, iter_mode = False):
    topic_list = t_list
    if not iter_mode:
        html = inject_post(query)
    else:
        html = BeautifulSoup((requests.get(query)).text, "html.parser")
    pages = page_count
    search_results = []
    cm = ConsoleMessage("")
    cm.change_message("Arama sonuçları indiriliyor, toplam indirilen sayfa: " + str(pages))
    cm.write()
    ol = html.find("ol", class_ = "searchResultsList")
    for li in ol:
        if li != "\n":          
            forum_link = li.find("h3", class_ = "title").find("a")["href"]
            if re.findall(r'post-', li["id"]):
                tid = int(li["id"].replace("post-", ""))
                result = (forum_link, tid)
                topic_list.append(result) 
            else:
                result = (forum_link, 0)
                topic_list.append(result)       
    del result
    pages += 1
    navend = html.find("a", string = "Sonraki >")
    if navend != None:
        l_next = navend["href"]
        lst = kadinlarkulubu_search(FORUM_URL + str(l_next), topic_list, pages, True)
        return lst
    print ("\nTüm " + str(pages) + " sayfa da indirildi.")
    for elem in topic_list:
        url = FORUM_URL + elem[0]
        html = BeautifulSoup(requests.get(url).text, "html.parser")
        if re.findall(r'threads', elem[0]):
            parsed = kadinlarklubu_parse_all_posts(html, url)
            search_results.extend(parsed) 
        else:
            parsed = kadinlarkulubu_parse_posts(html, elem[1])
            search_results.extend(parsed)    
    return search_results

