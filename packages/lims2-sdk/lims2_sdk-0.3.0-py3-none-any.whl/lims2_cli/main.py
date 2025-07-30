"""Lims2 命令行工具"""

import json
import sys
from pathlib import Path

import click

from lims2 import Lims2Client, __version__


def get_client(ctx):
    """获取或创建客户端实例"""
    if "client" not in ctx.obj:
        try:
            ctx.obj["client"] = Lims2Client()
        except Exception as e:
            click.echo(f"错误: {e}", err=True)
            sys.exit(1)
    return ctx.obj["client"]


@click.group()
@click.version_option(version=__version__, prog_name="lims2")
@click.pass_context
def cli(ctx):
    """Lims2 SDK 命令行工具

    使用前请设置环境变量：
    - LIMS2_API_URL: API 地址
    - LIMS2_API_TOKEN: API Token
    """
    # 延迟初始化客户端，让 help 命令正常工作
    ctx.ensure_object(dict)


@cli.group()
def chart():
    """图表相关命令"""
    pass


@chart.command("upload")
@click.argument("file_path", default="-")
@click.option("-p", "--project-id", required=True, help="项目 ID")
@click.option("-n", "--name", help="图表名称（默认使用文件名）")
@click.option("-s", "--sample-id", help="样本 ID")
@click.option("-t", "--chart-type", help="图表类型")
@click.option("-d", "--description", help="图表描述")
@click.option("-c", "--contrast", help="对比策略")
@click.option("-a", "--analysis-node", help="分析节点名称")
@click.option(
    "--precision",
    type=click.IntRange(0, 10),
    default=3,
    help="浮点数精度（小数位数，0-10，默认3）",
)
@click.pass_context
def chart_upload(
    ctx,
    file_path,
    project_id,
    name,
    sample_id,
    chart_type,
    description,
    contrast,
    analysis_node,
    precision,
):
    """上传图表文件

    Examples:
        # 上传 JSON 文件
        lims2 chart upload plot.json -p proj_001 -n "我的图表" -t heatmap

        # 指定分析节点
        lims2 chart upload plot.json -p proj_001 -n "我的图表" -a Expression_statistics

        # 使用精度控制
        lims2 chart upload plot.json -p proj_001 -n "我的图表" --precision 2

        # 管道输入（可选）
        echo '{"data": [...]}' | lims2 chart upload - -p proj_001 -n "管道图表"
    """
    client = get_client(ctx)
    try:
        if file_path == "-":
            # 从标准输入读取 JSON 数据
            if sys.stdin.isatty():
                click.echo("错误: 没有从管道接收到数据", err=True)
                sys.exit(1)

            data = json.load(sys.stdin)
            chart_name = name or "stdin_chart"
            result = client.chart.upload(
                data,
                project_id,
                chart_name,
                sample_id=sample_id,
                chart_type=chart_type,
                description=description,
                contrast=contrast,
                analysis_node=analysis_node,
                precision=precision,
            )
        else:
            # 从文件读取
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                click.echo(f"错误: 文件不存在: {file_path}", err=True)
                sys.exit(1)

            chart_name = name or file_path_obj.stem
            result = client.chart.upload(
                file_path,
                project_id,
                chart_name,
                sample_id=sample_id,
                chart_type=chart_type,
                description=description,
                contrast=contrast,
                analysis_node=analysis_node,
                precision=precision,
            )

        # 仿照原版的输出格式
        if result.get("code") == 200:
            click.echo("✓ 图表上传成功")
            if file_path != "-":
                click.echo(f"  文件名     : {Path(file_path).name}")
            click.echo(f"  图表名     : {chart_name}")
            click.echo(f"  chart_id   : {result['record']['chart_id']}")
            click.echo(f"  project_id : {project_id}")
            if sample_id:
                click.echo(f"  sample_id  : {sample_id}")
            if analysis_node:
                click.echo(f"  analysis_node: {analysis_node}")
        else:
            click.echo(f"上传结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

    except Exception as e:
        click.echo(f"✗ 上传失败: {e}", err=True)
        sys.exit(1)


@cli.group()
def storage():
    """存储相关命令"""
    pass


@storage.command("upload")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("-p", "--project-id", required=True, help="项目 ID")
@click.option("-a", "--analysis-node", required=True, help="分析节点名称")
@click.option("-c", "--file-category", required=True, help="文件分类")
@click.option("-s", "--sample-id", help="样本 ID")
@click.option("-k", "--key", help="自定义 OSS 键名")
@click.option("-d", "--description", help="文件描述")
@click.option("--progress", is_flag=True, help="显示上传进度")
@click.pass_context
def storage_upload(
    ctx,
    file_path,
    project_id,
    analysis_node,
    file_category,
    sample_id,
    key,
    description,
    progress,
):
    """上传文件到 OSS

    Examples:
        # 上传文件
        lims2 storage upload data.txt -p proj_001 -a analysis1 -c raw_data

        # 指定样本ID
        lims2 storage upload results.csv -p proj_001 -a qc -c results -s sample001
    """
    client = get_client(ctx)

    def progress_callback(consumed_bytes, total_bytes):
        if progress:
            percentage = (consumed_bytes / total_bytes) * 100
            click.echo(
                f"\r上传进度: {percentage:.1f}% ({consumed_bytes}/{total_bytes} 字节)",
                nl=False,
            )

    try:
        callback = progress_callback if progress else None
        result = client.storage.upload_file(
            file_path,
            project_id,
            analysis_node,
            file_category,
            key=key,
            sample_id=sample_id,
            description=description,
            progress_callback=callback,
        )

        if progress:
            click.echo()  # 换行

        click.echo("✓ 文件上传成功:")
        click.echo(f"  文件名     : {result['file_name']}")
        click.echo(f"  OSS 键     : {result['oss_key']}")
        click.echo(f"  文件大小   : {result.get('file_size_readable', 'N/A')}")
        click.echo(f"  文件 ID    : {result['file_id']}")
        if result.get("record_created"):
            click.echo("  记录状态   : 已创建")
        if result.get("error"):
            click.echo(f"  警告       : {result['error']}")

    except Exception as e:
        click.echo(f"✗ 上传失败: {e}", err=True)
        sys.exit(1)


@storage.command("upload-dir")
@click.argument(
    "dir_path", type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option("-p", "--project-id", required=True, help="项目 ID")
@click.option("-a", "--analysis-node", required=True, help="分析节点名称")
@click.option("-c", "--file-category", required=True, help="文件分类")
@click.option("-s", "--sample-id", help="样本 ID")
@click.option("--no-recursive", is_flag=True, help="不递归上传子目录")
@click.pass_context
def storage_upload_dir(
    ctx, dir_path, project_id, analysis_node, file_category, sample_id, no_recursive
):
    """上传目录到 OSS

    Examples:
        # 上传整个目录
        lims2 storage upload-dir ./data -p proj_001 -a preprocessing -c raw_data
    """
    client = get_client(ctx)

    try:
        results = client.storage.upload_directory(
            dir_path,
            project_id,
            analysis_node,
            file_category,
            sample_id=sample_id,
            recursive=not no_recursive,
        )

        success_count = sum(1 for r in results if not r.get("error"))
        total_count = len(results)

        click.echo(f"✓ 目录上传完成: {success_count}/{total_count} 文件成功")

        # 显示成功上传的文件
        for result in results:
            if not result.get("error"):
                file_name = result.get(
                    "file_name", Path(result.get("file_path", "Unknown")).name
                )
                click.echo(f"  ✓ {file_name}")

        # 显示失败的文件
        for result in results:
            if result.get("error"):
                file_path = result.get("file_path", "Unknown")
                file_name = (
                    Path(file_path).name if file_path != "Unknown" else "Unknown"
                )
                click.echo(f"  ✗ {file_name}: {result['error']}")

    except Exception as e:
        click.echo(f"✗ 目录上传失败: {e}", err=True)
        sys.exit(1)


@storage.command("info")
@click.argument("oss_key")
@click.option("-p", "--project-id", required=True, help="项目 ID")
@click.option("--json", "output_json", is_flag=True, help="输出 JSON 格式")
@click.pass_context
def storage_info(ctx, oss_key, project_id, output_json):
    """查看文件详细信息

    Examples:
        lims2 storage info biofile/proj_001/analysis1/file.txt -p proj_001
    """
    client = get_client(ctx)

    try:
        result = client.storage.get_file_info(oss_key, project_id)

        if output_json:
            click.echo(json.dumps(result, ensure_ascii=False, indent=2))
            return

        click.echo("✓ 文件信息:")
        click.echo(f"  文件名     : {result['file_name']}")
        click.echo(f"  OSS 键     : {result['oss_key']}")
        click.echo(f"  文件大小   : {result.get('file_size_readable', 'N/A')}")
        click.echo(f"  修改时间   : {result.get('last_modified', 'N/A')}")
        if result.get("content_type"):
            click.echo(f"  内容类型   : {result['content_type']}")
        if result.get("analysis_node"):
            click.echo(f"  分析节点   : {result['analysis_node']}")
        if result.get("sample_id"):
            click.echo(f"  样本 ID    : {result['sample_id']}")

    except Exception as e:
        click.echo(f"✗ 获取文件信息失败: {e}", err=True)
        sys.exit(1)


@storage.command("exists")
@click.argument("oss_key")
@click.option("-p", "--project-id", required=True, help="项目 ID")
@click.pass_context
def storage_exists(ctx, oss_key, project_id):
    """检查文件是否存在

    Examples:
        lims2 storage exists biofile/proj_001/analysis1/file.txt -p proj_001
    """
    client = get_client(ctx)

    try:
        exists = client.storage.file_exists(oss_key, project_id)

        if exists:
            click.echo(f"✓ 文件存在: {oss_key}")
        else:
            click.echo(f"✗ 文件不存在: {oss_key}")
            sys.exit(1)

    except Exception as e:
        click.echo(f"✗ 检查失败: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
