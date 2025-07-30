import _test_case

from m9lib import uCSV, uCSVFormat, uCSVIdentity, uCSVWriteMode, uCSVReadMode

from datetime import datetime
import os

class TestCSV(_test_case.uTestCase):

    def setUp(self):
        self.test_cols = ['id', 'date', 'position']
        self.test_rows = [['2', '2010-01-01 0:0:0', 'first'], ['6', '2010-02-02 0:0:0', 'second'], ['3', '2013-01-03 0:0:0', 'third'], ['1', '2009-03-04 0:0:0', 'before']]
        self.bad_rows = [['4', '2010-01-05 0:0:0'], ['5', '2010-01-06 0:0:0', 'fifth', 'fifth']]
        self.test_folder = self.GetOutputFolder("csv")

    def test_csv(self):
        csv_format = uCSVFormat()
        csv_format.SetColumns(self.test_cols)
        csv_0 = uCSV(csv_format)
        ret_add = csv_0.AddRows(self.test_rows)
        rows = csv_0.GetRows()
        self.assertEqual(ret_add, 4)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0][2], 'first')
        self.assertEqual(rows[0][1], '2010-01-01 0:0:0')
        ret_add = csv_0.AddRows(self.bad_rows)
        self.assertEqual(ret_add, False)
        
        csv_format = uCSVFormat(Identity=uCSVIdentity.ID_ONLY)
        csv_format.SetColumns(self.test_cols)
        csv_1 = uCSV(csv_format)
        ret_add = csv_1.AddRows(self.test_rows)
        self.assertEqual(ret_add, 4)
        rows = csv_1.GetRows()
        self.assertEqual(len(rows), 4)

        # identity test
        self.assertEqual(csv_1.GetRowCount(), 4)
        ret_add = csv_1.AddRow(['2', '2010-01-01 0:0:0', 'my dupe'])
        self.assertEqual(ret_add, False)
        self.assertEqual(csv_1.GetRowById('2')[2], 'first')
        ret_add = csv_1.AddRow(['2', '2010-01-01 0:0:0', 'my dupe'], True)
        self.assertEqual(ret_add, '2')
        self.assertEqual(csv_1.GetRowById('2')[2], 'my dupe')
        self.assertEqual(csv_1.GetRowCount(), 4)
        ret_add = csv_1.AddRow('2, 2010-01-01 0:0:0, duplicate', True)
        self.assertEqual(ret_add, '2')
        self.assertEqual(csv_1.GetRowById('2')[2], 'duplicate')
        self.assertEqual(csv_1.GetRowCount(), 4)

        # search - invalid conditions
        s_ret = csv_1.SearchRows([('xxx', 'first')])
        self.assertEqual(s_ret, False)
        s_ret = csv_1.SearchRows([(9, 'first')])
        self.assertEqual(s_ret, False)
        s_ret = csv_1.SearchRows([('id', '>xxx')])
        self.assertEqual(s_ret, False)

        # search - no match
        s_ret = csv_1.SearchRows([])
        self.assertEqual(s_ret, [])
        s_ret = csv_1.SearchRows([('position', 'xxx')])
        self.assertEqual(s_ret, [])

        # search - literal match
        s_ret = csv_1.SearchRows([('position', 'second')])
        self.assertEqual(len(s_ret), 1)
        self.assertEqual(s_ret[0][2], 'second')
        # search - or success
        s_ret = csv_1.SearchRows([('position', 'second'), ('position', 'xxx')], And=False)
        self.assertEqual(len(s_ret), 1)
        self.assertEqual(s_ret[0][2], 'second')
        # search - and failure
        s_ret = csv_1.SearchRows([('position', 'second'), ('position', 'xxx')])
        self.assertEqual(len(s_ret), 0)
        # search - and success
        s_ret = csv_1.SearchRows([('position', 'second'), ('id', '6')])
        self.assertEqual(len(s_ret), 1)
        self.assertEqual(s_ret[0][2], 'second')

        # search - regex
        s_ret = csv_1.SearchRows([('position', 'REGEX:.*lic.*')])
        self.assertEqual(len(s_ret), 1)
        self.assertEqual(s_ret[0][2], 'duplicate')
        # search - regex timestamp conversion
        s_ret = csv_1.SearchRows([('date', 'REGEX:.*-01-.*')])
        self.assertEqual(len(s_ret), 2)
        # search - numerical failure
        s_ret = csv_1.SearchRows([('position', '>2')])
        self.assertEqual(len(s_ret), 0)
        # search - numerical comparison
        s_ret = csv_1.SearchRows([('id', '=2')])
        self.assertEqual(len(s_ret), 1)
        self.assertEqual(int(s_ret[0][0]), 2)
        s_ret = csv_1.SearchRows([('id', '==2')])
        self.assertEqual(len(s_ret), 1)
        self.assertEqual(int(s_ret[0][0]), 2)
        s_ret = csv_1.SearchRows([('id', '!=2')])
        self.assertEqual(len(s_ret), 3)
        s_ret = csv_1.SearchRows([('id', '>2')])
        self.assertEqual(len(s_ret), 2)
        self.assertEqual(int(s_ret[0][0])+int(s_ret[1][0]), 9)
        s_ret = csv_1.SearchRows([('id', '>=2')])
        self.assertEqual(len(s_ret), 3)
        self.assertEqual(int(s_ret[0][0])+int(s_ret[1][0])+int(s_ret[2][0]), 11)
        s_ret = csv_1.SearchRows([('id', '<2')])
        self.assertEqual(len(s_ret), 1)
        self.assertEqual(int(s_ret[0][0]), 1)
        s_ret = csv_1.SearchRows([('id', '<=2')])
        self.assertEqual(len(s_ret), 2)
        self.assertEqual(int(s_ret[0][0])+int(s_ret[1][0]), 3)

        # date identity        
        csv_format = uCSVFormat(Identity=uCSVIdentity.ID_DATE)
        csv_format.SetColumns(self.test_cols)
        csv_2 = uCSV(csv_format)
        csv_2.AddRows(self.test_rows)
        rows = csv_2.GetRows()
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[3][2], 'before')
        self.assertEqual(rows[2][1].year, 2013)
        
    def test_csv_file(self):
        csv_format = uCSVFormat(Identity=uCSVIdentity.ID_ONLY)
        csv_format.SetColumns(self.test_cols)
        csv = uCSV(csv_format)
        self.assertEqual(csv.AddRows(self.test_rows), 4)
        filepath = os.path.join(self.test_folder, 'test.csv')
        empty = os.path.join(self.test_folder, 'empty.csv')
        open(empty, "w").close()

        ret = csv.WriteFile(filepath)
        self.assertEqual(ret, 4)
        self.assertEqual(self.__count_lines(filepath), 5)
        ret = csv.WriteFile(filepath)
        self.assertEqual(ret, 4)
        self.assertEqual(self.__count_lines(filepath), 5)
        ret = csv.WriteFile(filepath, uCSVWriteMode.APPEND)
        self.assertEqual(ret, 4)
        self.assertEqual(self.__count_lines(filepath), 9)

        # test formats
        format_test = csv_format.TestFormat(filepath)
        self.assertEqual(format_test, True)
        format2 = uCSVFormat.ReadFormat(filepath)
        self.assertTrue(isinstance(format2, uCSVFormat))
        if isinstance(format2, uCSVFormat):
            self.assertEqual(csv_format.Columns, format2.Columns)
        format2 = uCSVFormat.ReadFormat(filepath, Header=False)
        self.assertTrue(isinstance(format2, uCSVFormat))
        if isinstance(format2, uCSVFormat):
            self.assertEqual(len(csv_format.Columns), len(format2.Columns))
        # column counts good but ids do not match
        format2 = uCSVFormat(Header=True)
        format2.SetColumns(['xxx','yyy','zzz'])
        test_format = format2.TestFormat(filepath)
        self.assertFalse(test_format is True)
        # no header .. column count matches
        format2 = uCSVFormat(Header=False)
        format2.SetColumns(['xxx','yyy','zzz'])
        test_format = format2.TestFormat(filepath)
        self.assertTrue(test_format)
        # open file with format
        csv = uCSV(format2)
        csv.ReadFile(filepath)
        self.assertEqual(len(csv.GetRows()), 9)
        # open file with no format
        csv = uCSV()
        csv.ReadFile(filepath) # first row is header
        self.assertEqual(len(csv.GetRows()), 8)
        csv.ReadFile(filepath) # replace contents
        self.assertEqual(len(csv.GetRows()), 8)
        csv.ReadFile(filepath, uCSVReadMode.ADDROWS) # append contents
        self.assertEqual(len(csv.GetRows()), 16)
        # empty file test
        test_format = format2.TestFormat(empty)
        self.assertTrue(test_format) # format of empty file matches
        csv.ReadFile(empty, uCSVReadMode.ADDROWS) # append no contents
        self.assertEqual(len(csv.GetRows()), 16)
        rf = csv.ReadFile(empty) # append no contents
        self.assertTrue(rf)
        self.assertEqual(len(csv.GetRows()), 0)

        csv_format2 = uCSVFormat(Identity=uCSVIdentity.ID_ONLY)
        csv2 = uCSV(csv_format2)
        filepath2 = os.path.join(self.test_folder, 'test2.csv')
        ret = csv2.ReadFile (filepath)
        self.assertFalse(ret)
        ret = csv2.ReadFile (filepath, uCSVReadMode.RESET)
        # fails due to ID conflict
        self.assertFalse(ret)

        # rewrite file and repeat test
        csv_format = uCSVFormat(Identity=uCSVIdentity.ID_ONLY)
        csv_format.SetColumns(self.test_cols)
        csv = uCSV(csv_format)
        self.assertEqual(csv.AddRows(self.test_rows), 4)
        filepath = os.path.join(self.test_folder, 'test.csv')
        ret = csv.WriteFile(filepath)
        self.assertEqual(ret, 4)
        self.assertEqual(self.__count_lines(filepath), 5)

        csv_format2 = uCSVFormat(Identity=uCSVIdentity.ID_ONLY)
        csv2 = uCSV(csv_format2)
        filepath2 = os.path.join(self.test_folder, 'test2.csv')
        ret = csv2.ReadFile (filepath)
        self.assertFalse(ret)
        ret = csv2.ReadFile (filepath, uCSVReadMode.RESET)
        self.assertTrue(ret)
        self.assertEqual(csv.format.Columns, csv2.format.Columns)
        ret = csv2.WriteFile(filepath2)
        self.assertEqual(ret, 4)

        csv2.format.Header = False
        csv2.format.Delimiter = '|'
        filepath3 = os.path.join(self.test_folder, 'test3.csv')
        ret = csv2.WriteFile(filepath3)
        self.assertEqual(ret, 4)
        
    def __count_lines(self, in_filepath):
        count = 0
        try:
            file = open(in_filepath, 'r')
            while file.readline()!="":
                count += 1
            file.close ()
        except:
            return False

        return count
