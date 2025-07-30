# uWeb

These classes rely on urllib3 and beautifulsoap to provide high level helper methods.

- [Urllib3 documentation](https://urllib3.readthedocs.io/en/latest/user-guide.html)
- [Beautiful Soup documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## uWeb static methods

**uWeb.LoadUrlData(*Url*)**
- Loads a web target and returns the data
- No certificate is used
- Returns bytes data

**uWeb.SaveUrl2File(*Url*, *FolderPath*=None, *FilePath*=None, *Overwrite*=True)**
- Loads data from an *Url* and saves to a file
- If *FilePath* is specified, file will be saved to this path
- If *FilePath* is not specified, and *FolderPath* is specified, file will be saved to this folder using a resource name from the *Url*
- If the file exists and *Overwrite* is False, nothing is downloaded and None is returned
- Returns filepath to file on success
- Returns False on failure

### uSoap static methods

**LoadSoup(*Url*, *Parser*='html.parser')**
- Load data from an *Url* and instantiate a **BeautifulSoap** object
- Returns a **BeautifulSoap** object

**uSoup.FindImagesReferences(*Soup*)**
- Finds all images based on a href attribute within anchor (a)
- For example: `<a href='http://www.mydomain.com/myimage.png'>`
- Returns a list of image urls

**uSoup.FindImagesSources(*Soup*)**
- Finds all images based on a src or data-src attribute within an image (img)
- For example: `<img src='http://www.mydomain.com/myimage.png'>`
- Returns a list of image urls

**AddImageExt(*Ext*)**
- Adds extentions the list of image extensions
- Image extensions are not case sensitive
- *Ext* can be a comma-delimited string, or a list of extensions

**uSoap.IsImage(*Url*)**
- Returns True if Url is an image, based on extension
- Also works on file names or paths that are not urls

**uSoup.FindAllText(*Soup*)**
- Scans descendants looking for textual data.  Returns a list of discovered text
- Returns None if no text is found

**uSoup.FindText(*Soup*)**
- Scans descendants looking for textual data.  Returns a string of the first text discovered
- Returns None if no text is found

**uSoup.ReadTable(*Soup*)**
- Reads an HTML table and returns the textual content of the table as a grid in a list of lists