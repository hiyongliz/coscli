import os
import sys
from datetime import datetime

import typer
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError

# logging.basicConfig(level=logging.INFO, stream=sys.stdout)
__VERSION__ = "0.1.1"


app = typer.Typer(
    short_help="Command line tool for managing Tencent Cloud COS",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode="rich",
    add_completion=False,
    rich_help_panel="coscli",
    help="Command line tool for managing Tencent Cloud COS (Cloud Object Storage)",
)


def version_callback(value: bool):
    if value:
        print(__VERSION__)
        raise typer.Exit()


def percentage(consumed_bytes, total_bytes):
    """进度条回调函数，计算当前上传的百分比

    :param consumed_bytes: 已经上传/下载的数据量
    :param total_bytes: 总数据量
    """
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        print("\r{0}% ".format(rate))
        sys.stdout.flush()


def create_client():
    """创建COS客户端"""
    secret_id = os.getenv("SECRET_ID")
    secret_key = os.getenv("SECRET_KEY")
    region = os.getenv("REGION", "wuxi")  # Default region if not set
    token = None
    domain = os.getenv("DOMAIN")

    if not secret_id or not secret_key:
        print("Please set SECRET_ID and SECRET_KEY environment variables.")
        sys.exit(1)

    config = CosConfig(
        Region=region,
        SecretId=secret_id,
        SecretKey=secret_key,
        Token=token,
        Domain=domain,
    )

    return CosS3Client(config)


def size_formater(size: str) -> str:
    """格式化文件大小"""
    size_int = int(size)
    if size_int < 1024:
        return f"{size_int}B"
    elif size_int < 1024**2:
        return f"{size_int / 1024:.2f}KB"
    elif size_int < 1024**3:
        return f"{size_int / (1024**2):.2f}MB"
    else:
        return f"{size_int / (1024**3):.2f}GB"


@app.command()
def upload(file: str, obj_name: str = ""):
    """Upload a file to the bucket."""
    if obj_name == "":
        obj_name = file.split("/")[-1]
    print(f"Uploading {file} to {obj_name}")

    client = create_client()

    start_time = datetime.now()
    response = client.upload_file(
        Bucket="",
        LocalFilePath=file,
        Key=obj_name,
        PartSize=10,
        MAXThread=10,
        progress_callback=percentage,
    )
    print(f"Upload completed in {datetime.now() - start_time}s\n{response}")


@app.command()
def get(obj_name: str, filepath: str = ""):
    """Download an object from the bucket."""
    if filepath == "":
        filepath = obj_name.split("/")[-1]
    print(f"Downloading {obj_name} to {filepath}")

    client = create_client()

    start_time = datetime.now()
    for _ in range(0, 10):
        try:
            client.download_file(
                Bucket="",
                Key=obj_name,
                DestFilePath=filepath,
                progress_callback=percentage,
            )
            break
        except (CosClientError, CosServiceError) as e:
            print(e)
    print(f"Download completed in {datetime.now() - start_time}s")


@app.command()
def list():
    """List all objects in the bucket."""
    client = create_client()

    marker: str = ""
    contents = []
    while True:
        response = client.list_objects(
            Bucket="",
            Prefix="",
            Marker=marker,
            MaxKeys=100,
        )
        if "Contents" in response:
            contents.extend(response["Contents"])
            # print(f"total {len(response['Contents'])}")
            # for content in response["Contents"]:
            #     print(
            #         f"{content['LastModified']} {size_formater(content['Size']):>10} {content['Key']}"
            #     )
        if response["IsTruncated"] == "false":
            break
        marker = response["NextMarker"]

    print(f"total {len(contents)}")
    for content in contents:
        print(
            f"{content['LastModified']} {size_formater(content['Size']):>10} {content['Key']}"
        )


# @app.command()
# def delete(obj_name: str):
#     """Delete an object from the bucket."""
#     client = create_client()

#     response = client.delete_object(
#         Bucket="",
#         Key=obj_name,
#     )
#     print(response)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
):
    """Command line tool for managing Tencent Cloud COS (Cloud Object Storage)"""
    pass


if __name__ == "__main__":
    app()
