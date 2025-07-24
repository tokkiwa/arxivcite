from flask import Flask, render_template
import arxiv

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
    first_author_etal = f"{details['authors'][0]} et al."
    citations['ieee'] = (
        f"{first_author_etal}, \"{details['title']},\" arXiv preprint arXiv:{details['id']}, {details['year']}. "
        f"[Online]. Available: {details['url']}"
    )
    authors_pubmed = ', '.join(details['authors'])
    citations['pubmed'] = (
        f"{authors_pubmed}. {details['title']}. arXiv; {details['year']}. Available from: {details['url']}"
    )
    return citations

app = Flask(__name__)
# トップページ用のルートを追加
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
    return render_template('citation.html', paper=details, citations=citations)

if __name__ == '__main__':
    # 開発用サーバーを起動
    app.run(debug=True, host='0.0.0.0', port=5001)