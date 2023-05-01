import argparse
import datetime
import logging
import sondehub
import time
from dateutil.parser import parse
from queue import Queue
from threading import Thread
from .config import read_config
from .tawhiri import *
from .position_filters import *
from .payload_filters import *
from .email_notification import *


# Configuration
config = None

# Position filtering function pointer
position_filter = None

# Queue of telemetry packets to process
telemetry_queue = Queue()

# Store of telemetry data, keyed by callsign
telemetry_store = {}


def send_alert(callsign, alert_type, timestamp, telemetry):

    if not config['email_enabled']:
        logging.info("Not sending notification email, as notifications disabled.")
        return

    _sondehub_link = f"https://amateur.sondehub.org/?sondehub=1#!mt=Mapnik&mz=4&qm=1d&q={callsign}"

    if alert_type == "now":
        subject = f"BalloonAlert - {callsign} is within position filter limits now!"

        msg = f"Payload {callsign} observed within position filter limits at {timestamp}\n"
        msg += f"SondeHub-Amateur Link: {_sondehub_link}\n"

    else:
        subject = f"BalloonAlert - {callsign} predicted to be within position filter limits at {timestamp}."
        msg = f"Payload {callsign} predicted to be within position filter limits at {timestamp}\n"
        msg += f"SondeHub-Amateur Link: {_sondehub_link}\n"
        msg += f"(Use 'Float' prediction button)\n"

    msg += "\n\n\n"
    msg += f"Last Telemetry: {str(telemetry)}"

    send_email_notification(config, subject, msg)
        


def process_telemetry(data):
    """
    Process a telemetry packet.
    """

    logging.debug(f"Got telemetry: {data}")

    _callsign = data['payload_callsign']

    if config['picoballoon_only']:
        if not is_pico_balloon(data):
            logging.debug(f"Payload {_callsign} is not a picoballoon - discarding.")
            return

    # Create new entry in telemetry store
    if _callsign not in telemetry_store:
        telemetry_store[_callsign] = {
            'latest_data': data,
            'last_prediction': 0,
            'last_email': 0,
            'last_position': (data['lat'], data['lon'], data['alt']),
            'last_datetime': parse(data['datetime']),
            'last_ascent_rate': None,
            'last_velocity': None,
            'last_heading': None,
        }

        logging.info(f"New Payload Seen: {_callsign}")
    
    if parse(data['datetime']) != telemetry_store[_callsign]['last_datetime']:
        # Attempt to calculate ascent rate, velocity, and heading.
        pass
    

    # Write the new information into the telemetry store.
    telemetry_store[_callsign]['latest_data'] = data
    telemetry_store[_callsign]['last_position'] = (data['lat'], data['lon'], data['alt'])
    telemetry_store[_callsign]['last_datetime'] = parse(data['datetime'])

    # Compare current positions against filters.
    if position_filter(data['lat'], data['lon']):
        # Current position is within our position filter!
        logging.warning(f"Payload {_callsign} is within our position filter!")

        if (time.time() - telemetry_store[_callsign]['last_email']) > config['email_resend_time']*3600:
            # Send alert email
            logging.debug(f"Payload {_callsign} - Sending alert email.")

            send_alert(_callsign, "now", data['datetime'], data)

            telemetry_store[_callsign]['last_email'] = time.time()
        else:
            logging.info(f"Payload {_callsign} - Too soon to send email.")
    
    else:
        # Can we run a prediction?
        if (time.time() - telemetry_store[_callsign]['last_prediction']) > config['prediction_rerun_time']*3600:
            if data['alt'] > config['prediction_min_altitude']:
                # Run a forward prediction.
                logging.info(f"Payload {_callsign} - Running float prediction.")

                _pred = get_tawhiri_float_prediction(
                    launch_datetime=telemetry_store[_callsign]['last_datetime'],
                    launch_latitude=data['lat'],
                    launch_longitude=data['lon'],
                    launch_altitude=data['alt'],
                    float_time_hrs=config['float_duration']
                )

                if _pred:
                    telemetry_store[_callsign]['last_prediction_data'] = _pred
                    logging.debug(f"Payload {_callsign} - Prediction run OK, {len(_pred['path'])} data points.")

                    _pred_within_filter = None
                    for _position in _pred['path']:
                        if position_filter(_position[1], _position[2]):
                            # Prediction entry is within our position filter!
                            _pred_within_filter = _position[0]
                            break
                    
                    if _pred_within_filter:
                        logging.info(f"Payload {_callsign} - Predicted to enter position filter at {_pred_within_filter}!")

                        if (time.time() - telemetry_store[_callsign]['last_email']) > config['email_resend_time']*3600:
                            # Send alert email
                            logging.debug(f"Payload {_callsign} - Sending alert email.")

                            send_alert(_callsign, "prediction", _pred_within_filter, data)

                            telemetry_store[_callsign]['last_email'] = time.time()
                        else:
                            logging.info(f"Payload {_callsign} - Too soon to send email.")                   

                telemetry_store[_callsign]['last_prediction'] = time.time()
            else:
                logging.info(f"Payload {_callsign} - Too low in altitude to run prediction.")
        else:
            logging.info(f"Payload {_callsign} - Prediction run too recently.")
    




# Telemetry queue handling
telemetry_processing_running = True
def handle_telemetry_queue():
    logging.info("Telemetry Processing Thread Started.")
    while telemetry_processing_running:
        while telemetry_queue.qsize() > 0:
            data = telemetry_queue.get()

            try:
                process_telemetry(data)
            except Exception as e:
                logging.error(f"Error processing telemetry - {str(e)}")

        time.sleep(0.5)
    logging.info("Telemetry Processing Thread Stopped.")


# Command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "config",
    type=str,
    help=f"BalloonAlert Configuration File",
)
parser.add_argument(
    "-v", "--verbose", help="Enable debug output.", action="store_true"
)
args = parser.parse_args()

# Set log-level to DEBUG if requested
if args.verbose:
    logging_level = logging.DEBUG
else:
    logging_level = logging.INFO

# Set up logging
logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging_level)


# Read in configuration file
config = read_config(args.config)
logging.debug(f"Read configuration: {config}")


# Set up position/payload filtering
if config['position_filter_type'] == 'radius':
    position_filter = create_radius_filter(config['radius_latitude'], config['radius_longitude'], config['radius'])
    logging.info(f"Created radius filter with centre {config['radius_latitude']},{config['radius_longitude']}, and radius {config['radius']} km.")
else:
    position_filter = create_geofence(config['geofence_file'])
    logging.info(f"Created geofence filter from file {config['geofence_file']}")


# Start Telemetry Handling thread
telemetry_thread = Thread(target=handle_telemetry_queue)
telemetry_thread.start()

# Start SondeHub-Amateur Connection
logging.info("Starting SondeHub-Amateur Connection.")

shub = sondehub.Stream(on_message=telemetry_queue.put, prefix="amateur")

# Wait forever!
logging.info("Awaiting telemetry.")
try:
    while True:
        time.sleep(1)
except:
    telemetry_processing_running = False
    shub.close()