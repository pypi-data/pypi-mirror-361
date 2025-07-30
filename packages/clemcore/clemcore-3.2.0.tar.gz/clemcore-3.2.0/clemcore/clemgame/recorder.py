import collections
import copy
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Tuple, Any, List

from clemcore.clemgame.metrics import METRIC_REQUEST_COUNT, METRIC_REQUEST_COUNT_VIOLATED, METRIC_REQUEST_COUNT_PARSED
from clemcore import get_version
from clemcore.clemgame.resources import store_results_file

module_logger = logging.getLogger(__name__)


class GameRecorder(ABC):
    """Generic class for creating game records."""

    @abstractmethod
    def log_next_round(self):
        """Call this method to group interactions per turn."""
        pass

    @abstractmethod
    def count_request(self):
        pass

    @abstractmethod
    def count_request_violation(self):
        pass

    @abstractmethod
    def log_key(self, key, value):
        """Add a key and value to the internal log.
        Args:
            key: A string to identify the kind of log entry to be made.
            value: The content of the entry to be logged.
        """
        pass

    @abstractmethod
    def log_player(self, player_name: str, game_role: str, model_name: str):
        """Log a player of this game episode.
        Args:
            player_name: The player's name, usually "Player 1", "Player 2" or "Game Master"
            game_role: the role in the game e.g. Guesser or Answerer
            model_name: the name of the used model; CustomResponseModels resolve to "programmatic"
        """
        pass

    @abstractmethod
    def log_event(self, from_, to, action, call=None):
        """Add an event to the internal log.
        It can be only an action or an action plus an API call that should have the same timestamp as the action.
        Args:
            from_: The identifier string of the Player/GM that originated the action.
            to: The identifier string of the Player/GM target of the action.
            action: The benchmark action to be logged.
            call: If given, this is a tuple whose first element is the input prompt object (after API-specific
                manipulation) as passed to the API and the second element is the raw response object as returned by the
                API.
        """
        pass

    @abstractmethod
    def store_records(self, results_root, dialogue_pair_desc, game_record_dir):
        """Store benchmark records.
        Raise warnings if a mandatory element is empty or format is wrong.
        Args:
            results_root: The root path to the results directory.
            dialogue_pair_desc: A string combining the Player pair names to be used as directory name.
            game_record_dir: The game's record directory path.
        """
        pass


class NoopGameRecorder(GameRecorder):
    """Placeholder class for GameMaster initialization, does not actually record anything."""

    def __init__(self):
        self.interactions = []
        self.requests = []
        self.auto_count_logging = False  # see DefaultGameRecorder

    def log_next_round(self):
        pass

    def count_request(self):
        pass

    def count_request_violation(self):
        pass

    def log_key(self, key, value):
        pass

    def log_player(self, player_name: str, game_role: str, model_name: str):
        pass

    def log_event(self, from_, to, action, call=None):
        pass

    def store_records(self, results_root, dialogue_pair_desc, game_record_dir):
        pass


