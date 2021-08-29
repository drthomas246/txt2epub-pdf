# txt2epub-pdf

テキストを電子書籍形式またはPDF形式に変換します。

## 使用方法

### ファイルの準備

1. 新しいフォルダを作成します。
1. 章ごとにテキストファイルを作成します。
1. テキストファイルの名前を「数字＋半角スペース＋章のタイトル.txt」(例 「1 第１章.txt」)として作ったフォルダに保存します。
1. カバー画像は「cover.jpg」または「cover.png」または「cover.gif」として作ったフォルダに保存しておく。
1. 途中に挿絵を挿入したい場合は、作ったフォルダに挿絵を保存し、テキストファイルの差し込みたい場所に画像ファイル名のみを記入する。(画像の形式は JPG , PNG , GIF に対応)
1. 漢字にルビを振る場合は、半角縦線「ルビを振る漢字」二重山括弧開き「ルビ」二重山括弧閉じ(例 |漢字《るび》)となるようにする。(Webサイト「小説家になろう」と同じルビの振り方)

### コマンドラインシェルで使う

1. 上記準備が完了したら、コマンドラインに、電子書籍の場合は「txt2epub フォルダのパス」、PDFの場合は「txt2pdf フォルダのパス」を入力する。
1. 作成に成功すれば「電子書籍(epub)の作成が完了しました。」または「Portable Document Format(pdf)の作成が完了しました。」と表示されます。失敗した場合は理由が表示されますのでそれに従ってください。
1. 