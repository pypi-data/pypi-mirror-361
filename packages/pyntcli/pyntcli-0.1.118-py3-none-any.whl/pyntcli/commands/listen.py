import argparse
from copy import deepcopy
import os
import webbrowser
from http import HTTPStatus
import time
import tempfile
import json
from subprocess import Popen, PIPE
from functools import partial

from pyntcli.pynt_docker import pynt_container
from pyntcli.ui import ui_thread
from pyntcli.commands import util, sub_command
from pyntcli.ui import report as cli_reporter
from pyntcli.transport import pynt_requests


def listen_usage():
    return (
        ui_thread.PrinterText("Listen integration to Pynt. Run a security scan with routed traffic.")
        .with_line("")
        .with_line("Usage:", style=ui_thread.PrinterText.HEADER)
        .with_line("\tpynt listen [OPTIONS]")
        .with_line("")
        .with_line("Options:", style=ui_thread.PrinterText.HEADER)
        .with_line('\t--captured-domains - Pynt will scan only these domains and subdomains. For all domains write "*"')
        .with_line('\t--test-name - A name for your Pynt scan')
        .with_line("\t--port - Set the port pynt will listen to (DEFAULT: random)")
        .with_line("\t--ca-path - The path to the CA file in PEM format")
        .with_line("\t--proxy-port - Set the port proxied traffic should be routed to (DEFAULT: 6666)")
        .with_line("\t--report - If present will save the generated report in this path.")
        .with_line("\t--application-id - Attach the scan to an application, you can find the ID in your applications area at app.pynt.io")
        .with_line("\t--application-name - Attach the scan to an application, application will be created automatically if it does not exist.")
        .with_line("\t--insecure - use when target uses self signed certificates")
        .with_line("\t--host-ca - path to the CA file in PEM format to enable SSL certificate verification for pynt when running through a VPN.")
        .with_line("\t--severity-level - 'all', 'medium', 'high', 'critical', 'none' (default) ")
        .with_line("\t--tag - Tag the scan. Repeat for multiple tags")
        .with_line("\t--verbose - Use to get more detailed information about the run")
    )


