from pathlib import Path
import datamaestro.download.single as single
from datamaestro.definitions import AbstractDataset
from .conftest import MyRepository


TEST_PATH = Path(__file__).parent


class Dataset(AbstractDataset):
    def __init__(self, repository):
        super().__init__(repository)
        self.datapath = Path(repository.context._path)

    def _prepare(self):
        pass


def test_filedownloader(context):
    repository = MyRepository(context)
    dataset = Dataset(repository)

    url = "http://httpbin.org/html"
    downloader = single.filedownloader("test", url)
    downloader(dataset)
    downloader.download()
