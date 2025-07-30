# uFolder

uFolder contains static helper methods folder processing.

## Folder Creation

Folder creation/confirmation are combined into a single method.

**uFolder.ConfirmFolder(*Folderpath*, *Create*=True)**
- Returns True when folder exists, or *Create* is true and the folder is created
- Returns False otherwise

```python
# confirm a folder exists without creating it
exists = uFolder.ConfirmFolder(folderpath, False)

# confirm a folder by creating it if it does not exist
exists = uFolder.ConfirmFolder(folderpath)
exists = uFolder.ConfirmFolder(folderpath, True)
```

## Find Files

Scans folders recursively to return a list of files and folders.  Returns a list of \[*name*,*path*\].

**uFolder.FindFiles(*Folderpath*, *Recurse*=False, *Files*=True, *Folders*=False, *Match*="*")**
- **Recurse**: Scan subfolders
- **Files**: Include files
- **Folders**: Include folders
- **Match**: Pattern matching

This list can be reorganized by filepath by calling **uFolder.OrganizeFilesByPath(*Files*)**.
- Organizes file list from **FindFiles()** into a list of \[*path*, \[*file1*, *file2*\]\]

## Folder Destruction

Folders are destroyed recursively.

**uFolder.DestroyEmptyFolders()** will scan recursively for folders that are empty and destroy them.

```python
# returns true when the folder is destroyed
destroyed = uFolder.DestroyFolder(folderpath)

# returns a list of destroyed folders
destroyed = uFolder.DestroyEmptyFolders(folderpath)
print (f"{len(destroyed)} folders destroyed")

```

## Temp Folders

A temp folder can be created using **uFolder.CreateTempFolder(*Rootfolder*,*Namemask*="Temp-{:03d}")**.

A custom namemask may be provided.  Returns path to a newly created temp folder.  uFolder maintains a list of temp folders that were created using this method.

**uFolder.DestroyTempFolders()** destroys all folders created by **uFolder.CreateTempFolder()**.  Returns (*count*, \[*folder*\]) where *count* is the number of folders destroyed, and \[*folder*\] is a list of folders that **failed** to destroy.

## Trim Old Files

Files in the specifed folder, matching the filemask are deleted, but keeping the latest matching files.

**uFolder.TrimOldFiles(Folderpath, Match="*", KeepCount=*20*)**
- **Folderpath**: Folderpath to look for files
- **Match**: Filemask to match
- **KeepCount**: Number of files to keep (latest files by timestamp)

Returns a list of filepaths that were removed.
