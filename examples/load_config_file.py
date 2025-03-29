# telemetry-obd-log-to-csv/examples/load_config_file.py
"""given a telemetry-obd config file, produce a list of the OBD commands
listed in the specified configuration section.

E.g. --startup, --housekeeping and --cycle
"""
from argparse import ArgumentParser
import configparser

def load_config_file(settings_file):
    """Load three sets of OBD command names."""
    config = configparser.ConfigParser()
    config.read(settings_file)
    startup = (config['STARTUP NAMES']['startup']).split()
    housekeeping = (config['HOUSEKEEPING NAMES']['housekeeping']).split()
    cycle = (config['CYCLE NAMES']['cycle']).split()

    return startup, housekeeping, cycle

def command_line_options()->dict:
    parser = ArgumentParser(prog="obd_log_evaluation",
                        description="""
                            Given a telemetry_obd.obd_logger config file, produce a list of the OBD commands
                            listed in the specified configuration section.
                        """)

    parser.add_argument(
        "--verbose",
        help="Turn verbose output on. Default is off.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "--startup",
        help="Output startup OBD commands. Default is off.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "--housekeeping",
        help="Output housekeeping OBD commands. Default is off.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "--cycle",
        help="Output cycle OBD commans. Default is off.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "config_file",
        help="path for obd_logger configuration file.",
        default=None,
    )

    return vars(parser.parse_args())


def main():
    args = command_line_options()

    config_file = args['config_file']
    verbose = args['verbose']
    startup = args['startup']
    housekeeping = args['housekeeping']
    cycle = args['cycle']

    if verbose:
        print(f"verbose: {verbose}")
        print(f"config_file: {config_file}")
        print(f"startup: {startup}")
        print(f"housekeeping: {housekeeping}")
        print(f"cycle: {cycle}")

    if not (startup or housekeeping or cycle):
        raise ValueError("Must specify at least one type of OBD Commands to output.")

    startup_commands, housekeeping_commands, cycle_commands = load_config_file(config_file)

    commands = []
    if startup:
        commands += startup_commands
    if housekeeping:
        commands += housekeeping_commands
    if cycle:
        commands += cycle_commands

    command_string = ""
    for command in commands:
        command_string += f",{command}" if command_string != "" else command

    print(command_string)

if __name__ == "__main__":
    main()
