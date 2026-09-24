import unittest

import pandas as pd

from utils.batch.mapping_batch import orderlines_mapping


class TestOrderMapping(unittest.TestCase):
    def setUp(self):
        self.order_lines = pd.DataFrame(
            {
                "DATE": ["2026-01-01"] * 4,
                "OrderNumber": [101, 102, 102, 103],
                "SKU": ["A", "B", "C", "D"],
            }
        )

    def test_batch_mapping_keeps_multi_line_order_in_one_wave(self):
        mapped, wave_count = orderlines_mapping(self.order_lines.copy(), 2)

        self.assertEqual(mapped["OrderID"].tolist(), [1, 2, 2, 3])
        self.assertEqual(mapped["WaveID"].tolist(), [0, 0, 0, 1])
        self.assertEqual(wave_count, 2)

    def test_cluster_normal_mapping_keeps_multi_line_order_in_one_wave(self):
        from utils.cluster.clustering import lines_mapping

        mapped, next_wave = lines_mapping(self.order_lines.copy(), 2, 5)

        self.assertEqual(mapped["OrderID"].tolist(), [1, 2, 2, 3])
        self.assertEqual(mapped["WaveID"].tolist(), [5, 5, 5, 6])
        self.assertEqual(next_wave, 7)


if __name__ == "__main__":
    unittest.main()
