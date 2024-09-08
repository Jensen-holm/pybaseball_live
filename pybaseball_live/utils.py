__all__ = ["ROOT_URL", "ENDPOINT_URL"]

ROOT_URL = "https://statsapi.mlb.com"

ENDPOINT_URL = ROOT_URL + "/api/v1/{endpoint}"

GAME_ENDPOINT_ROOT = ROOT_URL + "/api/v1.1/game/{game_id}/feed/live"
