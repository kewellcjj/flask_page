from flask import Flask, render_template, render_template_string
from flask_flatpages import FlatPages, pygments_style_defs
import markdown
from bs4 import BeautifulSoup as bs
import sys

DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'

app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)

# fix unnested html code, and register to the jinja filter
@app.template_filter('prettify')
def prettify(html):
    soup = bs(html, 'html.parser')
    return soup.prettify()

def my_renderer(text):
    """Inject the markdown rendering into the jinga template"""
    rendered_body = render_template_string(text)
    extension_configs = {
        # 'codehilite': {
        #     'linenums': 'True'
        # },
        'mdx_math': {
            'enable_dollar_delimiter': True,
        }
    }
    pygmented_body = markdown.markdown(rendered_body, extensions=['codehilite', 'fenced_code', 'tables', 'mdx_math'],
                        extension_configs = extension_configs)
    return pygmented_body

app.config.update({
    'FLATPAGES_EXTENSION': ['.md', '.markdown'],
    'FLATPAGES_MARKDOWN_EXTENSIONS': ['codehilite', 'fenced_code', 'tables', 'mdx_math'],
    'FLATPAGES_HTML_RENDERER': my_renderer,
})

def index_summary(pages):
    #collect all tags
    tags = {}
    for p in pages:
        for tag in p.meta.get('tags', []):
            if tag not in tags:
                tags[tag] = 1
            else:
                tags[tag] += 1
    sorted_tags = sorted(tags.items(), reverse=True, key=lambda x: x[1])
    #collect publish dates
    dates = {}
    for p in pages:
        mmyyyy = p.meta.get('date','').strftime("%B %Y")
        if mmyyyy not in dates:
            dates[mmyyyy] = 1
        else:
            dates[mmyyyy] += 1
    sorted_dates = sorted(dates.items(), reverse=True, key=lambda x: x[1])

    return sorted_tags, sorted_dates


sorted_tags, sorted_dates = index_summary(pages)

@app.route('/')
def index():
    # #collect all tags
    # tags = {}
    # for p in pages:
    #     for tag in p.meta.get('tags', []):
    #         if tag not in tags:
    #             tags[tag] = 1
    #         else:
    #             tags[tag] += 1
    # sorted_tags = sorted(tags.items(), reverse=True, key=lambda x: x[1])
    # #collect publish dates
    # dates = {}
    # for p in pages:
    #     mmyyyy = p.meta.get('date','').strftime("%B %Y")
    #     if mmyyyy not in dates:
    #         dates[mmyyyy] = 1
    #     else:
    #         dates[mmyyyy] += 1
    # sorted_dates = sorted(dates.items(), reverse=True, key=lambda x: x[1])

    latest = sorted(pages, reverse=True, key=lambda p: p.meta['date'])
    return render_template('index.html', pages=latest, tags=sorted_tags, dates=sorted_dates, list_title="Recent Posts")

@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    # return render_template('page.html', page=page)
    return render_template('index.html', pages=[page], tags=sorted_tags, dates=sorted_dates, list_title="")

@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    tagged = sorted(tagged, reverse=True, key=lambda p: p.meta['date'])
    return render_template('index.html', pages=tagged, tags=sorted_tags, dates=sorted_dates, list_title="Recent Posts Tagged "+tag.title())

@app.route('/archive/<string:date>/')
def archive(date):
    archive = [p for p in pages if date == p.meta.get('date', []).strftime("%B %Y")]
    archive = sorted(archive, reverse=True, key=lambda p: p.meta['date'])
    return render_template('index.html', pages=archive, tags=sorted_tags, dates=sorted_dates, list_title="Posts in "+date.title())

@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('default'), 200, {'Content-Type': 'text/css'}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            if int(sys.argv[1])>2000:
                app.run(port=sys.argv[1])
        except ValueError:
            print("Invalid port number")
    else:
        app.run()