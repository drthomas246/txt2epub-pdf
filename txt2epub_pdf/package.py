#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import tempfile
import datetime
import uuid
import shutil
import zipfile
import subprocess

import pykakasi
from PIL import Image


class txt2epub():
    def __init__(self, metadata):
        self.metadata = metadata
        self.kakasi = pykakasi.kakasi()
        self.err = {
            0: "電子書籍(epub)の作成が完了しました。",
            -1: "読み込みディレクトリを設定して下さい。",
            -2: "存在するディレクトリを指定して下さい。",
            -3: "読み込みディレクトリに.txtファイルが有りません。",
            -4: "タイトルを設定して下さい。",
            -5: "著者名を設定して下さい。",
            -6: "出版社名を設定して下さい。",
            -7: "電子書籍を開いているため新しファイルを作成できません。",
            -8: "電子書籍(epub)の作成ができませんでした。"
        }

    def make(self):
        ini = init(self, None, "style-epub")
        check = ini.initialization()
        if check != 0:
            return self.err.get(check)

        ini.make_directory()
        make_file(self, "epub")
        check = self.make_zip()
        return self.err.get(check)

    def make_zip(self):
        epub_file = os.path.join(self.out_dir, self.metadata.get("title") + ".epub")
        if os.path.isfile(epub_file):
            try:
                os.remove(epub_file)
            except PermissionError:
                return -7

        with zipfile.ZipFile(epub_file, 'w') as zip_file:
            zip_file.write(os.path.join(self.temp_dir.name, "mimetype"), arcname="mimetype", compress_type=zipfile.ZIP_STORED)
            zip_file.write(os.path.join(self.meta_inf_dir, "container.xml"), arcname="META-INF/container.xml", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.item_dir, "standard.opf"), arcname="item/standard.opf", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.item_dir, "navigation-documents.xhtml"), arcname="item/navigation-documents.xhtml", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.style_dir, "book-style.css"), arcname="item/style/book-style.css", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.style_dir, "fixed-layout-jp.css"), arcname="item/style/fixed-layout-jp.css", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.style_dir, "style-reflow.css"), arcname="item/style/style-reflow.css", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.style_dir, "style-advance.css"), arcname="item/style/style-advance.css", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.style_dir, "style-reset.css"), arcname="item/style/style-reset.css", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.style_dir, "style-standard.css"), arcname="item/style/style-standard.css", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.xhtml_dir, "p-toc-001.xhtml"), arcname="item/xhtml/p-toc-001.xhtml", compress_type=zipfile.ZIP_DEFLATED)
            if self.cover_image_file_name != "":
                zip_file.write(os.path.join(self.xhtml_dir, "p-cover.xhtml"), arcname="item/xhtml/p-cover.xhtml", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.xhtml_dir, "p-titlepage.xhtml"), arcname="item/xhtml/p-titlepage.xhtml", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.xhtml_dir, "p-caution.xhtml"), arcname="item/xhtml/p-caution.xhtml", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.xhtml_dir, "p-colophon.xhtml"), arcname="item/xhtml/p-colophon.xhtml", compress_type=zipfile.ZIP_DEFLATED)
            zip_file.write(os.path.join(self.xhtml_dir, "p-colophon2.xhtml"), arcname="item/xhtml/p-colophon2.xhtml", compress_type=zipfile.ZIP_DEFLATED)
            for image_file_name in self.image_file_name_list:
                zip_file.write(os.path.join(self.image_dir, image_file_name), arcname="item/image/" + image_file_name, compress_type=zipfile.ZIP_DEFLATED)
            for number in range(1, len(self.text_file_name_list) + 1):
                zip_file.write(os.path.join(self.xhtml_dir, "p-" + str(number).zfill(3) + ".xhtml"), arcname="item/xhtml/p-" + str(number).zfill(3) + ".xhtml", compress_type=zipfile.ZIP_DEFLATED)

        self.temp_dir.cleanup()
        if not os.path.isfile(epub_file):
            return -8

        return 0


