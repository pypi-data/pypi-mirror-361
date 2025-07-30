# YDNATL

YDNATL (**Y**ou **D**on't **N**eed **A**nother **T**emplate **L**anguage) is a Python library that lets you build HTML using simple Python classes. It's great for apps that need HTML generation while skipping the hassle of writing it by hand or using a templating engine.

- ✓ Declarative syntax for building HTML documents (like Flutter)
- ✓ Easy to read and write
- ✓ Supports all HTML5 elements
- ✓ Lightweight
- ✓ Extremely fast
- ✓ Fully customisable
- ✓ Compose HTML efficiently

## Requirements

Python `3.9` or higher is recommended.

## Installation

```bash
pip install ydnatl
```

## Usage

```python
from ydnatl import *

# Create a simple HTML document
page = HTML(
    Head(
        Title("My Page")
    ),
    Body(
        Div(
            H1("Hello, World!"),
            Paragraph("This is a test document.")
        )
    )
)

# Render the HTML document
print(page.render())
```

This code will produce:

```html
<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <title>My Page</title>
  </head>
  <body>
    <div>
      <h1>Hello, World!</h1>
      <p>This is a test document.</p>
    </div>
  </body>
</html>
```

### Dynamic Composition 

```python
from ydnatl import *

html = HTML()
header = Head()
body = Body()

body.append(
    Div(
        H1("My Headline"),
        Paragraph("Basic paragraph element"),
    )
)

if day_of_week == "Monday": 
    header.append(Title("Unfortunately, it's Monday!"))
else:
    header.append(Title("Great! It's no longer Monday!"))

html.append(header)
html.append(body)

print(html.render())
```

All element classes are subclasses of HTMLElement. The parent class provides all of the inherited functionality to generated the individual tags. Keywords args used on methods will be converted to attributes on the HTML elements being generated.

## Great For

- CLI tools
- Site builders
- Web frameworks
- Alternative to heavy template engines
- Static site generators
- Documentation generators
- LLM's and AI tooling that generate interfaces dynamically
- Creating frontends for headless platforms (CMS/CRM etc)

## Examples

### FastAPI

```python
from fastapi import FastAPI
from ydnatl import *

app = FastAPI()

@app.get("/")
async def root():
    return HTML(
        Head(
            Title("My Page")
        ),
        Body(
            Section(
                H1("Hello, World!"),
                Paragraph("This is a test document.")
            )
        )
    )
```

### Django

```python
from django.http import HttpResponse
from ydnatl import *

def index(request):
    return HttpResponse(HTML(
        Head(
            Title("My Page"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Link(rel="stylesheet", href="style.css"),
            Script(src="script.js")
        ),
        Body(
            Section(
                H1("Hello, World!"),
                Paragraph("This is a paragraph."),
                Paragraph("This is another paragraph.")
            )
        )
    ))
```

### Flask

```python
from flask import Flask
from ydnatl import *

app = Flask(__name__)

@app.route("/")
def index():
    return HTML(
        Head(
            Title("My Page")
        ),
        Body(
            Section(
                H1("Hello, World!"),
                Paragraph("This is a test document.")
            )
        )
    )
```

## Test Coverage

YDNATL has full test coverage. To run the tests locally, use:

```shell
pytest
```

or:

```shell
python run_test.py
```

## Element Methods:

- `instance.prepend()`
- `instance.append()`
- `instance.filter()`
- `instance.remove_all()`
- `instance.clear()`
- `instance.pop()`
- `instance.first()`
- `instance.last()`
- `instance.add_attribute()`
- `instance.add_attributes()`
- `instance.remove_attribute()`
- `instance.get_attribute()`
- `instance.has_attribute()`
- `instance.generate_id()`
- `instance.clone()`
- `instance.find_by_attribute()`
- `instance.get_attributes()`
- `instance.count_children()`
- `instance.render()`
- `instance.to_dict()`

## Events

- `instance.on_load()`
- `instance.on_before_render()`
- `instance.on_after_render()`
- `instance.on_unload()`

## Element Properties

- `instance.tag`
- `instance.children`
- `instance.text`
- `instance.attributes`
- `instance.self_closing`

## Modules

| **Module**         | **Purpose**                       | **Examples** |
| ------------------ | --------------------------------- | ------------ |
| ydnatl.tags.form   | Common HTML form elements         | TODO         |
| ydnatl.tags.html   | Structural HTML document elements | TODO         |
| ydnatl.tags.layout | Layout related HTML tags          | TODO         |
| ydnatl.tags.lists  | HTML list elements                | TODO         |
| ydnatl.tags.media  | Media related HTML elements       | TODO         |
| ydnatl.tags.table  | HTML table elements               | TODO         |
| ydnatl.tags.text   | HTML text elements                | TODO         |

## Importing

Instead of importing the entire module, you can selectively use only the elements you need like this:

```python

# Instead of
from ydnatl import *

# Import selectively
from ydnatl.tags.form import Form, Button
```

#### ydnatl.tags.form

- `Form()`
- `Input()`
- `Label()`
- `Select()`
- `Option()`
- `Button()`
- `Fieldset()`
- `Optgroup()`

#### ydnatl.tags.html

- `HTML()`
- `Head()`
- `Body()`
- `Title()`
- `Meta()`
- `Link()`
- `Script()`
- `Style()`
- `IFrame()`

#### ydnatl.tags.layout

- `Div()`
- `Section()`
- `Header()`
- `Nav()`
- `Footer()`
- `HorizontalRule()`
- `Main()`

#### ydnatl.tags.lists

- `OrderedList()`
- `ListItem()`
- `Datalist()`
- `DescriptionDetails()`
- `DescriptionList()`
- `DescriptionTerm()`

#### ydnatl.tags.media

- `Image()`
- `Video()`
- `Audio()`
- `Source()`
- `Picture()`
- `Figure()`
- `Figcaption()`
- `Canvas()`

#### ydnatl.tags.table

- `Table()`
- `TableFooter()`
- `TableHeaderCell()`
- `TableHeader()`
- `TableBody()`
- `TableDataCell()`
- `TableRow()`

#### ydnatl.tags.text

- `H1()`
- `H2()`
- `H3()`
- `H4()`
- `H5()`
- `H6()`
- `Paragraph()`
- `Blockquote()`
- `Pre()`
- `Quote()`
- `Cite()`
- `Em()`
- `Italic()`
- `Span()`
- `Strong()`
- `Abbr()`
- `Link()`
- `Small()`
- `Superscript()`
- `Subscript()`
- `Time()`
- `Code()`

## Creating your own elements or components

```python

from ydnatl import *

class MyTag(HTMLElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, "tag": "mytag"})

        self.add_attributes([
            ("id", "mycustomid"),
            ("aria-controls", "menu"),
        ])

    def on_load(self) -> None:
        print("The on_load event has been called")

    def on_before_render(self) -> None:
        print("The on_before_render event has been called")

    def on_after_render(self) -> None:
        print("The on_after_render event has been called")


mytag = MyTag(
    Div(
        Paragraph("Hello World!")
    )
)

print(mytag.render())
```

This will produce:

```html
<mytag id="mycustomid" aria-controls="menu">
  <div>
    <p>Hello World!</p>
  </div>
</mytag>
```

You can use the event callbacks or properties/methods directly to load further child elements, fetch data or any other programmatic task to enrich or contruct your tag on loading, render or even after render.

You can take this further and contruct an entire page as a component where everything needed for the page is contained within the element class itself. This is a great way to build websites.

## Contributions

Contributions, suggestions and improvements are all welcome. 

#### Developing YDANTL

1. Create a virtual environment

```
python3.12 -m venv .venv 
source .venv/bin/activate 
pip install --upgrade pip
```

2. Install the dev dependencies:

```
pip install ".[dev]"
```

3. Run the tests:

```
python run_tests.py
```

When you are happy with your changes, create a merge request.

## License

Please see [LICENSE](LICENSE) for licensing details.

## Author

[github.com/sn](https://github.com/sn)
