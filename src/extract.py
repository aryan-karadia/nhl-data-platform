import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any

# Configure basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NHLExtractor:
    """
    Ingestion Module to pull live game states, player stats, play-by-play telemetry,
    schedules, and standings from the undocumented NHL API.
    """

    BASE_WEB_URL = "https://api-web.nhle.com/v1"

    def __init__(self, retries: int = 3, backoff_factor: float = 0.5):
        """
        Initializes the extractor with a session that includes robust retry logic
        for timeouts and server errors.
        """
        self.session = requests.Session()

        # Configure retry strategy for resilient API calls
        retry_strategy = Retry(
            total=retries,  # Total number of retries
            read=retries,  # Retries on read timeouts
            connect=retries,  # Retries on connection timeouts
            backoff_factor=backoff_factor,  # Wait 0.5, 1.0, 2.0 seconds between retries
            status_forcelist=[
                429,
                500,
                502,
                503,
                504,
            ],  # Retry on these HTTP status codes
            allowed_methods=["GET"],  # Only retry GET requests
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _fetch_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to make the HTTP GET request and handle exceptions.
        """
        url = f"{self.BASE_WEB_URL}/{endpoint}"
        try:
            logger.info(f"Fetching data from: {url}")
            # The configured timeout is 10 seconds. If it times out,
            # the HTTPAdapter's Retry strategy will automatically kick in.
            response = self.session.get(url, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error after max retries while fetching {url}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error for {url}: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")

        return None

    # --- Schedules & Standings ---

    def get_standings(self) -> Optional[Dict[str, Any]]:
        """Gets NHL standings as of the current date."""
        return self._fetch_data("standings/now")

    def get_schedule(self, date_str: str = "now") -> Optional[Dict[str, Any]]:
        """
        Gets schedule of games.
        :param date_str: 'now' for today, or 'YYYY-MM-DD' for a specific date.
        """
        return self._fetch_data(f"schedule/{date_str}")

    # --- Live Game States & Telemetry ---

    def get_live_score(self) -> Optional[Dict[str, Any]]:
        """Gets linescore details for all current games."""
        return self._fetch_data("score/now")

    def get_boxscore(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Gets boxscore details for a specific game."""
        return self._fetch_data(f"gamecenter/{game_id}/boxscore")

    def get_play_by_play(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Gets play-by-play telemetry for a specific game."""
        return self._fetch_data(f"gamecenter/{game_id}/play-by-play")

    # --- Player Stats ---

    def get_player_stats(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Gets player specific landing stats."""
        return self._fetch_data(f"player/{player_id}/landing")


# Example Usage / Testing
if __name__ == "__main__":
    extractor = NHLExtractor()

    # 1. Fetch Standings
    logger.info("--- Testing Standings ---")
    standings = extractor.get_standings()
    if standings:
        print("Successfully fetched standings data.")
        print(standings)

    # 2. Fetch Schedule (Today)
    logger.info("--- Testing Schedule ---")
    schedule = extractor.get_schedule("now")
    if schedule:
        print("Successfully fetched schedule data.")
        print(schedule)

    # 3. Fetch Play-by-Play & Boxscore (requires a GAME_ID)
    # We will attempt to grab a valid GAME_ID from today's schedule to test telemetry
    if schedule and "gameWeek" in schedule and len(schedule["gameWeek"]) > 0:
        games_today = schedule["gameWeek"][0].get("games", [])

        if games_today:
            sample_game_id = games_today[0]["id"]
            logger.info(f"--- Testing Game Telemetry for Game ID: {sample_game_id} ---")

            # Fetch Boxscore
            boxscore = extractor.get_boxscore(sample_game_id)
            if boxscore:
                print(f"Successfully fetched boxscore for game {sample_game_id}.")
                print(boxscore)

            # Fetch Play-by-Play
            pbp = extractor.get_play_by_play(sample_game_id)
            if pbp:
                print(f"Successfully fetched play-by-play for game {sample_game_id}.")
                print(pbp)
        else:
            logger.info("No games scheduled for today to test telemetry endpoints.")

    # 4. Fetch Player Stats (Using a known active Player ID as an example, e.g., Connor McDavid: 8478402)
    logger.info("--- Testing Player Stats ---")
    mcdavid_id = 8478402
    player_data = extractor.get_player_stats(mcdavid_id)
    if player_data:
        print(f"Successfully fetched stats for player {mcdavid_id}.")
        print(player_data)
