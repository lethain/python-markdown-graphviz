"""
### Markdown-Python-Graphviz

This module is an extention to [Python-Markdown][pymd] which makes it
possible to embed [Graphviz][gv] syntax into Markdown documents.

### Requirements

Using this module requires:
   * Python-Markdown
   * Graphviz (particularly ``dot``)

### Syntax

Wrap Graphviz definitions within a dot/neato/dotty/lefty tag.

An example document:

    This is some text above a graph.

    <dot>
    digraph a {
        nodesep=1.0;
        rankdir=LR;
        a -> b -> c ->d;
    }
    </dot>

    Some other text between two graphs.

    <neato>
    some graph in neato...
    </neato>

    This is also some text below a graph.

Note that the opening and closing tags should come at the beginning of
their lines and should be immediately followed by a newline.
    
### Usage

    import markdown
    md = markdown.Markdown(
            extensions=['graphviz'], 
            extension_configs={'graphviz' : {'DOT','/usr/bin/dot'}}
    )
    return md.convert(some_text)


[pymd]: http://www.freewisdom.org/projects/python-markdown/ "Python-Markdown"
[gv]: http://www.graphviz.org/ "Graphviz"

"""
import markdown, re, markdown.preprocessors, subprocess

class GraphvizExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {'FORMAT':'png', 'BINARY_PATH':"", 'WRITE_IMGS_DIR':"", "BASE_IMG_LINK_DIR":""}
        for key, value in configs:
            self.config[key] = value
    
    def reset(self):
        pass

    def extendMarkdown(self, md, md_globals):
        "Add GraphvizExtension to the Markdown instance."
        md.registerExtension(self)
        self.parser = md.parser
        md.preprocessors.add('graphviz', GraphvizPreprocessor(self), '_begin')

class GraphvizPreprocessor(markdown.preprocessors.Preprocessor):
    "Find all graphviz blocks, generate images and inject image link to generated images."

    def __init__ (self, graphviz):
        self.graphviz = graphviz
        self.formatters = ["dot", "neato", "lefty", "dotty"]

    def run(self, lines):
        start_tags = [ "<%s>" % x for x in self.formatters ]
        end_tags = [ "</%s>" % x for x in self.formatters ]
        graph_n = 0
        new_lines = []
        block = []
        in_block = None
        for line in lines:
            if line in start_tags:
                assert(block == [])
                in_block = self.extract_format(line)
            elif line in end_tags:
                new_lines.append(self.graph(graph_n, in_block, block))
                graph_n = graph_n + 1
                block = []
                in_block = None
            elif in_block in self.formatters:
                block.append(line)
            else:
                new_lines.append(line)
        assert(block == [])
        return new_lines

    def extract_format(self, tag):
        format = tag[1:-1]
        assert(format in self.formatters)
        return format

    def graph(self, n, type, lines):
        "Generates a graph from lines and returns a string containing n image link to created graph."
        assert(type in self.formatters)        
        cmd = "%s%s -T%s" % (self.graphviz.config["BINARY_PATH"],
                             type,
                             self.graphviz.config["FORMAT"])
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
        #(child_stdin, child_stdout) = (p.stdin, p.stdout) 
        p.stdin.write("\n".join(lines))
        p.stdin.close()
        p.wait()
        filepath = "%s%s.%s" % (self.graphviz.config["WRITE_IMGS_DIR"], n, self.graphviz.config["FORMAT"])
        fout = open(filepath, 'w')
        fout.write(p.stdout.read())
        fout.close()
        output_path = "%s%s.%s" % (self.graphviz.config["BASE_IMG_LINK_DIR"], n, self.graphviz.config["FORMAT"])
        return "![Graphviz chart %s](%s)" % (n, output_path)

def makeExtension(configs=None) :
    return GraphvizExtension(configs=configs)
