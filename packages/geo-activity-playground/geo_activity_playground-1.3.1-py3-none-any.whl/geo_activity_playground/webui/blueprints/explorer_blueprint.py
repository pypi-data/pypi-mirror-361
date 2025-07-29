import abc
import datetime
import hashlib
import io
import logging
from collections.abc import Iterable
from typing import Union

import altair as alt
import geojson
import matplotlib
import matplotlib.pyplot as pl
import numpy as np
import pandas as pd
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import Response
from flask import url_for
from flask.typing import ResponseReturnValue

from ...core.config import ConfigAccessor
from ...core.coordinates import Bounds
from ...core.datamodel import Activity
from ...core.datamodel import DB
from ...core.raster_map import ImageTransform
from ...core.raster_map import TileGetter
from ...core.tiles import compute_tile
from ...core.tiles import get_tile_upper_left_lat_lon
from ...explorer.grid_file import get_border_tiles
from ...explorer.grid_file import make_grid_file_geojson
from ...explorer.grid_file import make_grid_file_gpx
from ...explorer.grid_file import make_grid_points
from ...explorer.tile_visits import compute_tile_evolution
from ...explorer.tile_visits import TileEvolutionState
from ...explorer.tile_visits import TileVisitAccessor
from ..authenticator import Authenticator
from ..authenticator import needs_authentication

alt.data_transformers.enable("vegafusion")

logger = logging.getLogger(__name__)


def blend_color(
    base: np.ndarray, addition: Union[np.ndarray, float], opacity: float
) -> np.ndarray:
    return (1 - opacity) * base + opacity * addition


class ColorStrategy(abc.ABC):
    @abc.abstractmethod
    def color_image(
        self, tile_xy: tuple[int, int], grayscale: np.ndarray
    ) -> np.ndarray:
        pass


class MaxClusterColorStrategy(ColorStrategy):
    def __init__(self, evolution_state, tile_visits):
        self.evolution_state = evolution_state
        self.tile_visits = tile_visits
        self.max_cluster_members = max(
            evolution_state.clusters.values(),
            key=len,
        )

    def color_image(
        self, tile_xy: tuple[int, int], grayscale: np.ndarray
    ) -> np.ndarray:
        if tile_xy in self.max_cluster_members:
            return blend_color(grayscale, np.array([[[55, 126, 184]]]) / 256, 0.3)
        elif tile_xy in self.evolution_state.memberships:
            return blend_color(grayscale, np.array([[[77, 175, 74]]]) / 256, 0.3)
        elif tile_xy in self.tile_visits:
            return blend_color(grayscale, 0.0, 0.3)
        else:
            return grayscale


class ColorfulClusterColorStrategy(ColorStrategy):
    def __init__(self, evolution_state: TileEvolutionState, tile_visits):
        self.evolution_state = evolution_state
        self.tile_visits = tile_visits
        self.max_cluster_members = max(
            evolution_state.clusters.values(),
            key=len,
        )
        self._cmap = matplotlib.colormaps["hsv"]

    def color_image(
        self, tile_xy: tuple[int, int], grayscale: np.ndarray
    ) -> np.ndarray:
        if tile_xy in self.evolution_state.memberships:
            cluster_id = self.evolution_state.memberships[tile_xy]
            m = hashlib.sha256()
            m.update(str(cluster_id).encode())
            d = int(m.hexdigest(), base=16) / (256.0**m.digest_size)
            return blend_color(grayscale, np.array([[self._cmap(d)[:3]]]), 0.3)
        elif tile_xy in self.tile_visits:
            return blend_color(grayscale, 0.0, 0.3)
        else:
            return grayscale


