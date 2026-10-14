import unittest

from app.services.conversation_state import ConversationStateStore


class ConversationStateStoreTest(unittest.TestCase):
    def setUp(self):
        self.store = ConversationStateStore()

    def test_limit_only_uses_top_n_digits(self):
        state = self.store.hydrate("s1", "近30天销售额前10名")["structured_query"]
        self.assertEqual(state["limit"], 10)
        self.assertEqual(state["time_range"], "近30天销售额前10名")

    def test_lowest_sets_ascending_order(self):
        state = self.store.hydrate("s1", "销售额最低的前5名")["structured_query"]
        self.assertEqual(state["sort"], "ascending")

    def test_follow_up_replaces_filter_when_requested(self):
        self.store.hydrate("s1", "查询华东销售额")
        state = self.store.hydrate("s1", "改成华北")["structured_query"]
        self.assertEqual(state["filters"], ["华北"])

    def test_analysis_query_carries_inherited_constraints(self):
        self.store.hydrate("s1", "近30天华东区域收入")
        analysis_query = self.store.hydrate("s1", "只看前五名")["analysis_query"]
        self.assertIn("华东", analysis_query)
        self.assertIn("收入", analysis_query)
        self.assertIn("Top-N：5", analysis_query)


if __name__ == "__main__":
    unittest.main()
