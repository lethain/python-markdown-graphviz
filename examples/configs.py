import markdown

fin = open("test.md", 'r')
txt = fin.read()
fin.close()
md = markdown.Markdown(
    extensions=['graphviz'],
    extension_configs={'graphviz':
                           {'FORMAT':'gif'}
                       },
    )
print md.convert(txt)
