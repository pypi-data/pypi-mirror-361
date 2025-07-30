import abc
import collections
from copy import deepcopy
from typing import List, Dict, Tuple, Union

from clemcore import backends
from clemcore.clemgame.master import GameMaster
from clemcore.clemgame.registry import GameSpec
from clemcore.clemgame.player import Player


class DialogueGameMaster(GameMaster):
    """Extended GameMaster, implementing turns as described in the clembench paper.
    Has most logging and gameplay procedures implemented, including convenient logging methods.
    """

    def __init__(self, game_spec: GameSpec, experiment: dict, player_models: List[backends.Model]):
        """
        Args:
            name: The name of the game (as specified in game_registry).
            path: Path to the game (as specified in game_registry).
            experiment: The experiment (set of instances) to use.
            player_models: Player models to use for one or two players.
        """
        super().__init__(game_spec, experiment, player_models)
        # the logging works with an internal mapping of "Player N" -> Player
        self.players_by_names: Dict[str, Player] = collections.OrderedDict()
        self.context_for_player: Dict[str, Dict] = dict()  # context entries look like {"role":"user", "content": ...}
        self.current_round: int = 0
        self._current_player: Player = None
        self._current_player_idx: int = 0
        self.info = {}

    def __setstate__(self, state):
        self.__dict__.update(state)
        for player in self.players_by_names.values():  # sync game recorders (not copied in Player)
            player.game_recorder = self.game_recorder

    @property
    def current_player(self) -> Player:
        return self._current_player

    def get_players(self) -> List[Player]:
        """Get a list of the players.
        Returns:
            List of Player instances in the order they are added.
        """
        return list(self.players_by_names.values())

    def add_player(self, player: Player, initial_prompt: Union[str, Dict] = None,
                   initial_context: Union[str, Dict] = None):
        """Add a player to the game. The same player cannot be added twice.
        The player identity is determined by the player's name.

        Important: During gameplay, the players will be called in the same order as added to the game master!

        Args:
            player: The player to be added to the game. The player's name must be unique.
            initial_prompt: The initial prompt given to the player (optional). See Player for more details.
            initial_context: A context to be immediately set for the player (optional). This is useful for initial
                            prompts that are supposed to be handled as the first context, for example, when adding
                            the other player's response to the prompt is not necessary, but the player is supposed
                            to directly react to the initial prompt. Alternatively, overwrite on_before_game() and
                            use set_context_for(player) to set the player context.
        """
        player.game_recorder = self.game_recorder  # player should record to the same interaction log
        player.initial_prompt = initial_prompt
        player.name = f"Player {len(self.players_by_names) + 1}"
        if player.name in self.players_by_names:
            raise ValueError(f"Player names must be unique, "
                             f"but there is already a player registered with name '{player.name}'.")
        self.players_by_names[player.name] = player
        self.log_player(player)
        if initial_context is not None:
            assert isinstance(initial_context, (str, dict)), \
                f"The initial context must be a str or dict, but is {type(initial_context)}"
            if isinstance(initial_context, dict):
                assert "content" in initial_context, "The initial context requires a content entry"
                extras = {k: v for k, v in initial_context.items() if k not in ["role", "content"]}
                self.set_context_for(player, initial_context["content"], **extras)
            else:
                self.set_context_for(player, initial_context)

    def setup(self, **kwargs):
        """Load resources and prepare everything to play the game.
        Needs to log the players dictionary via self.log_players(players_dict).
        Intended to be left as-is by inheriting classes. Implement game-specific setup functionality in the _on_setup
        method.
        Called by the game's GameBenchmark run method for each game instance.
        Args:
            kwargs: Keyword arguments used to set up the GameMaster instance. This is usually a game instance object
                read from the game's instances.json.
        """
        self.game_recorder.auto_count_logging = False  # legacy games usually count and store themselves
        self._on_setup(**kwargs)
        self._current_player = self.get_players()[self._current_player_idx]
        self._on_before_game()
        self._on_before_round()

    @abc.abstractmethod
    def _on_setup(self, **kwargs):
        """Method executed at the start of the default setup method.
        Template method: Must be implemented!
        Use add_player() here to add the players.
        Args:
            kwargs: Keyword arguments of the game instance. This is usually a game instance object
                read from the game's instances.json.
        """
        pass

    def get_game_state(self):
        return None

    def set_context_for(self, player: Player, content: str, **extras):
        """
        Set the context for the specified Player. The player will be prompted with the context on its next turn.

        The context always has a 'role' and 'content' entry where the 'role' is always set to 'user'.
        Args:
            player: The player to set the context for.
            content: The text content to be added to the context.
            extras: Additional content to be merged into the context e.g. information about images
        """
        if player is None:
            return
        message = {"role": "user", "content": content}
        context = {**extras, **message}
        self.context_for_player[player.name] = context

    def get_context_for(self, player) -> Dict:
        assert player is not None, "Cannot get player context for 'None'"
        assert player.name in self.context_for_player, f"No context set for {player.name}"
        context = self.context_for_player[player.name]
        assert "role" in context, f"Player context must have a 'role' entry"
        assert context["role"] == "user", f"Role of player context must be 'user'"
        assert "content" in context, f"Player context must have a 'content' entry"
        return context

    def play(self) -> None:
        """
        Main play loop method. This method is called to run the game for benchmarking.
        """
        done = False
        while not done:
            context = self.get_context_for(self.current_player)
            response = self.current_player(context)
            done, _ = self.step(response)

    def step(self, response: str) -> Tuple[bool, Dict]:
        """
        Transitions the game state by applying the current player's response.

        :param response: The response (verbal action) of the current player.
        :return: done, info
        """
        # compute scores first, so that we are sure that the player's context
        # can still be retrieved (state has not changed yet)
        context = self.get_context_for(self.current_player)
        self.info["response_score"] = self.compute_response_score(response, context)
        self.info["response_feedback"] = self.get_response_feedback(response, context)
        self.info["episode_score"] = 0

        # todo: it seems we should change the order here: Parse should come first, and then validate.
        # While parse might throw a parsing (format error) validate would check solely for satisfied game rules.
        # Note: this would allow to cut off too long responses (during parse) and to only validate on the cut off piece.
        if self._validate_player_response(self.current_player, response):
            parsed_response = self._parse_response(self.current_player, response)
            self._on_valid_player_response(self.current_player, parsed_response)

        # determine if the current player should pass the turn to the next player or get another turn:
        if self._should_pass_turn():  # True = move on to next player
            self._current_player = self._next_player()

        if self._start_next_round():
            self._on_after_round()
            self.current_round += 1  # already increment here b.c. _does_game_proceed might rely on it

        done = not self._does_game_proceed()
        if done:
            self._on_after_game()
            self.info["episode_score"] = self.compute_episode_score()
        elif self._start_next_round():  # prepare next round only when game has not ended yet
            self.__prepare_next_round()

        info = deepcopy(self.info)
        self.info = {}  # reset info after each step
        return done, info

    def _should_pass_turn(self):
        """
        Whether to pass the turn to the next player. Otherwise, the current player keeps playing based on the context
        set via set_player_context(player, content).
        As every response request entails a single turn, this should return False if the player is to be reprompted.
        """
        return True

    def _next_player(self) -> Player:
        """
        Subclasses can overwrite this method to determine the next player after a player's turn has been passed.

        Default: The gamer master passes the turn to the next player in the player list (order as added).
        Starting again with the first player, when all players have had their turn(s).

        :return: the next (current) player
        """
        self._current_player_idx = (self._current_player_idx + 1) % len(self.players_by_names)
        return self.get_players()[self._current_player_idx]

    def _start_next_round(self) -> bool:
        """
        Subclasses can overwrite this method to specify when a next round should start after a player's turn is passed.

        Default: Start next round when we cycled through the whole list i.e. it is again the first player's turn.

        :return: True, when to start a new round
        """
        return self._current_player_idx == 0

    def __prepare_next_round(self):
        self.log_next_round()  # add record entry for player turns
        self._on_before_round()

    def get_response_feedback(self, response: str, context: Dict):
        """
        Optional.
        :param response: The response of the current player.
        :param context: The context given to the current player to generate the response for.
        :return: a verbal feedback about the player's response given the context
        """
        return None

    def compute_response_score(self, response: str, context: Dict):
        """
        Mandatory.
        :param response: The response of the current player.
        :param context: The context given to the current player to generate the response for.
        :return: the performance score for a player's response given the context
        """
        return 0

    def compute_episode_score(self):
        """
        :return: the performance of the agent over the whole episode
        """
        return 0

    @abc.abstractmethod
    def _on_valid_player_response(self, player: Player, parsed_response: str):
        """
        Method executed after a player response has been parsed and validated.

        Set the response as the context for the other player (if necessary).

        You could also set a new context for the current player and give the player
        another turn by letting _should_pass_turn() return False.

        To do this use the method set_context_for(player, response).
        Args:
            player: The Player instance that produced the response (or has been modified by the GM).
            parsed_response: The parsed and valid response of the current player.
        """
        pass

    @abc.abstractmethod
    def _validate_player_response(self, player: Player, response: str) -> bool:
        """
        Decide if a player response is valid. An invalid response breaks the game rules and might end the game.

        Note: If the response is not valid, then _parse_response() and on_valid_player_response() will not be called.

        However, game developers can decide to give the player another turn by letting _should_pass_turn() return False.

        Args:
            player: The player that gave the response.
            response: The response of the current player.
        Returns:
            True, if the response is fine. Otherwise, False.
        """
        pass

    def _parse_response(self, player: Player, response: str) -> str:
        """Decide if a response utterance should be modified and apply modifications.

        Hook: Modify this method for game-specific functionality.

        Args:
            player: The Player instance that produced the response. Intended to allow for individual handling of
                different players.
            response: The response of the current player.
        Returns:
            The parsed response
        """
        return response

    @abc.abstractmethod
    def _does_game_proceed(self) -> bool:
        """Check if game should proceed.

        Mandatory override.

        This method is used to determine if a game should continue or be stopped. Both successful completion of the game
        and game-ending failures should lead to this method returning False.
        Returns:
            A bool, True if game continues, False if game should stop.
        """
        pass

    def _on_before_round(self):
        """Executed in the play loop before a new round of gameplay starts.

        Hook: Modify this method for game-specific functionality.
        """
        pass

    def _on_after_round(self):
        """Executed in the play loop after a round of gameply finished i.e. _start_next_round() resolves to True.

        Hook: Modify this method for game-specific functionality.
        """
        pass

    def _on_before_game(self):
        """Executed once at the start, before entering the play loop.

        Hook: Modify this method for game-specific functionality.

        Adding the initial prompt to the dialogue history with this method is recommended.
        """
        pass

    def _on_after_game(self):
        """Executed once at the end, after exiting the play loop.

        Hook: Modify this method for game-specific functionality.

        This method is useful to process and log/record overall game results.
        """
        pass
