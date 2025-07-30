import pytest

from mbag.agents.heuristic_agents import PriorityQueueAgent
from mbag.evaluation.evaluator import MbagEvaluator


def test_goal_generator():
    evaluator = MbagEvaluator(
        {
            "world_size": (20, 20, 20),
            "num_players": 1,
            "horizon": 500,
            "goal_generator_config": {
                "goal_generator": "craftassist",
                "goal_generator_config": {
                    "data_dir": "data/craftassist",
                    "train": True,
                },
                "transforms": [
                    {"transform": "min_size_filter", "config": {"min_size": (5, 5, 5)}},
                    {"transform": "randomly_place"},
                ],
            },
            "malmo": {
                "use_malmo": False,
                "use_spectator": False,
                "video_dir": None,
            },
        },
        [
            (
                PriorityQueueAgent,
                {},
            )
        ],
    )
    episode_info = evaluator.rollout()
    assert episode_info.cumulative_reward > 0


@pytest.mark.uses_malmo
def test_goal_generator_in_malmo():
    evaluator = MbagEvaluator(
        {
            "world_size": (20, 20, 20),
            "num_players": 1,
            "horizon": 1000,
            "goal_generator_config": {
                "goal_generator": "craftassist",
                "goal_generator_config": {
                    "data_dir": "data/craftassist",
                    "train": True,
                },
                "transforms": [
                    {"transform": "min_size_filter", "config": {"min_size": (5, 5, 5)}},
                    {"transform": "randomly_place"},
                ],
            },
            "malmo": {
                "use_malmo": True,
                "use_spectator": False,
                "video_dir": None,
            },
        },
        [
            (
                PriorityQueueAgent,
                {},
            ),
        ],
    )
    episode_info = evaluator.rollout()
    assert episode_info.cumulative_reward > 0


@pytest.mark.uses_malmo
def test_seam_carving_in_malmo():
    evaluator = MbagEvaluator(
        {
            "world_size": (10, 10, 10),
            "num_players": 1,
            "horizon": 1000,
            "goal_generator_config": {
                "goal_generator": "craftassist",
                "goal_generator_config": {
                    "data_dir": "data/craftassist",
                    "train": True,
                },
                "transforms": [
                    {"transform": "min_size_filter", "config": {"min_size": (5, 5, 5)}},
                    {"transform": "seam_carving"},
                    {"transform": "randomly_place"},
                ],
            },
            "malmo": {
                "use_malmo": True,
                "use_spectator": False,
                "video_dir": None,
            },
        },
        [
            (
                PriorityQueueAgent,
                {},
            ),
        ],
    )
    episode_info = evaluator.rollout()
    assert episode_info.cumulative_reward > 0
