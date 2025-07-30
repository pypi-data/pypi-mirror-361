# Inara - helper for displaying JSON, XML, Images in all kinds of notebooks

Use in any Notebook (Jupyter, VSCode, Databricks) to display dicts/jsons and XML:
```python
from inara import displayJSON, displayXML, displayImage, image_frames
displayJSON(dict(data='driven',value=dict(cre='ation'), location=dict(ch="Zurich", gr="Athens")))
displayXML("""<?xml version="1.0"?>
<data>
    <country name="Liechtenstein">
        <rank>1</rank>
        <year>2008</year>
        <gdppc>141100</gdppc>
        <neighbor name="Austria" direction="E"/>
        <neighbor name="Switzerland" direction="W"/>
    </country>
    <country name="Singapore">
        <rank>4</rank>
        <year>2011</year>
        <gdppc>59900</gdppc>
        <neighbor name="Malaysia" direction="N"/>
    </country>
</data>
""")
```

And for images use:
```python
displayImage(image, width=500)
# or with an array of images e.g. from a multi-frame TIF
displayImage(image_frames(image_tif), width=500)
```

