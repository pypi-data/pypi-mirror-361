import _test_case

import os,shutil

from m9lib import uWeb, uSoup

class TestWeb(_test_case.uTestCase):

    def setUp(self):
        pass

    def test_web(self):
        webdir = self.GetOutputFolder("web")
        flower_url = 'https://upload.wikimedia.org/wikipedia/commons/c/cb/Hibiscus_flower_TZ.jpg'
        flower_file = os.path.join(webdir, "flower.jpg")
        save_ret = uWeb.SaveUrl2File(flower_url, FilePath=flower_file)
        self.assertTrue(isinstance (save_ret, str))
        self.assertFileExists(flower_file)
        sz = os.path.getsize(flower_file)
        self.assertEqual(os.path.getsize(flower_file), 1030765)

        # fail with overwrite false
        save_ret = uWeb.SaveUrl2File(flower_url, FilePath=flower_file, Overwrite=False)
        self.assertEqual(save_ret, None)

        save_ret = uWeb.SaveUrl2File(flower_url, webdir)
        self.assertTrue(isinstance (save_ret, str))

        cosplay_page = 'https://thelightningpalace.blogspot.com/2016/02/cosplay-feature-bindi-smalls-bunny-suit.html'
        soup = uSoup.LoadSoup (cosplay_page)
        images = uSoup.FindImagesReferences(soup)
        self.assertEqual(len(images), 5)
        pass
