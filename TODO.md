# TODO List for WebPot Improvements

## Critical Fixes
 - [x] Fix FAKE_LOGIN undefined variable in trap_server.py
 - [x] Define FAKE_LOGIN as a proper HTML template for fallback login page

## Cloner Enhancements
 - [x] Make target URL configurable via command-line argument in cloner.py
 - [x] Automate form action modification to point to "/" in cloned HTML
 - [x] Add better error handling in cloner.py

## Configuration
 - [x] Create config.json file for customizable settings (port, log paths, etc.)
 - [x] Load configuration in trap_server.py and cloner.py

## Logging Enhancements
 - [x] Replace custom logging with Python's logging module
 - [x] Add log rotation to prevent large log files
 - [ ] Better log formatting and levels

## Error Handling
- [ ] Add input validation for URLs and parameters
- [ ] Improve exception handling throughout the code
- [ ] Add graceful error responses

## Dependencies
- [ ] Update requirements.txt if needed