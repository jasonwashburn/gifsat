from pathlib import Path

import matplotlib.pyplot as plt
import requests
import xarray as xr
from PIL import Image
from pydantic import BaseModel


class BBox(BaseModel):
    x_min: int
    x_max: int
    y_min: int
    y_max: int

    def to_extent(self):
        return (self.x_min, self.x_max, self.y_min, self.y_max)


def make_gif(list_of_pngs, file_path):
    frames = [Image.open(image).convert("RGBA") for image in list_of_pngs]
    frame_one = frames[0]
    frame_one.save(
        file_path,
        format="GIF",
        append_images=frames,
        save_all=True,
        duration=120,
        loop=0,
        optimize=True,
    )


def make_centered_extent(lon, lat, width, height, offset=(0, 0)):
    x_min = lon - (width / 2) + offset[0]
    x_max = lon + (width / 2) + offset[0]
    y_min = lat - (height / 2) + offset[1]
    y_max = lat + (height / 2) + offset[1]
    return BBox(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)


def get_storm_info():
    url = "https://www.nhc.noaa.gov/CurrentStorms.json"
    resp = requests.get(url)
    return resp.json()


def netcdf_to_png(
    nc_file: str, output_dir: str, bounding_box: BBox, night_IR=False
) -> Path:
    nc_file_path = Path(nc_file)
    output_dir_path = Path(output_dir)
    plt.figure(figsize=(8, 6))
    data_set = xr.open_dataset(nc_file_path)
    ax = plt.subplot(projection=data_set.rgb.crs)
    ax.imshow(
        data_set.rgb.NaturalColor(night_IR=night_IR), **data_set.rgb.imshow_kwargs
    )
    ax.set_extent(bounding_box.to_extent())
    png_file_path = output_dir_path / f"{nc_file_path.stem}.png"
    plt.savefig(png_file_path, format="png")
    plt.close()

    return png_file_path
