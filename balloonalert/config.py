import logging
import os
from configparser import RawConfigParser


def parse_config_file(filename):
    """ Parse a Configuration File """

    alert_config = {}

    config = RawConfigParser()
    config.read(filename)

    # Filtering Settings
    alert_config['picoballoon_only'] = config.getboolean("filtering", "picoballoon_only")
    alert_config['position_filter_type'] = config.get("filtering", "position_filter_type")
    # Radius filtering
    alert_config['radius'] = config.getfloat("filtering", "radius")
    alert_config['radius_latitude'] = config.getfloat("filtering", "radius_latitude")
    alert_config['radius_longitude'] = config.getfloat("filtering", "radius_longitude")
    # Geofence Filtering
    alert_config['geofence_file'] = config.get("filtering", "geofence_file")

    # Prediction Settings
    alert_config['predictions_enabled'] = config.getboolean("predictions", "predictions_enabled")
    alert_config['prediction_min_altitude'] = config.getint("predictions", "prediction_min_altitude")
    alert_config['float_duration'] = config.getint("predictions", "float_duration")
    alert_config['prediction_rerun_time'] = config.getint("predictions", "prediction_rerun_time")
    
    # Email settings
    alert_config["email_enabled"] = config.getboolean(
        "email", "email_enabled"
    )
    alert_config["email_resend_time"] = config.getint("email", "email_resend_time")
    alert_config["email_smtp_server"] = config.get("email", "smtp_server")
    alert_config["email_smtp_port"] = config.get("email", "smtp_port")
    alert_config["email_smtp_authentication"] = config.get(
        "email", "smtp_authentication"
    )
    alert_config["email_smtp_login"] = config.get("email", "smtp_login")
    alert_config["email_smtp_password"] = config.get(
        "email", "smtp_password"
    )
    alert_config["email_from"] = config.get("email", "from")
    alert_config["email_to"] = config.get("email", "to")

    if alert_config["email_smtp_authentication"] not in [
        "None",
        "TLS",
        "SSL",
    ]:
        logging.error(
            "Config - Invalid email authentication setting. Must be None, TLS or SSL."
        )
        return None

    
    return alert_config


def read_config(filename, default_cfg="alert.cfg.example"):
    """ Read in a Balloon Alert configuration file,and return as a dict. """

    try:
        config_dict = parse_config_file(filename)
    except Exception as e:
        logging.error("Could not parse %s, trying default: %s" % (filename, str(e)))
        try:
            config_dict = parse_config_file(default_cfg)
        except Exception as e:
            logging.critical("Could not parse example config file! - %s" % str(e))
            config_dict = None

    return config_dict


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG,
    )
    print(read_config(sys.argv[1]))
