import ffmpeg


def add_watermark(input_path: str, output_path: str, text: str = "aivid.ch | Free Plan") -> None:
    """Burn a text watermark into the bottom-right corner."""
    (
        ffmpeg
        .input(input_path)
        .drawtext(
            text=text,
            fontsize=28,
            fontcolor="white@0.7",
            x="w-tw-20",
            y="h-th-20",
            shadowcolor="black@0.5",
            shadowx=2,
            shadowy=2,
        )
        .output(output_path, vcodec="libx264", pix_fmt="yuv420p", acodec="copy")
        .overwrite_output()
        .run(quiet=True)
    )
