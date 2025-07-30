import _test_case

import os

from m9lib import uScanFilter, uScanFilterCondition, uScanFiles, uScanFolders

class TestCSV(_test_case.uTestCase):

    def setUp(self):
        pass

    def test_scan(self):
        rootpath = self.GetFilepath("scan")

        ##################################
        # Test filters
        ##################################

        fpImage1 = os.path.join(rootpath, "image1.jpg")
        self.assertFalse(uScanFilter ().Test (fpImage1))
        self.assertTrue(uScanFilter (uScanFilterCondition.ISFILE).Test (fpImage1))
        self.assertFalse(uScanFilter (uScanFilterCondition.ISFOLDER).Test (fpImage1))
        self.assertFalse(uScanFilter (uScanFilterCondition.ISFILE, Include=False).Test (fpImage1))
        self.assertTrue(uScanFilter (uScanFilterCondition.PATTERN, "*.jpg").Test (fpImage1))
        self.assertTrue(uScanFilter (uScanFilterCondition.P_PATTERN, "scan").Test (fpImage1))
        self.assertTrue(uScanFilter (uScanFilterCondition.LTSIZE, 13000).Test (fpImage1))
        self.assertTrue(uScanFilter (uScanFilterCondition.LTSIZE, "13000").Test (fpImage1))
        self.assertTrue(uScanFilter (uScanFilterCondition.LTSIZE, "13kb").Test (fpImage1))
        self.assertTrue(uScanFilter (uScanFilterCondition.LTSIZE, "1gb").Test (fpImage1))
        self.assertTrue(uScanFilter (uScanFilterCondition.GTSIZE, 9000).Test (fpImage1))
        fpMov = os.path.join(rootpath, "dsc_1234.mov")
        self.assertTrue(uScanFilter (uScanFilterCondition.REGEX, r".*\.mov").Test (fpMov))
        self.assertTrue(uScanFilter (uScanFilterCondition.REGEX, r".*_[0-9]{4}\.mov").Test (fpMov))
        # invalid filters
        self.assertFalse(uScanFilter (uScanFilterCondition.REGEX, r"*").IsValid())
        self.assertFalse(uScanFilter (uScanFilterCondition.GTSIZE, r"*").IsValid())
        self.assertFalse(uScanFilter (uScanFilterCondition.GTSIZE, {}).IsValid())

        ##################################
        # Scan files with filters
        ##################################

        # no filters
        scan = uScanFiles ()
        result = scan.Execute(rootpath, "", RecurseFolders=True)
        self.assertEqual(result, False)

        # bad filter
        scan = uScanFiles ()
        result = scan.Execute(rootpath, ["PATTERN:*.*", "BAD FILTER STRING"], RecurseFolders=True)
        self.assertEqual(result, False)

        # bad root path
        scan = uScanFiles ()
        result = scan.Execute(os.path.join(rootpath, "bad-path"), "PATTERN:*.*", RecurseFolders=True)
        self.assertEqual(result, False)

        # all files
        scan = uScanFiles ()
        result = scan.Execute(rootpath, "PATTERN:*.*", RecurseFolders=True)
        self.assertEqual(len(result), 6)

        # find text files at root
        scan = uScanFiles ()
        result = scan.Execute(rootpath, "PATTERN:*.txt")
        self.assertEqual(len(result), 0)

        # find text files recursively
        scan = uScanFiles ()
        result = scan.Execute(rootpath, "PATTERN:*.txt;*.doc", RecurseFolders=True)
        self.assertEqual(len(result), 3)

        # find text files recursively
        scan = uScanFiles ()
        result = scan.Execute(rootpath, "PATTERN:*.txt;*.doc;*.jpg", RecurseFolders=True)
        self.assertEqual(len(result), 5)

        # find small jpeg files recursively
        scan = uScanFiles ()
        result = scan.Execute(rootpath, ["PATTERN:*.jpg", "LTSIZE:10kb"], RecurseFolders=True)
        self.assertEqual(len(result), 1)

        # find small jpeg and mov files recursively
        scan = uScanFiles ()
        result = scan.Execute(rootpath, ["PATTERN:*.jpg;*.mov", "LTSIZE:10kb"], RecurseFolders=True)
        self.assertEqual(len(result), 2)

        # find jpeg and mov files recursively in folders starting with s
        scan = uScanFiles ()
        result = scan.Execute(rootpath, ["PATTERN:*.jpg;*.mov", "P_PATTERN:s*"], RecurseFolders=True)
        self.assertEqual(len(result), 3)

        # find jpeg and mov files recursively in folders starting with su
        scan = uScanFiles ()
        result = scan.Execute(rootpath, ["PATTERN:*.jpg;*.mov", "P_PATTERN:su*"], RecurseFolders=True)
        self.assertEqual(len(result), 1)

        # find jpeg and mov files recursively in folders NOT starting with su
        scan = uScanFiles ()
        result = scan.Execute(rootpath, ["PATTERN:*.jpg;*.mov", "PN_PATTERN:su*"], RecurseFolders=True)
        self.assertEqual(len(result), 2)

        # find jpeg and mov files recursively in folders starting with su - regex
        scan = uScanFiles ()
        result = scan.Execute(rootpath, ["REGEX:.+\\.(jpg|mov)", "P_REGEX:(s.b|xxx)"], RecurseFolders=True)
        self.assertEqual(len(result), 1)

        # find jpeg and mov files recursively in folders starting with su - regex
        scan = uScanFiles ()
        result = scan.Execute(rootpath, ["PATTERN:*.jpg;*.mov", "P_REGEX:(s.b|xxx)"], RecurseFolders=True)
        self.assertEqual(len(result), 1)

        # find jpeg and mov files recursively in folders starting with su - regex
        scan = uScanFiles ()
        result = scan.Execute(rootpath, ["PATTERN:*.jpg;*.mov", "PN_REGEX:(s.b|xxx)"], RecurseFolders=True)
        self.assertEqual(len(result), 2)

        # same but using uScanFilter
        scan = uScanFiles ()
        result = scan.Execute(rootpath, [uScanFilter("PATTERN:*.jpg;*.mov"), uScanFilter("PN_REGEX:(s.b|xxx)")], RecurseFolders=True)
        self.assertEqual(len(result), 2)

        # same but using AddScanFilter -- THIS NO LONGER WORKS
        # scan = uScanFiles ()
        # scan.AddScanFilter(uScanFilter("PATTERN:*.jpg;*.mov"))
        # scan.AddScanFilter("PN_REGEX:(s.b|xxx)")
        # result = scan.Execute(rootpath, RecurseFolders=True)
        # self.assertEqual(len(result), 2)

        ##################################
        # Scan files with IgnoreFolders
        ##################################

        # ignore a folder at the sub path
        scan = uScanFiles ()
        result = scan.Execute(rootpath, "PATTERN:*.txt", RecurseFolders=True, IgnoreFolders="sub")
        self.assertEqual(len(result), 1)

        # ignore a folder at the sub\text path
        scan = uScanFiles ()
        result = scan.Execute(rootpath, "PATTERN:*.txt", RecurseFolders=True, IgnoreFolders=r"sub\text")
        self.assertEqual(len(result), 1)

        # ignore a folder at the sub\text path, using a regular expression
        scan = uScanFiles ()
        result = scan.Execute(rootpath, "PATTERN:*.txt", RecurseFolders=True, IgnoreFolders=r"s.*b\t(ex|xx)t")
        self.assertEqual(len(result), 1)

        # ignore a folder at the sub\text path, using a regular expression with the REGEX: prefix
        scan = uScanFiles ()
        result = scan.Execute(rootpath, "PATTERN:*.txt", RecurseFolders=True, IgnoreFolders=r"$s.*b\\t(ex|xx)t")
        self.assertEqual(len(result), 1)

        # find files using regex
        scan = uScanFiles ()
        result = scan.Execute(rootpath, r"REGEX:.*_[0-9]{4}\.mov")
        self.assertEqual(len(result), 1)

        ##################################
        # Scan folders with filters
        ##################################

        # all folders
        scan = uScanFolders ()
        result = scan.Execute(rootpath, "PATTERN:*", RecurseFolders=True)
        self.assertEqual(len(result), 3)

        # folders starting with t
        scan = uScanFolders ()
        result = scan.Execute(rootpath, "PATTERN:t*", RecurseFolders=True)
        self.assertEqual(len(result), 2)

        # folders starting with t
        scan = uScanFolders ()
        result = scan.Execute(rootpath, "REGEX:t.+", RecurseFolders=True)
        self.assertEqual(len(result), 2)

        # folders under sub
        scan = uScanFolders ()
        result = scan.Execute(rootpath, "P_PATTERN:sub", RecurseFolders=True)
        self.assertEqual(len(result), 1)
