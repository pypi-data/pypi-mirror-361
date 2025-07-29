#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试 StrongSort._remove_duplicate_tracks 方法的单元测试

该测试文件专注于验证重复轨迹ID处理逻辑的正确性，包括：
- 无重复ID的情况
- 存在重复ID的情况
- 相同time_since_update值的处理
- 空轨迹列表的处理
- 多个重复ID组的处理
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch
from pathlib import Path
import torch

# 导入被测试的类
from boxmot.trackers.strongsort.strongsort import StrongSort


class TestRemoveDuplicateTracks(unittest.TestCase):
    """StrongSort._remove_duplicate_tracks方法的专项单元测试"""

    def setUp(self):
        """测试前的设置"""
        # Mock所有外部依赖
        with patch('boxmot.trackers.strongsort.strongsort.ReidAutoBackend') as mock_reid, \
             patch('boxmot.trackers.strongsort.strongsort.Tracker') as mock_tracker_class, \
             patch('boxmot.trackers.strongsort.strongsort.get_cmc_method') as mock_cmc_method:
            
            # 配置mock对象
            mock_model = Mock()
            mock_model.get_features.return_value = np.random.rand(0, 128)
            mock_reid.return_value.model = mock_model
            
            mock_tracker = Mock()
            mock_tracker.tracks = []
            mock_tracker_class.return_value = mock_tracker
            
            mock_cmc = Mock()
            mock_cmc.apply.return_value = np.eye(3)
            mock_cmc_method.return_value = lambda: mock_cmc
            
            # 创建StrongSort实例
            self.strongsort = StrongSort(
                reid_weights=Path("dummy.pt"),
                device=torch.device("cpu"),
                half=False,
                per_class=False,
                min_conf=0.5
            )
            
            # 保存mock对象的引用
            self.mock_tracker = self.strongsort.tracker

    def test_remove_duplicate_tracks_no_duplicates(self):
        """测试没有重复ID的情况"""
        # 创建不同ID的轨迹
        mock_tracks = []
        for i in range(3):
            mock_track = Mock()
            mock_track.id = i + 1
            mock_track.time_since_update = i
            mock_tracks.append(mock_track)
        
        self.mock_tracker.tracks = mock_tracks
        original_count = len(self.mock_tracker.tracks)
        
        # 调用方法
        self.strongsort._remove_duplicate_tracks()
        
        # 验证没有轨迹被移除
        self.assertEqual(len(self.mock_tracker.tracks), original_count)
        for track in mock_tracks:
            self.assertIn(track, self.mock_tracker.tracks)

    def test_remove_duplicate_tracks_with_duplicates(self):
        """测试存在重复ID的情况"""
        # 创建重复ID的轨迹
        mock_tracks = []
        
        # ID=1的轨迹，time_since_update=2（应被保留）
        track1_keep = Mock()
        track1_keep.id = 1
        track1_keep.time_since_update = 2
        mock_tracks.append(track1_keep)
        
        # ID=1的轨迹，time_since_update=5（应被移除）
        track1_remove = Mock()
        track1_remove.id = 1
        track1_remove.time_since_update = 5
        mock_tracks.append(track1_remove)
        
        # ID=2的轨迹，无重复
        track2_unique = Mock()
        track2_unique.id = 2
        track2_unique.time_since_update = 1
        mock_tracks.append(track2_unique)
        
        # ID=3的轨迹，time_since_update=0（应被保留）
        track3_keep = Mock()
        track3_keep.id = 3
        track3_keep.time_since_update = 0
        mock_tracks.append(track3_keep)
        
        # ID=3的轨迹，time_since_update=3（应被移除）
        track3_remove = Mock()
        track3_remove.id = 3
        track3_remove.time_since_update = 3
        mock_tracks.append(track3_remove)
        
        self.mock_tracker.tracks = mock_tracks.copy()
        
        # 调用方法
        self.strongsort._remove_duplicate_tracks()
        
        # 验证结果
        self.assertEqual(len(self.mock_tracker.tracks), 3)  # 应该剩余3个轨迹
        
        # 验证保留的轨迹
        remaining_tracks = self.mock_tracker.tracks
        self.assertIn(track1_keep, remaining_tracks)
        self.assertIn(track2_unique, remaining_tracks)
        self.assertIn(track3_keep, remaining_tracks)
        
        # 验证被移除的轨迹
        self.assertNotIn(track1_remove, remaining_tracks)
        self.assertNotIn(track3_remove, remaining_tracks)

    def test_remove_duplicate_tracks_same_time_since_update(self):
        """测试重复ID且time_since_update相同的情况"""
        # 创建相同ID和time_since_update的轨迹
        track1 = Mock()
        track1.id = 1
        track1.time_since_update = 2
        
        track2 = Mock()
        track2.id = 1
        track2.time_since_update = 2
        
        self.mock_tracker.tracks = [track1, track2]
        
        # 调用方法
        self.strongsort._remove_duplicate_tracks()
        
        # 验证只保留一个轨迹（min函数会返回第一个遇到的最小值）
        self.assertEqual(len(self.mock_tracker.tracks), 1)
        # 应该保留第一个轨迹
        self.assertIn(track1, self.mock_tracker.tracks)
        self.assertNotIn(track2, self.mock_tracker.tracks)

    def test_remove_duplicate_tracks_empty_tracks(self):
        """测试空轨迹列表的情况"""
        self.mock_tracker.tracks = []
        
        # 调用方法（不应该抛出异常）
        self.strongsort._remove_duplicate_tracks()
        
        # 验证轨迹列表仍为空
        self.assertEqual(len(self.mock_tracker.tracks), 0)

    def test_remove_duplicate_tracks_multiple_groups(self):
        """测试多个重复ID组的情况"""
        mock_tracks = []
        
        # ID=1组：3个轨迹，保留time_since_update=1的
        for i, time_update in enumerate([3, 1, 5]):
            track = Mock()
            track.id = 1
            track.time_since_update = time_update
            mock_tracks.append(track)
        
        # ID=2组：2个轨迹，保留time_since_update=0的
        for i, time_update in enumerate([2, 0]):
            track = Mock()
            track.id = 2
            track.time_since_update = time_update
            mock_tracks.append(track)
        
        # ID=3：单个轨迹，无重复
        track_unique = Mock()
        track_unique.id = 3
        track_unique.time_since_update = 4
        mock_tracks.append(track_unique)
        
        self.mock_tracker.tracks = mock_tracks.copy()
        
        # 调用方法
        self.strongsort._remove_duplicate_tracks()
        
        # 验证结果：应该剩余3个轨迹（每个ID组保留1个）
        self.assertEqual(len(self.mock_tracker.tracks), 3)
        
        # 验证保留的轨迹具有正确的time_since_update值
        remaining_ids_and_times = [(track.id, track.time_since_update) for track in self.mock_tracker.tracks]
        expected_combinations = [(1, 1), (2, 0), (3, 4)]
        
        for expected in expected_combinations:
            self.assertIn(expected, remaining_ids_and_times)

    def test_remove_duplicate_tracks_large_scale(self):
        """测试大规模重复ID的情况"""
        mock_tracks = []
        
        # 创建大量重复ID的轨迹
        for track_id in range(1, 6):  # ID 1-5
            for time_update in range(10):  # 每个ID有10个轨迹
                track = Mock()
                track.id = track_id
                track.time_since_update = time_update
                mock_tracks.append(track)
        
        self.mock_tracker.tracks = mock_tracks.copy()
        
        # 调用方法
        self.strongsort._remove_duplicate_tracks()
        
        # 验证结果：应该剩余5个轨迹（每个ID保留1个）
        self.assertEqual(len(self.mock_tracker.tracks), 5)
        
        # 验证每个ID都保留了time_since_update=0的轨迹
        remaining_ids_and_times = [(track.id, track.time_since_update) for track in self.mock_tracker.tracks]
        expected_combinations = [(i, 0) for i in range(1, 6)]
        
        for expected in expected_combinations:
            self.assertIn(expected, remaining_ids_and_times)

    def test_remove_duplicate_tracks_edge_cases(self):
        """测试边界情况"""
        # 测试负数ID
        track_negative = Mock()
        track_negative.id = -1
        track_negative.time_since_update = 0
        
        # 测试零ID
        track_zero = Mock()
        track_zero.id = 0
        track_zero.time_since_update = 1
        
        # 测试大数ID
        track_large = Mock()
        track_large.id = 999999
        track_large.time_since_update = 2
        
        self.mock_tracker.tracks = [track_negative, track_zero, track_large]
        
        # 调用方法
        self.strongsort._remove_duplicate_tracks()
        
        # 验证所有轨迹都被保留（因为没有重复ID）
        self.assertEqual(len(self.mock_tracker.tracks), 3)
        self.assertIn(track_negative, self.mock_tracker.tracks)
        self.assertIn(track_zero, self.mock_tracker.tracks)
        self.assertIn(track_large, self.mock_tracker.tracks)


if __name__ == '__main__':
    unittest.main(verbosity=2)