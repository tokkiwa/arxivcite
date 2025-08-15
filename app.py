from flask import Flask, render_template
import arxiv
from urllib.parse import quote_plus

app = Flask(__name__)

def get_paper_details(paper_id):
    """論文IDを使ってarXiv APIから論文情報を取得する"""
    try:
        search = arxiv.Search(id_list=[paper_id])
        paper = next(search.results())
        details = {
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'year': paper.published.year,
            'url': paper.pdf_url,
            'id': paper_id
        }
        return details
    except StopIteration:
        return None

def generate_citations(details):
    """論文情報から各種引用フォーマットを生成する"""
    if not details:
        return None
    citations = {}
    authors_str = ' and '.join(details['authors'])
    citations['bibtex'] = (
        f"@article{{arxiv:{details['id']},\n"
        f"  author  = {{{authors_str}}},\n"
        f"  title   = {{{details['title']}}},\n"
        f"  journal = {{arXiv preprint arXiv:{details['id']}}},\n"
        f"  year    = {{{details['year']}}},\n"
        f"  url     = {{{details['url']}}}\n"
        f"}}"
    )
    def format_author(name):
        parts = name.split()
        if len(parts) == 1:
            return parts[0]
        initials = ''.join([p[0] + '.' for p in parts[:-1]])
        return f"{initials} {parts[-1]}"
    # IEEE形式
    ieee_authors = ', '.join([format_author(a) for a in details['authors'][:-1]])
    if len(details['authors']) > 1:
        ieee_authors += f", and {format_author(details['authors'][-1])}"
    citations['ieee'] = (
        f"{ieee_authors}, \"{details['title']},\" {details['year']}, arXiv:{details['id']}."
    )
    # APA形式
    apa_authors = ', '.join([format_author(a) for a in details['authors'][:-1]])
    if len(details['authors']) > 1:
        apa_authors += f", & {format_author(details['authors'][-1])}"
    else:
        apa_authors = format_author(details['authors'][0])
    citations['apa'] = (
        f"{apa_authors} ({details['year']}). {details['title']}. arXiv:{details['id']}. {details['url']}"
    )
    return citations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf/<paper_id>')
@app.route('/abs/<paper_id>')
def show_citation(paper_id):
    details = get_paper_details(paper_id)
    if not details:
        return "Paper not found.", 404
    
    citations = generate_citations(details)
    
    # Google ScholarのURLを生成
    google_scholar_url = f"https://scholar.google.com/scholar?q={quote_plus(details['title'])}"
    
    return render_template('citation.html', paper=details, citations=citations, google_scholar_url=google_scholar_url)

if __name__ == '__main__':
    # 開発用サーバーを起動
    app.run(debug=True, host='0.0.0.0', port=5001)