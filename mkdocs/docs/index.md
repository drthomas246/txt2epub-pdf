# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.

## クラスメソッド
こんにちは！こんばんわ！

- [htmlcov](/txt2epub-pdf/htmlcov/)

私は天才です。[^1]
 
私はお金持ちです。[^2]
 
[^1]: これは嘘です。
[^2]: これも嘘です。

```python
def epub():
    parser = argparse.ArgumentParser(
        prog='txt2epub.exe',
        description='テキストを電子書籍(epub)化する'
    )
    metadata = parser2metadata(parser)

    epub_init = txt2epub(metadata)
    print(epub_init.make())
```

!!! Note
    Note。
 
!!! Tip
    Tip。
 
!!! Success
    Success。
 
!!! Failure
    Failure。
 
!!! Warning
    Warning。
 
!!! Danger
    Danger。
 
!!! Bug
    Bug。
 
!!! summary
    summary。