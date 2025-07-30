import os
import pytest
import gwalk.gapply

pathTest = os.path.dirname(os.path.abspath(__file__))
pathSimples = os.path.join(pathTest, 'simples')

class TestExtractor(object):
    def pathchs(self, path):
        for root, dirs, files in os.walk(pathSimples):
            for file in files:
                if file.endswith('.patch'):
                    yield os.path.join(root, file)

    def test_extract_subject_from_patch(self):
        for file in self.pathchs(pathSimples):
            subject = gwalk.gapply.extract_subject_from_patch(file)
            assert subject is not None
            filename = gwalk.gapply.extract_subject_from_filename(subject)
            assert filename is not None