class VisitTimeColorStrategy(ColorStrategy):
    def __init__(self, tile_visits, use_first=True):
        self.tile_visits = tile_visits
        self.use_first = use_first

    def color_image(
        self, tile_xy: tuple[int, int], grayscale: np.ndarray
    ) -> np.ndarray:
        if tile_xy in self.tile_visits:
            today = datetime.date.today()
            cmap = matplotlib.colormaps["plasma"]
            tile_info = self.tile_visits[tile_xy]
            relevant_time = (
                tile_info["first_time"] if self.use_first else tile_info["last_time"]
            )
            last_age_days = (today - relevant_time.date()).days
            color = cmap(max(1 - last_age_days / (2 * 365), 0.0))
            return blend_color(grayscale, np.array([[color[:3]]]), 0.3)
        else:
            return grayscale


class NumVisitsColorStrategy(ColorStrategy):
    def __init__(self, tile_visits):
        self.tile_visits = tile_visits

    def color_image(
        self, tile_xy: tuple[int, int], grayscale: np.ndarray
    ) -> np.ndarray:
        if tile_xy in self.tile_visits:
            cmap = matplotlib.colormaps["viridis"]
            tile_info = self.tile_visits[tile_xy]
            color = cmap(min(len(tile_info["activity_ids"]) / 50, 1.0))
            return blend_color(grayscale, np.array([[color[:3]]]), 0.3)
        else:
            return grayscale


