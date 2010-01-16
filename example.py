import markdown

fin = open("test.md", 'r')
txt = fin.read()
fin.close()
md = markdown.Markdown(extensions=['graphviz'])
print md.convert(txt)