class txt2pdf():
    def __init__(self, metadata):
        self.metadata = metadata
        self.kakasi = pykakasi.kakasi()
        self.err = {
            0: "Portable Document Format(pdf)の作成が完了しました。",
            -1: "読み込みディレクトリを設定して下さい。",
            -2: "存在するディレクトリを指定して下さい。",
            -3: "読み込みディレクトリに.txtファイルが有りません。",
            -4: "タイトルを設定して下さい。",
            -5: "著者名を設定して下さい。",
            -6: "出版社名を設定して下さい。",
            -7: "PDFを開いているため新しファイルを作成できません。",
            -8: "Portable Document Format(pdf)の作成ができませんでした。"
        }

    def make(self):
        ini = init(self, os.getcwd(), "style-pdf")
        check = ini.initialization()
        if check != 0:
            return self.err.get(check)

        ini.make_directory()
        make_file(self, "pdf")
        check = self.make_compile()
        return self.err.get(check)

    def make_compile(self):
        pdf_file = os.path.join(self.out_dir, self.metadata.get("title") + ".pdf")
        if os.path.isfile(pdf_file):
            try:
                os.remove(pdf_file)
            except PermissionError:
                return -7

        os.chdir(self.xhtml_dir)
        parameter = ['wkhtmltopdf', '--disable-smart-shrinking', '--allow', '../style', '--allow', '../image']
        if self.cover_image_file_name != "":
            parameter.append("p-cover.xhtml")

        parameter.append('p-titlepage.xhtml')
        parameter.append('p-caution.xhtml')
        parameter.append('toc')
        parameter.append('--disable-dotted-lines')
        parameter.append('--toc-header-text')
        parameter.append('目次')
        for number in range(1, len(self.text_file_name_list) + 1):
            title = 'p-' + str(number).zfill(3) + '.xhtml'
            parameter.append(title)

        parameter.append('p-colophon.xhtml')
        parameter.append('p-colophon2.xhtml')
        parameter.append(pdf_file)
        subprocess.run(parameter, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir(self.current)
        self.temp_dir.cleanup()
        if not os.path.isfile(pdf_file):
            return -8

        return 0


class init():
    def __init__(self, app, dirc, style):
        self.app = app
        self.dirc = dirc
        self.style = style

    def initialization(self):
        if self.app.metadata.get("path") is None:
            return -1

        self.app.current = os.getcwd()
        self.app.in_dir = os.path.join(self.app.current, self.app.metadata.get("path"))
        if not os.path.isdir(self.app.in_dir):
            return -2

        self.app.out_dir = os.path.join(self.app.current, "book")
        if not os.path.isdir(self.app.out_dir):
            os.mkdir(self.app.out_dir)

        file_name_list = os.listdir(self.app.in_dir)
        self.app.text_file_name_list = []
        self.app.image_file_name_list = []
        self.app.cover_image_file_name = ""
        for file_name in file_name_list:
            # ファイルの場合
            if os.path.isfile(os.path.join(self.app.in_dir, file_name)):
                # .txtファイルの場合
                if re.match(r"^.+\.[tT][xX][tT]$", file_name):
                    self.app.text_file_name_list.append(file_name)
                # .jpgファイルか.pngファイルの場合
                elif re.match(r"^.+\.[jJ][pP][eE]?[gG]$|^.+\.[pP][nN][gG]$|^.+\.[gG][iI][fF]$", file_name):
                    self.app.image_file_name_list.append(file_name)
                    # cover.jpgかcover.pngの場合
                    if re.match(r"^cover\.[jJ][pP][eE]?[gG]$|^cover\.[pP][nN][gG]$|^cover\.[gG][iI][fF]$", file_name):
                        self.app.cover_image_file_name = file_name

        if len(self.app.text_file_name_list) == 0:
            return -3

        if self.app.metadata.get("title") is None:
            self.app.metadata["title"] = os.path.basename(self.app.in_dir)

        if self.app.metadata.get("author") is None:
            self.app.metadata["author"] = "No name"

        if self.app.metadata.get("publisher") is None:
            self.app.metadata["publisher"] = "No publisher"

        self.app.text_file_name_list.sort()
        self.app.image_file_name_list.sort()
        return 0

    def make_directory(self):
        # 一時ディレクトリを作成
        self.app.temp_dir = tempfile.TemporaryDirectory(dir=self.dirc)
        # META-INFディレクトリを新規作成
        self.app.meta_inf_dir = os.path.join(self.app.temp_dir.name, "META-INF")
        os.mkdir(self.app.meta_inf_dir)
        # itemディレクトリを新規作成
        self.app.item_dir = os.path.join(self.app.temp_dir.name, "item")
        os.mkdir(self.app.item_dir)
        # xhtmlディレクトリを新規作成
        self.app.xhtml_dir = os.path.join(self.app.item_dir, "xhtml")
        os.mkdir(self.app.xhtml_dir)
        # imageディレクトリを選択
        self.app.image_dir = os.path.join(self.app.item_dir, "image")
        os.mkdir(self.app.image_dir)
        for image_file_name in self.app.image_file_name_list:
            shutil.copy2(os.path.join(self.app.in_dir, image_file_name), os.path.join(self.app.image_dir, image_file_name))

        # styleディレクトリを選択
        self.app.style_dir = os.path.join(self.app.item_dir, "style")
        shutil.copytree(os.path.join(os.path.dirname(__file__), self.style), self.app.style_dir)
        return


class make_file():
    def __init__(self, app, text_type):
        self.app = app
        if text_type == "epub":
            self.make_mimetype()
            self.make_container()
            self.make_cover()
            self.make_p_colophon()
            self.make_p_colophon2()
            self.make_p_caution()
            self.make_p_titlepage()
            self.make_standard()
            self.make_navigation_documents()
            self.make_p_toc()
            self.make_p_XXX()
        else:
            self.make_cover_pdf()
            self.make_p_colophon()
            self.make_p_colophon2()
            self.make_p_caution()
            self.make_p_titlepage()
            self.make_p_XXX()

    def make_mimetype(self):
        # mimetypeファイルを新規作成
        with open(os.path.join(self.app.temp_dir.name, "mimetype"), "w", encoding="utf-8", newline="\n") as file:
            file.write('application/epub+zip')
        return

    def make_container(self):
        # META-INF/container.xmlを新規作成
        with open(os.path.join(self.app.meta_inf_dir, "container.xml"), "w", encoding="utf-8", newline="\n") as file:
            file.write('<?xml version="1.0"?>\n')
            file.write('<container\n')
            file.write(' version="1.0"\n')
            file.write(' xmlns="urn:oasis:names:tc:opendocument:xmlns:container"\n')
            file.write('>\n')
            file.write('<rootfiles>\n')
            file.write('<rootfile\n')
            file.write(' full-path="item/standard.opf"\n')
            file.write(' media-type="application/oebps-package+xml"\n')
            file.write('/>\n')
            file.write('</rootfiles>\n')
            file.write('</container>\n')
        return

    def make_cover(self):
        # cover.xhtmlを新規作成
        if self.app.cover_image_file_name != "":
            im = Image.open(os.path.join(self.app.in_dir, self.app.cover_image_file_name))
            width, height = im.size
            with open(os.path.join(self.app.xhtml_dir, "p-cover.xhtml"), "w", encoding="utf-8", newline="\n") as file:
                file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                file.write('<!DOCTYPE html>\n')
                file.write('<html\n')
                file.write(' xmlns="http://www.w3.org/1999/xhtml"\n')
                file.write(' xmlns:epub="http://www.idpf.org/2007/ops"\n')
                file.write(' xml:lang="ja"\n')
                file.write('>\n')
                file.write('<head>\n')
                file.write('<meta charset="UTF-8"/>\n')
                file.write('<title>' + self.app.metadata.get("title") + '</title>\n')
                file.write('<link rel="stylesheet" type="text/css" href="../style/fixed-layout-jp.css"/>\n')
                file.write('<meta name="viewport" content="width=' + str(width) + ', height=' + str(height) + '"/>\n')
                file.write('</head>\n')
                file.write('<body epub:type="cover">\n')
                file.write('<div class="main">\n')
                file.write('\n')
                file.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1"\n')
                file.write(' xmlns:xlink="http://www.w3.org/1999/xlink"\n')
                file.write(' width="100%" height="100%" viewBox="0 0 ' + str(width) + ' ' + str(height) + '">\n')
                file.write('<image width="' + str(width) + '" height="' + str(height) + '" xlink:href="../image/' + self.app.cover_image_file_name + '"/>\n')
                file.write('</svg>\n')
                file.write('\n')
                file.write('</div>\n')
                file.write('</body>\n')
                file.write('</html>\n')
        return

    def make_cover_pdf(self):
        # cover.xhtmlを新規作成
        if self.app.cover_image_file_name != "":
            with open(os.path.join(self.app.xhtml_dir, "p-cover.xhtml"), "w", encoding="utf-8", newline="\n") as file:
                file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                file.write('<!DOCTYPE html>\n')
                file.write('<html\n')
                file.write(' xmlns="http://www.w3.org/1999/xhtml"\n')
                file.write(' xmlns:epub="http://www.idpf.org/2007/ops"\n')
                file.write(' xml:lang="ja"\n')
                file.write('>\n')
                file.write('<head>\n')
                file.write('<meta charset="UTF-8"/>\n')
                file.write('<title>' + self.app.metadata.get("title") + '</title>\n')
                file.write('<link rel="stylesheet" type="text/css" href="../style/book-style.css"/>\n')
                file.write('</head>\n')
                file.write('<body epub:type="cover">\n')
                file.write('<div class="image">\n')
                file.write('\n')
                file.write('<img src="../image/' + self.app.cover_image_file_name + '"/>\n')
                file.write('\n')
                file.write('</div>\n')
                file.write('</body>\n')
                file.write('</html>\n')
        return

    def make_p_colophon(self):
        # p-colophon.xhtmlを新規作成
        with open(os.path.join(self.app.xhtml_dir, "p-colophon.xhtml"), "w", encoding="utf-8", newline="\n") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<!DOCTYPE html>\n')
            file.write('<html\n')
            file.write(' xmlns="http://www.w3.org/1999/xhtml"\n')
            file.write(' xmlns:epub="http://www.idpf.org/2007/ops"\n')
            file.write(' xml:lang="ja"\n')
            file.write(' class="hltr">\n')
            file.write('<head>\n')
            file.write('<meta charset="UTF-8"/>\n')
            file.write('<title>' + self.app.metadata.get("title") + '</title>\n')
            file.write('<link rel="stylesheet" type="text/css" href="../style/book-style.css"/>\n')
            file.write('</head>\n')
            file.write('<body class="p-colophon">\n')
            file.write('<div class="main">\n')
            file.write('\n')
            file.write('<!-- ======================================================================= -->\n')
            file.write('<div class="book-title">\n')
            file.write('<div class="book-title-main mfont">\n')
            file.write('<p>' + self.app.metadata.get("title") + '</p>\n')
            file.write('</div>\n')
            if self.app.metadata.get("sub_title") is not None:
                file.write('<div class="book-title-after gfont">\n')
                file.write('<p>' + self.app.metadata.get("sub_title") + '</p>\n')
                file.write('</div>\n')

            file.write('</div>\n')
            file.write('<!-- ======================================================================= -->\n')
            file.write('\n')
            file.write('<div class="author mfont">\n')
            if self.app.metadata.get("author_ruby") is not None:
                file.write('<p><ruby>' + self.app.metadata.get("author") + '<rt>' + self.app.metadata.get("author_ruby", "") + '</rt></ruby></p>\n')
            else:
                file.write('<p>' + self.app.metadata.get("author") + '</p>\n')

            file.write('</div>\n')
            file.write('\n')
            file.write('<div class="publisher">\n')
            file.write('<p class="publisher-name">' + self.app.metadata.get("publisher") + '</p>\n')
            file.write('</div>\n')
            file.write('\n')
            file.write('<div class="release-date">\n')
            file.write('<p>' + datetime.datetime.now().strftime("%Y年%m月%d日") + '　発行</p>\n')
            file.write('</div>\n')
            file.write('\n')
            file.write('<div class="release-version">\n')
            file.write('<p>ver.' + str(self.app.metadata.get("version", 1)).zfill(3) + '</p>\n')
            file.write('</div>\n')
            file.write('\n')
            file.write('<div class="copyright">\n')
            if self.app.metadata.get("original_first_day") is not None:
                years = datetime.date.fromisoformat(self.app.metadata.get("original_first_day"))
            else:
                years = datetime.datetime.now()

            file.write('<p>&#0169;' + str(years.year) + ' ' + self.app.metadata.get("author") + '</p>\n')
            file.write('</div>\n')
            file.write('\n')
            file.write('<div class="original-books">\n')
            file.write('<p>本電子書籍は下記にもとづいて制作しました</p>\n')
            file.write('<p class="original-title">' + self.app.metadata.get("publisher") + '『' + self.app.metadata.get("title") + '』</p>\n')
            file.write('<p class="original-first-edition">' + years.strftime("%Y年%m月%d日") + '　初版発行</p>\n')
            if self.app.metadata.get("original_url") is not None:
                file.write('<p class="original-url">' + self.app.metadata.get("original_url") + '</p>\n')

            file.write('</div>\n')
            file.write('\n')
            file.write('<div class="publisher-data">\n')
            file.write('<p class="publish-person">発行者　' + self.app.metadata.get("author") + '</p>\n')
            file.write('</div>\n')
            file.write('\n')
            file.write('</div>\n')
            file.write('</body>\n')
            file.write('</html>\n')
        return

    def make_p_colophon2(self):
        # p-colophon2.xhtmlを新規作成
        with open(os.path.join(self.app.xhtml_dir, "p-colophon2.xhtml"), "w", encoding="utf-8", newline="\n") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<!DOCTYPE html>\n')
            file.write('<html\n')
            file.write(' xmlns="http://www.w3.org/1999/xhtml"\n')
            file.write(' xmlns:epub="http://www.idpf.org/2007/ops"\n')
            file.write(' xml:lang="ja"\n')
            file.write(' class="hltr">\n')
            file.write('<head>\n')
            file.write('<meta charset="UTF-8"/>\n')
            file.write('<title>' + self.app.metadata.get("title") + '</title>\n')
            file.write('<link rel="stylesheet" type="text/css" href="../style/book-style.css"/>\n')
            file.write('</head>\n')
            file.write('<body class="p-colophon2">\n')
            file.write('<div class="main">\n')
            file.write('\n')
            if self.app.metadata.get("illustrator") is not None:
                file.write('<div class="font-0em80">\n')
                file.write('<p>イラスト／' + self.app.metadata.get("illustrator") + '</p>\n')
                file.write('</div>\n')

            file.write('\n')
            file.write('<p><br/></p>\n')
            file.write('<p><br/></p>\n')
            file.write('\n')
            file.write('<div class="font-0em80">\n')
            file.write('<p>本電子書籍の全部または一部を無断で複製、転載、配信、送信すること、あるいはウェブサイトへの転載等を禁止します。また、本電子書籍の内容を無断で改変、改ざん等を行うことも禁止します。</p>\n')
            file.write('</div>\n')
            file.write('\n')
            file.write('<p><br/></p>\n')
            file.write('\n')
            file.write('<div class="font-0em60">\n')
            file.write('<p>この電子書籍はpythonライブラリtxt2epub-pdfを使って作成されました</p>\n')
            file.write('<p>&#0169;2021 Yamahara Yoshihiro</p>\n')
            file.write('<p>https://www.hobofoto.work/</p>\n')
            file.write('</div>\n')
            file.write('\n')
            file.write('</div>\n')
            file.write('</body>\n')
            file.write('</html>\n')
        return

    def make_p_caution(self):
        # p-caution.xhtmlを新規作成
        with open(os.path.join(self.app.xhtml_dir, "p-caution.xhtml"), "w", encoding="utf-8", newline="\n") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<!DOCTYPE html>\n')
            file.write('<html\n')
            file.write(' xmlns="http://www.w3.org/1999/xhtml"\n')
            file.write(' xmlns:epub="http://www.idpf.org/2007/ops"\n')
            file.write(' xml:lang="ja"\n')
            file.write(' class="vrtl">\n')
            file.write('<head>\n')
            file.write('<meta charset="UTF-8"/>\n')
            file.write('<title>ご利用上の注意</title>\n')
            file.write('<link rel="stylesheet" type="text/css" href="../style/book-style.css"/>\n')
            file.write('</head>\n')
            file.write('<body class="p-caution">\n')
            file.write('<div class="main">\n')
            file.write('\n')
            file.write('<p>本電子書籍を示すサムネイルなどのイメージ画像は、再ダウンロード時に予告なく変更される場合があります。</p>\n')
            file.write('\n')
            file.write('<p><br/></p>\n')
            file.write('<p>本電子書籍は縦書きでレイアウトされています。</p>\n')
            file.write('<p>また、ご覧になるリーディングシステムにより、表示の差が認められることがあります。</p>\n')
            if self.app.metadata.get("fiction", True):
                file.write('\n')
                file.write('<p><br/></p>\n')
                file.write('<p>この物語はフィクションであり、実在の人物・団体とは関係がございません。</p>\n')

            file.write('\n')
            file.write('</div>\n')
            file.write('</body>\n')
            file.write('</html>\n')
        return

    def make_p_titlepage(self):
        # p-titlepage.xhtmlを新規作成
        with open(os.path.join(self.app.xhtml_dir, "p-titlepage.xhtml"), "w", encoding="utf-8", newline="\n") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<!DOCTYPE html>\n')
            file.write('<html\n')
            file.write(' xmlns="http://www.w3.org/1999/xhtml"\n')
            file.write(' xmlns:epub="http://www.idpf.org/2007/ops"\n')
            file.write(' xml:lang="ja"\n')
            file.write(' class="hltr"\n')
            file.write('>\n')
            file.write('<head>\n')
            file.write('<meta charset="UTF-8"/>\n')
            file.write('<title>' + self.app.metadata.get("title") + '</title>\n')
            file.write('<link rel="stylesheet" type="text/css" href="../style/book-style.css"/>\n')
            file.write('</head>\n')
            file.write('<body class="p-titlepage">\n')
            file.write('<div class="main">\n')
            file.write('\n')
            file.write('<!-- ======================================================================= -->\n')
            file.write('<div class="book-title">\n')
            file.write('<div class="book-title-main mfont">\n')
            file.write('<p>' + self.app.metadata.get("title") + '</p>\n')
            file.write('</div>\n')
            if self.app.metadata.get("sub_title") is not None:
                file.write('<div class="book-title-after mfont">\n')
                file.write('<p>' + self.app.metadata.get("sub_title") + '</p>\n')
                file.write('</div>\n')

            file.write('</div>\n')
            file.write('<!-- ======================================================================= -->\n')
            file.write('\n')
            file.write('<div class="author mfont">\n')
            file.write('<p>' + self.app.metadata.get("author") + '</p>\n')
            file.write('</div>\n')
            file.write('\n')
            file.write('<div class="publisher">\n')
            file.write('<p class="publisher-name">' + self.app.metadata.get("publisher") + '</p>\n')
            file.write('</div>\n')
            file.write('\n')
            file.write('</div>\n')
            file.write('</body>\n')
            file.write('</html>\n')
        return

    def make_standard(self):
        # standard.opfファイルを新規作成
        with open(os.path.join(self.app.item_dir, "standard.opf"), "w", encoding="utf-8", newline="\n") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<package\n')
            file.write(' xmlns="http://www.idpf.org/2007/opf"\n')
            file.write(' version="3.0"\n')
            file.write(' xml:lang="ja"\n')
            file.write(' unique-identifier="unique-id"\n')
            file.write(' prefix="rendition: http://www.idpf.org/vocab/rendition/#\n')
            file.write('         ebpaj: http://www.ebpaj.jp/\n')
            file.write('         fixed-layout-jp: http://www.digital-comic.jp/\n')
            file.write('         kadokawa: http://www.kadokawa.co.jp/\n')
            file.write('         access: http://www.access-company.com/2012/layout#\n')
            file.write('         ibooks: http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/"\n')
            file.write('>\n')
            file.write('\n')
            file.write('<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n')
            file.write('\n')
            file.write('<!-- 作品名 -->\n')
            file.write('<dc:title id="title">' + self.app.metadata.get("title") + '</dc:title>\n')
            if self.app.metadata.get("title_ruby") is not None:
                file.write('<meta refines="#title" property="file-as">' + self.app.kakasi.convert(self.app.metadata.get("title_ruby"))[0]["hira"] + '</meta>\n')
            else:
                file.write('<meta refines="#title" property="file-as">' + self.app.kakasi.convert(self.app.metadata.get("title"))[0]["hira"] + '</meta>\n')

            file.write('\n')
            file.write('<!-- 著者名 -->\n')
            file.write('<dc:creator id="creator01">' + self.app.metadata.get("author") + '</dc:creator>\n')
            file.write('<meta refines="#creator01" property="role" scheme="marc:relators">aut</meta>\n')
            if self.app.metadata.get("author_ruby") is not None:
                file.write('<meta refines="#creator01" property="file-as">' + self.app.kakasi.convert(self.app.metadata.get("author_ruby"))[0]["hira"] + '</meta>\n')
            else:
                file.write('<meta refines="#creator01" property="file-as">' + self.app.kakasi.convert(self.app.metadata.get("author"))[0]["hira"] + '</meta>\n')

            file.write('<meta refines="#creator01" property="display-seq">1</meta>\n')
            file.write('\n')
            file.write('<!-- 出版社名 -->\n')
            file.write('<dc:publisher id="publisher">' + self.app.metadata.get("publisher") + '</dc:publisher>\n')
            if self.app.metadata.get("publisher_ruby") is not None:
                file.write('<meta refines="#publisher" property="file-as">' + self.app.kakasi.convert(self.app.metadata.get("publisher_ruby"))[0]["hira"] + '</meta>\n')
            else:
                file.write('<meta refines="#publisher" property="file-as">' + self.app.kakasi.convert(self.app.metadata.get("publisher"))[0]["hira"] + '</meta>\n')

            file.write('\n')
            file.write('<!-- 言語 -->\n')
            file.write('<dc:language>ja</dc:language>\n')
            file.write('\n')
            file.write('<!-- UUID -->\n')
            file.write('<dc:identifier id="unique-id">urn:uuid:' + str(uuid.uuid4()).upper() + '</dc:identifier>\n')
            file.write('\n')
            file.write('<!-- 更新日 -->\n')
            file.write('<meta property="dcterms:modified">' + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ") + '</meta>\n')
            file.write('\n')
            file.write('<!-- レンダリング指定 -->\n')
            file.write('<meta property="rendition:layout">reflowable</meta>\n')
            file.write('<meta property="rendition:orientation">auto</meta>\n')
            file.write('<meta property="rendition:spread">auto</meta>\n')
            file.write('\n')
            file.write('<!-- etc. -->\n')
            file.write('<meta property="ebpaj:guide-version">1.1.3</meta>\n')
            file.write('<meta property="ibooks:specified-fonts">true</meta>\n')
            file.write('\n')
            file.write('</metadata>\n')
            file.write('\n')
            file.write('<manifest>\n')
            file.write('\n')
            file.write('<!-- navigation -->\n')
            file.write('<item media-type="application/xhtml+xml" id="toc" href="navigation-documents.xhtml" properties="nav"/>\n')
            file.write('\n')
            file.write('<!-- style -->\n')
            file.write('<item media-type="text/css" id="fixed-layout-jp" href="style/fixed-layout-jp.css"/>\n')
            file.write('<item media-type="text/css" id="book-style" href="style/book-style.css"/>\n')
            file.write('<item media-type="text/css" id="style-reset" href="style/style-reset.css"/>\n')
            file.write('<item media-type="text/css" id="style-standard" href="style/style-standard.css"/>\n')
            file.write('<item media-type="text/css" id="style-advance" href="style/style-advance.css"/>\n')
            file.write('<item media-type="text/css" id="style-reflow" href="style/style-reflow.css"/>\n')
            file.write('\n')
            file.write('<!-- image -->\n')
            # 画像ファイルの数だけ、くり返し
            for image_file_name in self.app.image_file_name_list:
                # cover.jpgまたはcover.pngまたはcover.gifではない場合
                if image_file_name != self.app.cover_image_file_name:
                    # .jpgファイルの場合
                    if re.match(r"^.+\.[jJ][pP][eE]?[gG]$", image_file_name):
                        file.write('<item media-type="image/jpeg" id="' + os.path.splitext(image_file_name)[0] + '" href="image/' + image_file_name + '"/>\n')
                    # .pngファイルの場合
                    elif re.match(r"^.+\.[pP][nN][gG]$", image_file_name):
                        file.write('<item media-type="image/png" id="' + os.path.splitext(image_file_name)[0] + '" href="image/' + image_file_name + '"/>\n')
                    # .gifファイルの場合
                    elif re.match(r"^.+\.[gG][iI][fF]$", image_file_name):
                        file.write('<item media-type="image/gif" id="' + os.path.splitext(image_file_name)[0] + '" href="image/' + image_file_name + '"/>\n')
                # cover.jpgかcover.pngである場合
                if image_file_name == self.app.cover_image_file_name:
                    # .jpgファイルの場合
                    if re.match(r"^.+\.[jJ][pP][eE]?[gG]$", image_file_name):
                        file.write('<item media-type="image/jpeg" id="cover" href="image/' + image_file_name + '" properties="cover-image"/>\n')
                    # .pngファイルの場合
                    elif re.match(r"^.+\.[pP][nN][gG]$", image_file_name):
                        file.write('<item media-type="image/png" id="cover" href="image/' + image_file_name + '" properties="cover-image"/>\n')
                    # .gifファイルの場合
                    elif re.match(r"^.+\.[gG][iI][fF]$", image_file_name):
                        file.write('<item media-type="image/gif" id="cover" href="image/' + image_file_name + '" properties="cover-image"/>\n')

            file.write('\n')
            file.write('<!-- xhtml -->\n')
            # cover.jpgかcover.pngが存在する場合
            if self.app.cover_image_file_name != "":
                file.write('<item media-type="application/xhtml+xml" id="p-cover" href="xhtml/p-cover.xhtml" properties="svg"/>\n')

            file.write('<item media-type="application/xhtml+xml" id="p-titlepage" href="xhtml/p-titlepage.xhtml"/>\n')
            file.write('<item media-type="application/xhtml+xml" id="p-caution" href="xhtml/p-caution.xhtml"/>\n')
            file.write('<item media-type="application/xhtml+xml" id="p-toc-001" href="xhtml/p-toc-001.xhtml"/>\n')
            # .txtファイルの数だけ、くり返し
            for number in range(1, len(self.app.text_file_name_list) + 1):
                file.write('<item media-type="application/xhtml+xml" id="p-' + str(number).zfill(3) + '" href="xhtml/p-' + str(number).zfill(3) + '.xhtml"/>\n')

            file.write('<item media-type="application/xhtml+xml" id="p-colophon" href="xhtml/p-colophon.xhtml"/>\n')
            file.write('<item media-type="application/xhtml+xml" id="p-colophon2" href="xhtml/p-colophon2.xhtml"/>\n')
            file.write('\n')
            file.write('</manifest>\n')
            file.write('\n')
            file.write('<spine page-progression-direction="rtl">\n')
            file.write('\n')
            # cover.jpgかcover.pngが存在する場合
            if self.app.cover_image_file_name != "":
                file.write('<itemref linear="yes" idref="p-cover" properties="rendition:layout-pre-paginated rendition:spread-none rendition:page-spread-center"/>\n')

            file.write('<itemref linear="yes" idref="p-titlepage" properties="page-spread-left"/>\n')
            file.write('<itemref linear="yes" idref="p-caution"/>\n')
            file.write('<itemref linear="yes" idref="p-toc-001" properties="page-spread-left"/>\n')
            # .txtファイルの数だけ、くり返し
            for number in range(1, len(self.app.text_file_name_list) + 1):
                if number == 1:
                    file.write('<itemref linear="yes" idref="p-' + str(number).zfill(3) + '" properties="page-spread-left"/>\n')
                else:
                    file.write('<itemref linear="yes" idref="p-' + str(number).zfill(3) + '"/>\n')

            file.write('<itemref linear="yes" idref="p-colophon" properties="page-spread-left"/>\n')
            file.write('<itemref linear="yes" idref="p-colophon2" properties="page-spread-left"/>\n')
            file.write('\n')
            file.write('</spine>\n')
            file.write('\n')
            file.write('</package>\n')
        return

    def make_navigation_documents(self):
        # navigation-documents.xhtmlファイルを新規作成
        with open(os.path.join(self.app.item_dir, "navigation-documents.xhtml"), "w", encoding="utf-8", newline="\n") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<!DOCTYPE html>\n')
            file.write('<html\n')
            file.write(' xmlns="http://www.w3.org/1999/xhtml"\n')
            file.write(' xmlns:epub="http://www.idpf.org/2007/ops"\n')
            file.write(' xml:lang="ja"\n')
            file.write('>\n')
            file.write('<head>\n')
            file.write('<meta charset="UTF-8"/>\n')
            file.write('<title>Navigation</title>\n')
            file.write('</head>\n')
            file.write('<body>\n')
            file.write('\n')
            file.write('<nav epub:type="toc" id="toc">\n')
            file.write('<h1>Navigation</h1>\n')
            file.write('<ol>\n')
            file.write('<li><a href="xhtml/p-cover.xhtml">表紙</a></li>\n')
            file.write('<li><a href="xhtml/p-toc-001.xhtml">目次</a></li>\n')
            for index, text_file_name in enumerate(self.app.text_file_name_list):
                file.write('<li><a href="xhtml/p-' + str(index + 1).zfill(3) + '.xhtml#toc-' + str(index + 1).zfill(3) + '">' + re.sub(r"^[0-9]*[ 　]*|\.[t][x][t]$", "", text_file_name) + '</a></li>\n')

            file.write('<li><a href="xhtml/p-colophon.xhtml">奥付</a></li>\n')
            file.write('</ol>\n')
            file.write('</nav>\n')
            file.write('\n')
            file.write('<nav epub:type="landmarks" id="guide">\n')
            file.write('<h1>Guide</h1>\n')
            file.write('<ol>\n')
            file.write('<li><a epub:type="cover" href="xhtml/p-cover.xhtml">表紙</a></li>\n')
            file.write('<li><a epub:type="toc" href="xhtml/p-toc-001.xhtml">目次</a></li>\n')
            file.write('<li><a epub:type="bodymatter" href="xhtml/p-001.xhtml">本編</a></li>\n')
            file.write('</ol>\n')
            file.write('</nav>\n')
            file.write('\n')
            file.write('</body>\n')
            file.write('</html>\n')
        return

    def make_p_toc(self):
        # p-toc-001.xhtmlファイルを新規作成
        with open(os.path.join(self.app.xhtml_dir, "p-toc-001.xhtml"), "w", encoding="utf-8", newline="\n") as file:
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write('<!DOCTYPE html>\n')
            file.write('<html\n')
            file.write(' xmlns="http://www.w3.org/1999/xhtml"\n')
            file.write(' xmlns:epub="http://www.idpf.org/2007/ops"\n')
            file.write(' xml:lang="ja"\n')
            file.write(' class="vrtl"\n')
            file.write('>\n')
            file.write('<head>\n')
            file.write('<meta charset="UTF-8"/>\n')
            file.write('<title>' + self.app.metadata.get("title") + '</title>\n')
            file.write('<link rel="stylesheet" type="text/css" href="../style/book-style.css"/>\n')
            file.write('</head>\n')
            file.write('<body class="p-toc">\n')
            file.write('<div class="main start-2em">\n')
            file.write('\n')
            file.write('<p>　<span class="font-1em30">目次</span></p>\n')
            file.write('<p><br/></p>\n')
            file.write('<p><br/></p>\n')
            for index, text_file_name in enumerate(self.app.text_file_name_list):
                file.write('<p><a href="p-' + str(index + 1).zfill(3) + '.xhtml#toc-' + str(index + 1).zfill(3) + '"><span class="font-1em10">' + re.sub(r"^[0-9]*[ 　]*|\.[t][x][t]$", "", text_file_name) + '</span></a></p>\n')

            file.write('\n')
            file.write('</div>\n')
            file.write('</body>\n')
            file.write('</html>\n')
        return

    def make_p_XXX(self):
        # p-XXX.xhtmlファイルを新規作成
        for index, text_file_name in enumerate(self.app.text_file_name_list):
            with open(os.path.join(self.app.xhtml_dir, "p-" + str(index + 1).zfill(3) + ".xhtml"), "w", encoding="utf-8", newline="\n") as file:
                file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                file.write('<!DOCTYPE html>\n')
                file.write('<html\n')
                file.write(' xmlns="http://www.w3.org/1999/xhtml"\n')
                file.write(' xmlns:epub="http://www.idpf.org/2007/ops"\n')
                file.write(' xml:lang="ja"\n')
                file.write(' class="vrtl">\n')
                file.write('<head>\n')
                file.write('<meta charset="UTF-8"/>\n')
                file.write('<title>' + self.app.metadata.get("title") + '</title>\n')
                file.write('<link rel="stylesheet" type="text/css" href="../style/book-style.css"/>\n')
                file.write('</head>\n')
                file.write('<body class="p-text">\n')
                file.write('<div class="main">\n')
                file.write('\n')
                file.write('<h2 id="toc-' + str(index + 1).zfill(3) + '" class="bold font-1em20">' + re.sub(r"^[0-9]*[ 　]*|\.[t][x][t]$", "", text_file_name) + '</h2>\n')
                file.write('<p><br/></p>\n')
                with open(os.path.join(self.app.in_dir, text_file_name), "r", encoding="utf-8") as f:
                    while True:
                        text = f.readline()
                        if text == '':
                            break
                        # 文末の改行コードを削除
                        text = re.sub("\n$", "", text)
                        # 読み込んだ行が.jpgまたは.pngまたは.gifで終わる場合
                        if re.match(r"^.+\.[jJ][pP][eE]?[gG]$|^.+\.[pP][nN][gG]$|^.+\.[gG][iI][fF]$", text):
                            # imgタグに置換
                            file.write('<p><img class="fit" src="../image/' + text + '" alt=""/></p>\n')
                        # 読み込んだ行が空行の場合
                        elif text == "":
                            # <p>全角空白</p>を出力
                            file.write('<p><br/></p>\n')
                        # 読み込んだ行が普通のテキストの場合
                        else:
                            # HTMLエスケープ
                            text = re.sub("&", "&amp;", text)
                            text = re.sub("<", "&lt;", text)
                            text = re.sub(">", "&gt;", text)
                            text = re.sub('"', "&quot;", text)
                            text = re.sub("'", "&apos;", text)
                            text = re.sub("([0-9?!”‘’“]+)", "<span class=\"upright\">\\1</span>", text)
                            # 半角縦線 漢字 二重山括弧開き ひらがなかカタカナ 二重山括弧閉じ をルビに置換
                            text = re.sub(r"\|([一-鿋々]+)《([ぁ-ゖァ-ヺー]+)》", "<ruby>\\1<rt>\\2</rt></ruby>", text)
                            file.write('<p>' + text + '</p>\n')

                file.write('\n')
                file.write('</div>\n')
                file.write('</body>\n')
                file.write('</html>\n')
        return
