from bs4 import BeautifulSoup


html = """
<html>
    <body>
        <h1>Job Market Analyzer</h1>

        <div class="job-card">
            <h2>Python Developer</h2>
            <h2> hippo </h2>
            <h2>Python Developer</h2>>
            <p>ABC Technologies</p>
        </div>
    </body>
</html>
"""

soup = BeautifulSoup(html, "html.parser")
print(type(soup))

print(soup.prettify())

heading = soup.find("h1")     # find() 只返回第一个匹配结果。
t = soup.find_all("h2" , class_="job-card")   #返回 List ,  class_ 只拿job-card 的 h2

titles = soup.find_all("h2")
print(heading)
print(type(heading))
print(heading.text)

print(type(titles))
print(titles)
print(titles[1].text)

heading = soup.find("h8")
print(type(heading))
print(heading)    # 找不到返回None， 但是 find_all 找不到返回空 []







