import os
import pytest
from gwalk.gwalk import RepoStatus, PathFilter

class TestRepoStatus:
    def test_asset_state_match(self):
        """测试 AssetState.match() 方法"""
        state = RepoStatus.AssetState('M', 'M', 'test.txt')
        assert state.match('modified') == True
        assert state.match('untracked') == False
        assert state.match('dirty') == True

        state = RepoStatus.AssetState('?', '?', 'test.txt')
        assert state.match('modified') == False
        assert state.match('untracked') == True
        assert state.match('dirty') == True

        state = RepoStatus.AssetState(' ', ' ', 'test.txt')
        assert state.match('modified') == False
        assert state.match('untracked') == False
        assert state.match('dirty') == False

class TestPathFilter:
    def test_path_filter_match(self, tmp_path):
        """测试 PathFilter.match() 方法"""
        # 创建临时的黑名单文件
        blacklist = tmp_path / "test.blacklist"
        blacklist.write_text("""
# 注释行
^.+/test1$
^.+/test2$
""")
        
        filter = PathFilter(str(blacklist))
        assert filter.match('path/to/test1') == True
        assert filter.match('path/to/test2') == True
        assert filter.match('path/to/test3') == False

    def test_path_filter_empty(self):
        """测试空的 PathFilter"""
        filter = PathFilter(None)
        assert bool(filter) == False