class ListenSubCommand(sub_command.PyntSubCommand):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.scan_id = ""
        self.proxy_sleep_interval = 2
        self.proxy_healthcheck_buffer = 10
        self.proxy_server_base_url = "http://localhost:{}/api"

    def print_usage(self, *args):
        ui_thread.print(listen_usage())

    def add_cmd(self, parent: argparse._SubParsersAction) -> argparse.ArgumentParser:
        listen_cmd = parent.add_parser(self.name)
        listen_cmd.add_argument("--port", "-p", help="", type=int, default=util.find_open_port())
        listen_cmd.add_argument("--proxy-port", help="", type=int, default=6666)
        listen_cmd.add_argument("--captured-domains", nargs="+", help="", default="", required=True)
        listen_cmd.add_argument("--test-name", help="", default="", required=False)
        listen_cmd.add_argument("--allow-errors", action="store_true")
        listen_cmd.add_argument("--ca-path", type=str, default="")
        listen_cmd.add_argument("--report", type=str, default="")
        listen_cmd.add_argument("--severity-level", choices=["all", "medium", "high", "critical", "none"], default="none")
        listen_cmd.print_usage = self.print_usage
        listen_cmd.print_help = self.print_usage
        return listen_cmd

    def _start_proxy(self, args):
        res = pynt_requests.put(self.proxy_server_base_url.format(args.port) + "/proxy/start")
        res.raise_for_status()
        self.scan_id = res.json()["scanId"]

    def _stop_proxy(self, args):
        start = time.time()
        while start + self.proxy_healthcheck_buffer > time.time():
            res = pynt_requests.put(
                self.proxy_server_base_url.format(args.port) + "/proxy/stop",
                json={"scanId": self.scan_id},
            )
            if res.status_code == HTTPStatus.OK:
                return
            time.sleep(self.proxy_sleep_interval)
        raise TimeoutError()

    def _get_report(self, args, report_format):
        while True:
            res = pynt_requests.get(
                self.proxy_server_base_url.format(args.port)
                + "/report?format={}".format(report_format),
                params={"scanId": self.scan_id},
            )
            if res.status_code == HTTPStatus.OK:
                return res.text
            if res.status_code == HTTPStatus.ACCEPTED:
                time.sleep(self.proxy_sleep_interval)
                continue
            if res.status_code == 517:  # pynt did not recieve any requests
                ui_thread.print(
                    ui_thread.PrinterText(
                        res.json()["message"], ui_thread.PrinterText.WARNING
                    )
                )
                return
            ui_thread.print("Error in polling for scan report: {}".format(res.text))
            return

    def run_cmd(self, args: argparse.Namespace):
        container_config = pynt_container.DockerContainerConfig(
            args,
            "proxy",
            pynt_container.api_port(args.port),
            pynt_container.proxy_port(args.proxy_port),
        )

        for host in args.captured_domains:
            container_config.docker_arguments += ["--host-targets", host]

        if args.test_name:
            container_config.docker_arguments += ["--test-name", args.test_name]

        if "ca_path" in args and args.ca_path:
            if not os.path.isfile(args.ca_path):
                ui_thread.print(
                    ui_thread.PrinterText(
                        "Could not find the provided ca path, please provide with a valid path",
                        ui_thread.PrinterText.WARNING,
                    )
                )
                return

            ca_name = os.path.basename(args.ca_path)
            container_config.docker_arguments += ["--ca-path", ca_name]
            container_config.mounts.append(
                pynt_container.create_mount(
                    os.path.abspath(args.ca_path), "/etc/pynt/{}".format(ca_name)
                )
            )

        proxy_docker = pynt_container.PyntContainerNative(container_config)

        proxy_docker.prepare_client()
        proxy_docker.pre_run_validation(args.port)
        proxy_docker.run()

        ui_thread.print_generator(proxy_docker.stdout)

        util.wait_for_healthcheck("http://localhost:{}".format(args.port))
        ui_thread.print_verbose(util.GOT_INITIAL_HEALTHCHECK_MESSAGE)
        ui_thread.print(ui_thread.PrinterText(
            "Pynt docker is ready",
            ui_thread.PrinterText.INFO,
        ))

        self._start_proxy(args)

        ui_thread.print(
            ui_thread.PrinterText(
                "\nListening to traffic on port: {}".format(args.proxy_port),
                ui_thread.PrinterText.DEFAULT,
            )
            .with_line(
                "Will scan APIs that belong to '{}' domains only".format(
                    args.captured_domains
                )
            )
            .with_line(""))

        ui_thread.print(
            ui_thread.PrinterText(
                "Press Enter to stop recording traffic and run security scan...",
                ui_thread.PrinterText.HEADER,
            ))

        input()

        self._stop_proxy(args)

        with ui_thread.progress(
                "ws://localhost:{}/progress?scanId={}".format(args.port, self.scan_id),
                partial(lambda *args: None),
                "scan in progress...", 100):
            html_report = self._get_report(args, "html")
            html_report_path = os.path.join(
                tempfile.gettempdir(), "pynt_report_{}.html".format(int(time.time()))
            )

            json_report = self._get_report(args, "json")
            json_report_path = os.path.join(
                tempfile.gettempdir(), "pynt_report_{}.json".format(int(time.time()))
            )

            if "report" in args and args.report:
                full_path = os.path.abspath(args.report)
                html_report_path = util.get_user_report_path(full_path, "html")
                json_report_path = util.get_user_report_path(full_path, "json")

            if html_report:
                with open(html_report_path, "w", encoding="utf-8") as html_file:
                    html_file.write(html_report)
                webbrowser.open("file://{}".format(html_report_path))

            if json_report:
                with open(json_report_path, "w", encoding="utf-8") as json_file:
                    json_file.write(json_report)
                reporter = cli_reporter.PyntReporter(json_report_path)
                reporter.print_summary()

            if json_report:
                json_obj = json.loads(json_report)
                if json_obj:
                    util.check_for_findings_or_warnings(args, json_obj)
                    util.check_severity(args.severity_level, json_obj)
