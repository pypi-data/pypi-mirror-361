import _test_case

import os

from m9lib import uFolder

class TestStringFolder(_test_case.uTestCase):

    def setUp(self):
        self.folder = os.path.join(self.GetOutputFolder(), "folder")

    def test_folder(self):
        # folder creation
        uFolder.ConfirmFolder(self.folder, False)
        self.assertFalse(os.path.isdir(self.folder))
        uFolder.ConfirmFolder(self.folder)
        self.assertTrue(os.path.isdir(self.folder))
        subfolder1 = os.path.join(self.folder, "subfolder1")
        uFolder.ConfirmFolder(subfolder1)
        self.assertTrue(os.path.isdir(subfolder1))
        subfolder2 = os.path.join(self.folder, "subfolder2")
        uFolder.ConfirmFolder(subfolder2)
        self.assertTrue(os.path.isdir(subfolder2))
        sillyfile = os.path.join(subfolder2, "silly.txt")
        with open(sillyfile, "w") as file:
            file.write("Silly file")
        self.assertTrue(os.path.isfile(sillyfile))

        # destroy empty folders
        ret_destroy = uFolder.DestroyEmptyFolders(self.folder)
        self.assertFalse(os.path.isdir(subfolder1))
        self.assertTrue(os.path.isdir(subfolder2))
        self.assertEqual(len(ret_destroy), 1)
        self.assertEqual(ret_destroy[0], subfolder1)

        # list files
        filepath = self.GetFilepath(None)
        files = uFolder.FindFiles(filepath, Recurse=False, Match="*.ini")
        self.assertEqual(len(files), 5)
        files = uFolder.FindFiles(filepath, Recurse=False, Match="*.jpg")
        self.assertEqual(len(files), 0)
        files = uFolder.FindFiles(filepath, Recurse=True, Match="*.jpg")
        self.assertEqual(len(files), 2)

        # temp folders
        temp_folder = uFolder.CreateTempFolder(self.folder)
        self.assertTrue(os.path.isdir(temp_folder))
        temp_folder = uFolder.CreateTempFolder(self.folder)
        self.assertTrue(os.path.isdir(temp_folder))
        temp_folder = uFolder.CreateTempFolder(self.folder)
        self.assertTrue(os.path.isdir(temp_folder))
        funnyfile = os.path.join(temp_folder, "funny.txt")
        with open(funnyfile, "w") as file:
            file.write("Funny file")
        self.assertTrue(os.path.isfile(funnyfile))
        destroyed = uFolder.DestroyTempFolders()
        self.assertEqual(destroyed[0], 3)
        self.assertFalse(os.path.isdir(temp_folder))

        # file organization
        files = [['f1', 'p1'], ['f2', 'p2'], ['f3', 'p2'], ['f4', 'p1'], ['f5', 'p3']]
        filesbypath = uFolder.OrganizeFilesByPath(files)
        self.assertEqual(filesbypath, [('p1', ['f1', 'f4']), ('p2', ['f2', 'f3']), ('p3', ['f5'])])
