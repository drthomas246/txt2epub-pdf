from txt2epub_pdf import txt2epub
from txt2epub_pdf import txt2pdf


class Testtxt2epub():
    def test__make_1(self):
        metadata = dict(
            path="./tests/TEST BOOK",
            title="テストブック",
            title_ruby="てすとぶっく",
            sub_title="txt2epub_pdfを使って",
            author="Dr?Thomas",
            author_ruby="どくたーとーます",
            publisher="山原出版",
            publisher_ruby="やまはらしゅっぱん",
            illustrator="山原喜寛",
            version=14,
            original_first_day="1979-04-11",
            original_url="https://www.hobofoto.work/",
            fiction=True
        )
        epub_init = txt2epub(metadata)
        assert epub_init.make() == '電子書籍(epub)の作成が完了しました。'

    def test__make_2(self):
        metadata = dict(
            # path="TEST BOOK",
            title="テストブック",
            title_ruby="てすとぶっく",
            sub_title="txt2epub_pdfを使って",
            author="Dr?Thomas",
            author_ruby="どくたーとーます",
            publisher="山原出版",
            publisher_ruby="やまはらしゅっぱん",
            illustrator="山原喜寛",
            version=14,
            original_first_day="1979-04-11",
            original_url="https://www.hobofoto.work/",
            fiction=True
        )
        epub_init = txt2epub(metadata)
        assert epub_init.make() == '読み込みディレクトリを設定して下さい。'


class Testtxt2pdf():
    def test__make(self):
        metadata = dict(
            path="./tests/TEST BOOK",
            title="テストブック",
            title_ruby="てすとぶっく",
            sub_title="txt2epub_pdfを使って",
            author="Dr?Thomas",
            author_ruby="どくたーとーます",
            publisher="山原出版",
            publisher_ruby="やまはらしゅっぱん",
            illustrator="山原喜寛",
            version=14,
            original_first_day="1979-04-11",
            original_url="https://www.hobofoto.work/",
            fiction=True
        )
        pdf_init = txt2pdf(metadata)
        assert pdf_init.make() == 'Portable Document Format(pdf)の作成が完了しました。'
