import fastf1
from fastf1 import utils
from tqdm import tqdm

fastf1.Cache.enable_cache('cache')

class F1DataLoader:
    def __init__(self, year, sessions=['FP1', 'FP2', 'FP3', 'Q', 'R']):
        """
        Fully automatic F1 Data Loader
        year: int - season year
        sessions: list of sessions to load (default FP1, FP2, FP3, Q, R)
        """
        self.year = year
        self.sessions_to_load = sessions
        self.data = {}  # nested dictionary: data[gp][session][driver] = {...}
        self.schedule = None

    # ----------------------------
    # Load full event schedule
    # ----------------------------
    def load_event_schedule(self):
        """
        Load full season schedule
        """
        self.schedule = fastf1.get_event_schedule(self.year)
        return self.schedule

    # ----------------------------
    # Load all events, sessions, drivers
    # ----------------------------
    def load_season_data(self, progress_bar=True):
        """
        Loop through all events and sessions, fetching all relevant data automatically
        """
        if self.schedule is None:
            self.load_event_schedule()

        for gp_name in tqdm(self.schedule['EventName'], desc=f"Loading {self.year} season", disable=not progress_bar):
            self.data[gp_name] = {}

            for session_id in self.sessions_to_load:
                try:
                    # Load session
                    session = fastf1.get_session(self.year, gp_name, session_id)
                    session.load()

                    # Initialize storage
                    self.data[gp_name][session_id] = {
                        'laps': session.laps,
                        'results': None,
                        'track_info': session.circuit,
                        'track_status': session.track_status,
                        'session_status': session.session_status,
                        'race_control_messages': session.race_control_messages,
                        'telemetry': {}
                    }

                    # Session results (may not exist for practice)
                    try:
                        self.data[gp_name][session_id]['results'] = session.results
                    except Exception:
                        self.data[gp_name][session_id]['results'] = None

                    # Driver telemetry
                    for driver in session.drivers:
                        driver_laps = session.laps.pick_driver(driver)
                        fastest_lap = driver_laps.pick_fastest() if not driver_laps.empty else None
                        telemetry = fastest_lap.get_telemetry() if fastest_lap is not None else None

                        self.data[gp_name][session_id]['telemetry'][driver] = {
                            'laps': driver_laps,
                            'fastest_lap': fastest_lap,
                            'telemetry': telemetry
                        }

                except Exception as e:
                    print(f"Skipping {gp_name} {session_id} due to error: {e}")

    # ----------------------------
    # Getter functions
    # ----------------------------
    def get_driver_telemetry(self, gp_name, session_id, driver):
        try:
            return self.data[gp_name][session_id]['telemetry'][driver]['telemetry']
        except KeyError:
            return None

    def get_driver_laps(self, gp_name, session_id, driver):
        try:
            return self.data[gp_name][session_id]['telemetry'][driver]['laps']
        except KeyError:
            return None

    def get_fastest_lap(self, gp_name, session_id, driver):
        try:
            return self.data[gp_name][session_id]['telemetry'][driver]['fastest_lap']
        except KeyError:
            return None

    def get_results(self, gp_name, session_id):
        try:
            return self.data[gp_name][session_id]['results']
        except KeyError:
            return None

    def get_track_info(self, gp_name, session_id):
        try:
            return self.data[gp_name][session_id]['track_info']
        except KeyError:
            return None

    def get_track_status(self, gp_name, session_id):
        try:
            return self.data[gp_name][session_id]['track_status']
        except KeyError:
            return None

    def get_session_status(self, gp_name, session_id):
        try:
            return self.data[gp_name][session_id]['session_status']
        except KeyError:
            return None

    def get_race_control_messages(self, gp_name, session_id):
        try:
            return self.data[gp_name][session_id]['race_control_messages']
        except KeyError:
            return None

if __name__ == "__main__":
    loader = F1DataLoader(2025)
    loader.load_season_data(progress_bar=True)