def make_explorer_blueprint(
    authenticator: Authenticator,
    tile_visit_accessor: TileVisitAccessor,
    config_accessor: ConfigAccessor,
    tile_getter: TileGetter,
    image_transforms: dict[str, ImageTransform],
) -> Blueprint:
    blueprint = Blueprint("explorer", __name__, template_folder="templates")

    @blueprint.route("/enable-zoom-level/<int:zoom>")
    @needs_authentication(authenticator)
    def enable_zoom_level(zoom: int) -> ResponseReturnValue:
        if 0 <= zoom <= 19:
            config_accessor().explorer_zoom_levels.append(zoom)
            config_accessor().explorer_zoom_levels.sort()
            config_accessor.save()
            compute_tile_evolution(tile_visit_accessor, config_accessor())
            flash(f"Enabled {zoom=} for explorer tiles.", category="success")
        else:
            flash(f"{zoom=} is not valid, must be between 0 and 19.", category="danger")
        return redirect(url_for(".map", zoom=zoom))

    @blueprint.route(
        "/<int:zoom>/<float:north>/<float:east>/<float:south>/<float:west>/missing.<suffix>"
    )
    def download_missing(
        zoom: int, north: float, east: float, south: float, west: float, suffix: str
    ) -> ResponseReturnValue:
        x1, y1 = compute_tile(north, west, zoom)
        x2, y2 = compute_tile(south, east, zoom)
        tile_bounds = Bounds(x1, y1, x2 + 2, y2 + 2)

        tile_histories = tile_visit_accessor.tile_state["tile_history"]
        tiles = tile_histories[zoom]
        points = get_border_tiles(tiles, zoom, tile_bounds)
        if suffix == "geojson":
            result = make_grid_file_geojson(points)
        elif suffix == "gpx":
            result = make_grid_file_gpx(points)

        mimetypes = {"geojson": "application/json", "gpx": "application/xml"}
        return Response(
            result,
            mimetype=mimetypes[suffix],
            headers={"Content-disposition": "attachment"},
        )

    @blueprint.route(
        "/<int:zoom>/<float:north>/<float:east>/<float:south>/<float:west>/explored.<suffix>"
    )
    def download_explored(
        zoom: int, north: float, east: float, south: float, west: float, suffix: str
    ) -> ResponseReturnValue:
        x1, y1 = compute_tile(north, west, zoom)
        x2, y2 = compute_tile(south, east, zoom)
        tile_bounds = Bounds(x1, y1, x2 + 2, y2 + 2)

        tile_visits = tile_visit_accessor.tile_state["tile_visits"]
        tiles = tile_visits[zoom]
        points = make_grid_points(
            (tile for tile in tiles.keys() if tile_bounds.contains(*tile)), zoom
        )
        if suffix == "geojson":
            result = make_grid_file_geojson(points)
        elif suffix == "gpx":
            result = make_grid_file_gpx(points)

        mimetypes = {"geojson": "application/json", "gpx": "application/xml"}
        return Response(
            result,
            mimetype=mimetypes[suffix],
            headers={"Content-disposition": "attachment"},
        )

    @blueprint.route("/<int:zoom>/server-side")
    def server_side(zoom: int) -> ResponseReturnValue:
        if zoom not in config_accessor().explorer_zoom_levels:
            return {"zoom_level_not_generated": zoom}

        tile_evolution_state = tile_visit_accessor.tile_state["evolution_state"][zoom]
        tile_history = tile_visit_accessor.tile_state["tile_history"][zoom]

        medians = tile_history[["tile_x", "tile_y"]].median()
        median_lat, median_lon = get_tile_upper_left_lat_lon(
            medians["tile_x"], medians["tile_y"], zoom
        )

        context = {
            "center": {
                "latitude": median_lat,
                "longitude": median_lon,
                "bbox": (
                    bounding_box_for_biggest_cluster(
                        tile_evolution_state.clusters.values(), zoom
                    )
                    if len(tile_evolution_state.memberships) > 0
                    else {}
                ),
            },
            "plot_tile_evolution": plot_tile_evolution(tile_history),
            "plot_cluster_evolution": plot_cluster_evolution(
                tile_evolution_state.cluster_evolution
            ),
            "plot_square_evolution": plot_square_evolution(
                tile_evolution_state.square_evolution
            ),
            "zoom": zoom,
            "num_tiles": len(tile_history),
            "num_cluster_tiles": len(tile_evolution_state.memberships),
            "square_x": tile_evolution_state.square_x,
            "square_y": tile_evolution_state.square_y,
            "square_size": tile_evolution_state.max_square_size,
            "max_cluster_size": max(map(len, tile_evolution_state.clusters.values())),
        }
        return render_template("explorer/server-side.html.j2", **context)

    @blueprint.route("/<int:zoom>/tile/<int:z>/<int:x>/<int:y>.png")
    def tile(zoom: int, z: int, x: int, y: int) -> ResponseReturnValue:
        tile_visits = tile_visit_accessor.tile_state["tile_visits"][zoom]
        evolution_state = tile_visit_accessor.tile_state["evolution_state"][zoom]

        map_tile = np.array(tile_getter.get_tile(z, x, y)) / 255
        grayscale = image_transforms["grayscale"].transform_image(map_tile)
        square_line_width = 3
        square_color = np.array([[[228, 26, 28]]]) / 256

        color_strategy_name = request.args.get("color_strategy", "colorful_cluster")
        if color_strategy_name == "default":
            color_strategy_name = config_accessor().cluster_color_strategy
        match color_strategy_name:
            case "max_cluster":
                color_strategy = MaxClusterColorStrategy(evolution_state, tile_visits)
            case "colorful_cluster":
                color_strategy = ColorfulClusterColorStrategy(
                    evolution_state, tile_visits
                )
            case "first":
                color_strategy = VisitTimeColorStrategy(tile_visits, use_first=True)
            case "last":
                color_strategy = VisitTimeColorStrategy(tile_visits, use_first=False)
            case "visits":
                color_strategy = NumVisitsColorStrategy(tile_visits)
            case _:
                raise ValueError("Unsupported color strategy.")

        if z >= zoom:
            factor = 2 ** (z - zoom)
            tile_x = x // factor
            tile_y = y // factor
            tile_xy = (tile_x, tile_y)
            result = color_strategy.color_image(tile_xy, grayscale)

            if x % factor == 0:
                result[:, 0, :] = 0.5
            if y % factor == 0:
                result[0, :, :] = 0.5

                if (
                    evolution_state.square_x is not None
                    and evolution_state.square_y is not None
                ):
                    if (
                        x % factor == 0
                        and tile_x == evolution_state.square_x
                        and evolution_state.square_y
                        <= tile_y
                        < evolution_state.square_y + evolution_state.max_square_size
                    ):
                        result[:, 0:square_line_width] = blend_color(
                            result[:, 0:square_line_width], square_color, 0.5
                        )
                    if (
                        y % factor == 0
                        and tile_y == evolution_state.square_y
                        and evolution_state.square_x
                        <= tile_x
                        < evolution_state.square_x + evolution_state.max_square_size
                    ):
                        result[0:square_line_width, :] = blend_color(
                            result[0:square_line_width, :], square_color, 0.5
                        )

                    if (
                        (x + 1) % factor == 0
                        and (x + 1) // factor
                        == evolution_state.square_x + evolution_state.max_square_size
                        and evolution_state.square_y
                        <= tile_y
                        < evolution_state.square_y + evolution_state.max_square_size
                    ):
                        result[:, -square_line_width:] = blend_color(
                            result[:, -square_line_width:], square_color, 0.5
                        )
                    if (
                        (y + 1) % factor == 0
                        and (y + 1) // factor
                        == evolution_state.square_y + evolution_state.max_square_size
                        and evolution_state.square_x
                        <= tile_x
                        < evolution_state.square_x + evolution_state.max_square_size
                    ):
                        result[-square_line_width:, :] = blend_color(
                            result[-square_line_width:, :], square_color, 0.5
                        )
        else:
            result = grayscale
            factor = 2 ** (zoom - z)
            width = 256 // factor
            for xo in range(factor):
                for yo in range(factor):
                    tile_x = x * factor + xo
                    tile_y = y * factor + yo
                    tile_xy = (tile_x, tile_y)
                    if tile_xy in tile_visits:
                        result[
                            yo * width : (yo + 1) * width, xo * width : (xo + 1) * width
                        ] = color_strategy.color_image(
                            tile_xy,
                            grayscale[
                                yo * width : (yo + 1) * width,
                                xo * width : (xo + 1) * width,
                            ],
                        )

                        if (
                            evolution_state.square_x is not None
                            and evolution_state.square_y is not None
                        ):
                            if (
                                tile_x == evolution_state.square_x
                                and evolution_state.square_y
                                <= tile_y
                                < evolution_state.square_y
                                + evolution_state.max_square_size
                            ):
                                result[
                                    yo * width : (yo + 1) * width,
                                    xo * width : xo * width + square_line_width,
                                ] = blend_color(
                                    result[
                                        yo * width : (yo + 1) * width,
                                        xo * width : xo * width + square_line_width,
                                    ],
                                    square_color,
                                    0.5,
                                )
                            if (
                                tile_y == evolution_state.square_y
                                and evolution_state.square_x
                                <= tile_x
                                < evolution_state.square_x
                                + evolution_state.max_square_size
                            ):
                                result[
                                    yo * width : yo * width + square_line_width,
                                    xo * width : (xo + 1) * width,
                                ] = blend_color(
                                    result[
                                        yo * width : yo * width + square_line_width,
                                        xo * width : (xo + 1) * width,
                                    ],
                                    square_color,
                                    0.5,
                                )

                            if (
                                tile_x + 1
                                == evolution_state.square_x
                                + evolution_state.max_square_size
                                and evolution_state.square_y
                                <= tile_y
                                < evolution_state.square_y
                                + evolution_state.max_square_size
                            ):
                                result[
                                    yo * width : (yo + 1) * width,
                                    (xo + 1) * width
                                    - square_line_width : (xo + 1) * width,
                                ] = blend_color(
                                    result[
                                        yo * width : (yo + 1) * width,
                                        (xo + 1) * width
                                        - square_line_width : (xo + 1) * width,
                                    ],
                                    square_color,
                                    0.5,
                                )

                            if (
                                tile_y + 1
                                == evolution_state.square_y
                                + evolution_state.max_square_size
                                and evolution_state.square_x
                                <= tile_x
                                < evolution_state.square_x
                                + evolution_state.max_square_size
                            ):
                                result[
                                    (yo + 1) * width
                                    - square_line_width : (yo + 1) * width,
                                    xo * width : (xo + 1) * width,
                                ] = blend_color(
                                    result[
                                        (yo + 1) * width
                                        - square_line_width : (yo + 1) * width,
                                        xo * width : (xo + 1) * width,
                                    ],
                                    square_color,
                                    0.5,
                                )
                    if width >= 64:
                        result[yo * width, :, :] = 0.5
                        result[:, xo * width, :] = 0.5
        f = io.BytesIO()
        pl.imsave(f, result, format="png")
        return Response(bytes(f.getbuffer()), mimetype="image/png")

    @blueprint.route("/<int:zoom>/info/<float:latitude>/<float:longitude>")
    def info(zoom: int, latitude: float, longitude: float) -> dict:
        tile_visits = tile_visit_accessor.tile_state["tile_visits"][zoom]
        evolution_state = tile_visit_accessor.tile_state["evolution_state"][zoom]
        tile_xy = compute_tile(latitude, longitude, zoom)
        if tile_xy in tile_visits:
            tile_info = tile_visits[tile_xy]
            first = DB.session.get_one(Activity, tile_info["first_id"])
            last = DB.session.get_one(Activity, tile_info["last_id"])
            result = {
                "tile_xy": f"{tile_xy}",
                "num_visits": len(tile_info["activity_ids"]),
                "first_activity_id": first.id,
                "first_activity_name": first.name,
                "first_time": tile_info["first_time"].isoformat(),
                "last_activity_id": last.id,
                "last_activity_name": last.name,
                "last_time": tile_info["last_time"].isoformat(),
                "is_cluster": tile_xy in evolution_state.memberships,
                "this_cluster_size": len(
                    evolution_state.clusters.get(
                        evolution_state.memberships.get(tile_xy, None), []
                    )
                ),
            }
        else:
            result = {}
        return result

    return blueprint


