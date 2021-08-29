#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .package import txt2epub as txt2epub
from .package import txt2pdf as txt2pdf
import argparse

__version__ = "0.1.0"


def epub():
    parser = argparse.ArgumentParser(
        prog='txt2epub.exe',
        description='テキストを電子書籍(epub)化する'
    )
    metadata = parser2metadata(parser)

    epub_init = txt2epub(metadata)
    print(epub_init.make())


def pdf():
    parser = argparse.ArgumentParser(
        prog='txt2pdf.exe',
        description='テキストをPDF化する'
    )
    metadata = parser2metadata(parser)

    pdf_init = txt2pdf(metadata)
    print(pdf_init.make())


def parser2metadata(parser):
    parser._actions[0].help = 'ヘルプの表示'
    parser.add_argument('-v', '--version', action='version', version=('%(prog)s Ver.' + __version__), help='バージョン情報の表示')
    parser.add_argument('PATH', help='フォルダのパス', metavar="PATH")
    parser.add_argument('-t', '--title', help='タイトル', type=str, metavar='(STRINGS)')
    parser.add_argument('-a', '--author', help='著者名', type=str, metavar='(STRINGS)')
    parser.add_argument('-p', '--publisher', help='出版社名', type=str, metavar='(STRINGS)')
    parser.add_argument('-tr', '--title_ruby', help='タイトルのルビ', type=str, metavar='(STRINGS)')
    parser.add_argument('-s', '--sub_title', help='サブタイトル', type=str, metavar='(STRINGS)')
    parser.add_argument('-ar', '--author_ruby', help='著者名のルビ', type=str, metavar='(STRINGS)')
    parser.add_argument('-pr', '--publisher_ruby', help='出版社名のルビ', type=str, metavar='(STRINGS)')
    parser.add_argument('-e', '--epub_version', help='電子書籍のバージョン', type=int, metavar='(INTEGER)', default=1)
    parser.add_argument('-o', '--original_first_day', help='初版出版日', metavar='(YYYY-MM-DD)')
    parser.add_argument('-u', '--original_url', help='著作物のURL', metavar='(URL)')
    parser.add_argument('-i', '--illustrator', help='出版社名のルビ', type=str, metavar='(STRINGS)')
    parser.add_argument('-f', '--fiction', help='フィクション表示', action='store_true')

    args = parser.parse_args()
    metadata = dict(
        path=args.PATH,
        title=args.title,
        author=args.author,
        publisher=args.publisher,
        fiction=args.fiction,
        sub_title=args.sub_title,
        author_ruby=args.author_ruby,
        publisher_ruby=args.publisher_ruby,
        illustrator=args.illustrator,
        version=args.epub_version,
        original_first_day=args.original_first_day,
        original_url=args.original_url
    )
    return metadata
