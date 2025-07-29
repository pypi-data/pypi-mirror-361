import logging
import textwrap

import click
from dateutil.parser import parse

from zet import api, __version__
from zet.app import ZetApp
from zet.decorators import async_command, pass_session
from zet.entities import Stop
from zet.output import generate_table


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.version_option(__version__)
def zet(debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)


@zet.command()
@async_command
@pass_session
async def news(session):
    """Show news feed"""
    news = await api.get_newsfeed(session)

    def _generator():
        first = True
        for item in news:
            if not first:
                yield click.style("-" * 80, dim=True) + "\n\n"
            yield click.style(item["title"], bold=True) + "\n\n"
            for line in textwrap.wrap(item["description"], 80):
                yield line + "\n"
            yield "\n"
            yield click.style(item["link"], underline=True, dim=True) + "\n"
            yield click.style(item["datePublished"], dim=True) + "\n\n"
            first = False

    click.echo_via_pager(_generator())


@zet.command()
@async_command
@pass_session
async def tui(session):
    app = ZetApp(session)
    await app.run_async()


@zet.command()
@async_command
@pass_session
async def routes(session):
    """List routes"""
    routes = await api.get_routes(session)
    headers = ["ID", "From", "To"]
    rows = [[r["id"], r["departureHeadsign"], r["destinationHeadsign"]] for r in routes]
    click.echo_via_pager(generate_table(headers, rows))


@zet.command()
@async_command
@pass_session
async def stops(session):
    """List stops"""
    stops = await api.get_stops(session)
    headers = ["ID", "Name", "Type", "Latitude", "Longitude", "Trips"]
    rows = [
        [s["id"], s["name"], s["routeType"], s["stopLat"], s["stopLong"], _trips(s)] for s in stops
    ]
    click.echo_via_pager(generate_table(headers, rows))


def _trips(stop: Stop):
    return ", ".join(trip["routeCode"] for trip in stop["trips"])


@zet.command()
@click.argument("stop_id")
@async_command
@pass_session
async def trips(session, stop_id: str):
    """List arrivals for a given stop"""
    trips = await api.get_incoming_trips(session, stop_id)
    headers = ["#", "Destination", "Arrival", "Tracked?"]
    rows = [
        [
            t["routeShortName"],
            t["headsign"],
            _time(t["expectedArrivalDateTime"]),
            t["hasLiveTracking"],
        ]
        for t in trips
    ]
    table = "".join(generate_table(headers, rows))
    click.echo(table)


@zet.command()
@click.argument("route_id")
@async_command
@pass_session
async def route_trips(session, route_id: str):
    """List trips for a given route"""
    trips = await api.get_route_trips(session, route_id)
    headers = ["Trip ID", "Direction", "Headsign", "Arrival", "Tracked?"]
    rows = [
        [
            t["id"],
            t["direction"],
            t["headsign"],
            _time(t["arrivalDateTime"]),
            t["hasLiveTracking"],
        ]
        for t in trips
    ]
    click.echo_via_pager(generate_table(headers, rows))


@zet.command()
@async_command
@pass_session
async def vehicles(session):
    """List vehicles"""
    vehicles = await api.get_vehicles(session)
    headers = ["#", "Garage#", "Plate", "Description"]
    rows = [
        [
            v["id"],
            v["garageNumber"],
            v["numberPlate"],
            v["description"].strip(),
        ]
        for v in vehicles
    ]
    click.echo_via_pager(generate_table(headers, rows))


def _time(value: str) -> str:
    return parse(value).time().strftime("%H:%M")