def bounding_box_for_biggest_cluster(
    clusters: Iterable[list[tuple[int, int]]], zoom: int
) -> str:
    biggest_cluster = max(clusters, key=lambda members: len(members))
    min_x = min(x for x, y in biggest_cluster)
    max_x = max(x for x, y in biggest_cluster)
    min_y = min(y for x, y in biggest_cluster)
    max_y = max(y for x, y in biggest_cluster)
    lat_max, lon_min = get_tile_upper_left_lat_lon(min_x, min_y, zoom)
    lat_min, lon_max = get_tile_upper_left_lat_lon(max_x, max_y, zoom)
    return geojson.dumps(
        geojson.Feature(
            geometry=geojson.Polygon(
                [
                    [
                        (lon_min, lat_max),
                        (lon_max, lat_max),
                        (lon_max, lat_min),
                        (lon_min, lat_min),
                        (lon_min, lat_max),
                    ]
                ]
            ),
        )
    )


def plot_tile_evolution(tiles: pd.DataFrame) -> str:
    if len(tiles) == 0:
        return ""
    tiles["count"] = np.arange(1, len(tiles) + 1)
    return (
        alt.Chart(tiles, title="Tiles")
        .mark_line(interpolate="step-after")
        .encode(alt.X("time", title="Time"), alt.Y("count", title="Number of tiles"))
        .interactive(bind_y=False)
        .to_json(format="vega")
    )


def plot_cluster_evolution(cluster_evolution: pd.DataFrame) -> str:
    if len(cluster_evolution) == 0:
        return ""
    return (
        alt.Chart(cluster_evolution, title="Cluster")
        .mark_line(interpolate="step-after")
        .encode(
            alt.X("time", title="Time"),
            alt.Y("max_cluster_size", title="Maximum cluster size"),
        )
        .interactive(bind_y=False)
        .to_json(format="vega")
    )


def plot_square_evolution(square_evolution: pd.DataFrame) -> str:
    if len(square_evolution) == 0:
        return ""
    return (
        alt.Chart(square_evolution, title="Square")
        .mark_line(interpolate="step-after")
        .encode(
            alt.X("time", title="Time"),
            alt.Y("max_square_size", title="Maximum square size"),
        )
        .interactive(bind_y=False)
        .to_json(format="vega")
    )