class DefaultGameRecorder(GameRecorder):
    """Default game recorder with common methods for recording game episodes."""

    def __init__(self, game_name: str, experiment_name: str, game_id: int, results_folder: str, player_model_infos: Dict):
        self._game_name = game_name
        self._current_round = 0
        """ Stores players and turn during the runs """
        self.interactions = {
            "meta": dict(game_name=game_name,
                         experiment_name=experiment_name,
                         game_id=game_id,
                         results_folder=results_folder,
                         clem_version=get_version()),
            "player_models": player_model_infos,
            # already add Game Master
            "players": collections.OrderedDict(GM=dict(game_role="Game Master", model_name="programmatic")),
            # already prepare to log the first round of turns
            "turns": [[]]
        }
        """ Stores calls to the API """
        self.requests = []
        """ Keep track of player response metrics"""
        self.requests_counts = [0]  # count per round (initially zero)
        self.violated_requests_counts = [0]  # count per round (initially zero)
        self.successful_requests_counts = [0]  # count per round (initially zero)
        # For legacy games, the counts were logged by the games.
        # New games can rely on the count logging by the recorder.
        self.auto_count_logging = True

    def log_next_round(self):
        """Call this method to group interactions per turn."""
        self._current_round += 1
        self.interactions["turns"].append([])
        self.requests_counts.append(0)
        self.violated_requests_counts.append(0)
        self.successful_requests_counts.append(0)

    def count_request_violation(self):
        self.violated_requests_counts[self._current_round] += 1
        self.successful_requests_counts[self._current_round] -= 1

    def count_request(self):
        self.requests_counts[self._current_round] += 1
        self.successful_requests_counts[self._current_round] += 1  # until parse error detected

    def log_key(self, key: str, value: Any):
        """Add a key and value to the internal log.
        Args:
            key: A string to identify the kind of log entry to be made.
            value: The content of the entry to be logged.
        """
        self.interactions[key] = value
        module_logger.info(f"{self._game_name}: Logged a game-specific interaction key: {key}.")

    def log_player(self, player_name: str, game_role: str, model_name: str):
        """Log a player of this game episode.

        Args:
            player_name: The player's name, usually "Player 1" or "Player 2"
            game_role: the role in the game e.g. Guesser or Answerer
            model_name: the name of the used model; CustomResponseModels resolve to "programmatic"
        """
        player_info = {
            "game_role": game_role,
            "model_name": model_name
        }
        self.interactions["players"][player_name] = player_info
        module_logger.info(f"{self._game_name}: Logged {player_name}: {player_info}")

    def log_event(self, from_: str, to: str, action: Dict, call: Tuple[Any, Any] = None):
        """Add an event to the internal log.
        It can be only an action or an action plus an API call that should have the same timestamp as the action.
        Args:
            from_: The identifier string of the Player/GM that originated the action.
            to: The identifier string of the Player/GM target of the action.
            action: The benchmark action to be logged.
            call: If given, this is a tuple whose first element is the input prompt object (after API-specific
                manipulation) as passed to the API and the second element is the raw response object as returned by the
                API.
        """
        timestamp = datetime.now().isoformat()
        action_obj = {
            "from": from_,
            "to": to,
            "timestamp": timestamp,
            "action": action
        }
        self.interactions["turns"][self._current_round].append(copy.deepcopy(action_obj))
        module_logger.info(
            f"{self._game_name}: Logged {action['type']} action ({from_}->{to}).")
        if call:
            call_obj = {
                "timestamp": timestamp,
                "manipulated_prompt_obj": self._needs_copy(call[0]),
                "raw_response_obj": self._needs_copy(call[1])
            }
            self.requests.append(call_obj)
            module_logger.info(f"{self._game_name}: Logged a call with timestamp {timestamp}")

    @staticmethod
    def _needs_copy(call_obj):
        """Deepcopy objects that may otherwise lead to reference issues.
        Args:
            call_obj: The object to be deep-copied for safety.
        Returns:
            The deep-copy of the passed object, or the original object if it is safe to use.
        """
        if isinstance(call_obj, Dict) or isinstance(call_obj, List):
            return copy.deepcopy(call_obj)
        elif isinstance(call_obj, str):
            return call_obj[:]
        return call_obj

    def store_records(self, results_root: str, dialogue_pair_desc: str, game_record_dir: str):
        """Store benchmark records.
        Raise warnings if a mandatory element is empty or format is wrong.
        Args:
            results_root: The root path to the results directory.
            dialogue_pair_desc: A string combining the Player pair names to be used as directory name.
            game_record_dir: The game's record directory path.
        """
        for name in self.interactions["players"]:
            """The transcript builder relies on specific player identifiers."""
            try:
                assert name == "GM" or name.startswith("Player ")
            except AssertionError:
                module_logger.warning(f"Invalid player identifiers, html builder won't work.")
        if not self.interactions["turns"]:
            module_logger.warning(f"Interaction logs are missing!")
        if not self.requests:
            module_logger.warning(f"No calls logged!")

        # add default framework metrics
        if self.auto_count_logging:
            self.log_key(METRIC_REQUEST_COUNT, self.requests_counts)
            self.log_key(METRIC_REQUEST_COUNT_VIOLATED, self.violated_requests_counts)
            self.log_key(METRIC_REQUEST_COUNT_PARSED, self.successful_requests_counts)

        store_results_file(self._game_name, self.interactions,
                           "interactions.json",
                           dialogue_pair_desc,
                           sub_dir=game_record_dir,
                           results_dir=results_root)
        store_results_file(self._game_name, self.requests,
                           "requests.json",
                           dialogue_pair_desc,
                           sub_dir=game_record_dir,
                           results_dir=results_root)
