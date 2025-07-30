
if not 'display' in dir():
    from IPython.display import display

if not 'displayHTML' in dir():
    from IPython.display import HTML
    def displayHTML(_):
        display(HTML(_))

def displayJSON(data, display=True):
    import random
    _p = f"-inara-json-{random.randint(1000, 9999)}"
    def _to_html_tree(name, data, active=False):
        if isinstance(data, dict):
            html = f'<span class="caret{_p} title{_p} {"caret-down"+_p if active else ""}">{name}</span>'
            html += f'<span class="list-description{_p}">{{}} {len(data)} key-value pairs</span>'
            html += f'<ul class="collapsible{_p} {"active"+_p if active else ""}">'
            for key, value in data.items():
                html += f'<li>{_to_html_tree(key, value)}</li>'
            html += '</ul>'
        elif isinstance(data, list):
            html = f'<span class="caret{_p} title{_p}">{name}</span>'
            html += f'<span class="list-description{_p}">[] {len(data)} items</span>'
            html += f'<ul class="collapsible{_p}">'
            for i, item in enumerate(data):
                html += f'<li>{_to_html_tree(i, item)}</li>'
            html += '</ul>'
        else:
            html = f'<span class="title{_p}">{name}</span>'
            html += f'<span>{repr(data)}</span>'
        return html
    html_content = f'''
    <html>
    <head>
    <style>
    .caret{_p} {{
        cursor: pointer;
        # user-select: none;
    }}
    .caret{_p}::before {{
        content: "\\25B6";
        font-size: 10px;
        color: black;
        display: inline-block;
        margin-right: 6px;
    }}
    .caret-down{_p}::before {{
        transform: rotate(90deg);
    }}
    .list-description{_p} {{
        font-style: italic;
        color: gray;
        margin-left: 0.5em;
    }}
    .title{_p} {{
        font-weight: bold;
        color: green;
        margin-right: 0.5em;
    }}
    .collapsible{_p} {{
        display: none;
        list-style-type: none;
    }}
    .active{_p} {{
        display: block;
    }}
    </style>
    </head>
    <body>
    <ul class="collapsible{_p} active{_p}">{_to_html_tree("root", data, active=True)}</ul>
    <script>
    var toggler = document.getElementsByClassName("caret{_p}");
    for (var i = 0; i < toggler.length; i++) {{
        toggler[i].addEventListener("click", function() {{
            this.parentElement.querySelector(".collapsible{_p}").classList.toggle("active{_p}");
            this.classList.toggle("caret-down{_p}");
        }});
    }}
    </script>
    </body>
    </html>
    '''
    if display:
        displayHTML(html_content)
    else:
        return html_content

def displayXML(xml_string, display=True):
    import xml.etree.ElementTree as ET
    import random
    _p = f"-inara-xml-{random.randint(1000, 9999)}"

    def _xml_to_html_tree(element, active=False):
        if len(element) > 0 or element.attrib:
            html = f'<li><span class="{"caret"+_p if len(element) else ""} {"caret-down"+_p if active else ""}">&lt;'
            html += f'<span class="title{_p}">{element.tag}</span>'
            for attr, value in element.attrib.items():
                html += f' <span class="attribute-name{_p}">{attr}</span>="<span class="attribute-value{_p}">{value}</span>"'
            html += '&gt;</span>'
            html += f'<ul class="collapsible{_p} {"active"+_p if active else ""}">'
            for child in element:
                html += _xml_to_html_tree(child)
            html += f'</ul></li>'
        else:
            html = f'<li>&lt;<span class="title{_p}">{element.tag}</span>&gt;{element.text}&lt;/<span class="title{_p}">{element.tag}</span>&gt;</li>'
        return html

    root = ET.fromstring(xml_string)
    html_content = f'''
    <html>
    <head>
    <style>
    .caret{_p} {{
        cursor: pointer;
        # user-select: none;
    }}
    .caret{_p}::before {{
        content: "\\25B6";
        font-size: 10px;
        color: black;
        display: inline-block;
        margin-right: 6px;
    }}
    .caret-down{_p}::before {{
        transform: rotate(90deg);
    }}
    .nested{_p} {{
        display: none;
    }}
    .collapsible{_p} {{
        display: none;
        list-style-type: none;
    }}
    .active{_p} {{
        display: block;
    }}
    .list-description{_p} {{
        font-style: italic;
        color: gray;
        margin-left: 0.5em;
    }}
    .title{_p} {{
        font-weight: bold;
        color: green;
    }}
    .attribute-name{_p} {{
        color: blue;
    }}
    .attribute-value{_p} {{
        color: red;
    }}
    </style>
    </head>
    <body>
    <ul class="collapsible{_p} active{_p}">{_xml_to_html_tree(root, active=True)}</ul>
    <script>
    var toggler = document.getElementsByClassName("caret{_p}");
    for (var i = 0; i < toggler.length; i++) {{
        toggler[i].addEventListener("click", function() {{
            this.parentElement.querySelector(".collapsible{_p}").classList.toggle("active{_p}");
            this.classList.toggle("caret-down{_p}");
        }});
    }}
    </script>
    </body>
    </html>
    '''
    if display:
        displayHTML(html_content)
    else:
        return html_content


def image_frames(data, format='PNG'):
    import io
    from PIL import Image
    img = Image.open(io.BytesIO(data))
    ret = []
    for i in range(img.n_frames):
        img.seek(i)
        buf = io.BytesIO()
        img.save(buf, format=format)
        ret.append(buf.getvalue())
    return ret

def image_url(data, format='png'):
    import base64
    image_64 = base64.b64encode(data).decode('utf-8')
    return f"data:image/{format};base64,{image_64}"

def image_html(data, format='png', width=None):
    if not isinstance(data, list):
        data = [data]
    html = ''
    for d in data:
        url = image_url(d, format)
        html += f'<img src="{url}"{" width="+str(width) if width is not None else ""}/>'
    return html

def displayImage(data, format='png', width=None):
    displayHTML(image_html(data, format=format, width=width))

def render(file, out):
    from pathlib import Path
    file = Path(file)
    if file.suffix == ".json":
        import json
        with open(file) as f:
            _ = json.load(f)
            res = displayJSON(_, display=False)
    elif file.suffix == ".xml":
        with open(file) as f:
            _ = f.read()
            res = displayXML(_, display=False)
    else:
        raise ValueError(f"Unsupported file type {file.suffix}. Please provide a .json or .xml file.")
    with open(out, 'w') as f:
        f.write(res)
