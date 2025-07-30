from pycerberus.client import CerberusError
from pycerberus.models.common import Md5
import typer
from dataclasses import dataclass
from rich import print
from pycerberus import Cerberus
import functools
import json

app = typer.Typer(help="PyCerberus CLI - Interact with your Cerberus server")

@dataclass
class AppContext:
    cerberus: Cerberus
    json_output: bool

# Add global options for host and port
@app.callback()
def callback(
    ctx: typer.Context,
    host: str = typer.Option("localhost", help="Cerberus server host"),
    port: int = typer.Option(55222, help="Cerberus server port"),
    json_output: bool = typer.Option(False, help="Print Cerberus reponse as a valid JSON string"),
):
    """
    Connect to a Cerberus server instance.
    """
    cerberus= Cerberus(
        host=host,
        port=port
    )
    ctx.obj = AppContext(cerberus=cerberus, json_output=json_output)

def cerberus_command_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        context: AppContext = kwargs['ctx'].obj
        try:
            r = func(*args, **kwargs)
            if context.json_output:
                print(r.model_dump_json(indent=4))
            else:
                print(r)
        except CerberusError as e:
            if context.json_output:
                print(json.dumps(e.raw_error, indent=4))
            else:
                print(e.raw_error)
    return wrapper

@app.command()
@cerberus_command_wrapper
def version(
    ctx: typer.Context
):
    """Send a version Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.version()
    return r

@app.command()
@cerberus_command_wrapper
def usage(
    ctx: typer.Context
):
    """Send a usage Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.usage()
    return r

@app.command()
@cerberus_command_wrapper
def is_alive(
    ctx: typer.Context
):
    """Send an is_alive Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.is_alive()
    return r

@app.command()
@cerberus_command_wrapper
def naming(
    ctx: typer.Context,
    md5: str
):
    """Send a naming Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.naming(Md5(md5))
    return r

@app.command()
@cerberus_command_wrapper
def filter(
    ctx: typer.Context,
    file_hash: str,
    disable_naming: bool = typer.Option(False, help="Disable naming"),
):
    """Send a filter Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.filter(file_hash, disable_naming)
    return r

@app.command()
@cerberus_command_wrapper
def clamav(
    ctx: typer.Context,
    filepath: str
):
    """Send a clamav Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.clamav(filepath)
    return r

@app.command()
@cerberus_command_wrapper
def signature(
    ctx: typer.Context,
    filepath: str
):
    """Send a signature Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.signature(filepath)
    return r

@app.command()
@cerberus_command_wrapper
def magic(
    ctx: typer.Context,
    filepath: str
):
    """Send a magic Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.magic(filepath)
    return r

@app.command()
@cerberus_command_wrapper
def die(
    ctx: typer.Context,
    filepath: str,
    timeout: int = typer.Option(None),
):
    """Send a die Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.die(filepath, timeout)
    return r

@app.command()
@cerberus_command_wrapper
def gorille_static(
    ctx: typer.Context,
    filepath: str,
    type: str = typer.Option(None),
    dist_3d_mode: bool = typer.Option(None),
    timeout_dist: int = typer.Option(None),
    timeout_waiting_mdec: int = typer.Option(None),
    max_matches: int = typer.Option(None),
    best_match_name: bool = typer.Option(None),
):
    """Send a gorille_static Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.gorille_static(
        filepath,
        type,
        dist_3d_mode,
        timeout_dist,
        timeout_waiting_mdec,
        max_matches,
        best_match_name
    )
    return r

@app.command()
@cerberus_command_wrapper
def gorille_static_gcore(
    ctx: typer.Context,
    filepath: str,
    reduction: str = typer.Option(None),
    sites_size: int = typer.Option(None),
    detailed_dist: bool = typer.Option(None),
    max_matches: int = typer.Option(None),
    timeout: int = typer.Option(None),
):
    """Send a gorille_static_gcore Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.gorille_static_gcore(
        filepath,
        reduction,
        sites_size,
        detailed_dist,
        max_matches,
        timeout,
    )
    return r

@app.command()
@cerberus_command_wrapper
def gorille_dynamic_gcore(
    ctx: typer.Context,
    filepath: str,
    os: str  = typer.Option(None),
    timeout_tracing: int  = typer.Option(None),
    timeout_waiting_sandbox: int  = typer.Option(None),
    screenshots: bool  = typer.Option(None),
    tracing_artifacts_output_folderpath: str  = typer.Option(None),
    dist: bool  = typer.Option(None),
    reduction: str  = typer.Option(None),
    sites_size: int  = typer.Option(None),
    disable_naming: bool  = typer.Option(None),
    max_matches: int  = typer.Option(None),
    timeout: int  = typer.Option(None),
):
    """Send a gorille_dynamic_gcore Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.gorille_dynamic_gcore(
        filepath,
        os,
        timeout_tracing,
        timeout_waiting_sandbox,
        screenshots,
        tracing_artifacts_output_folderpath,
        dist,
        reduction,
        sites_size,
        disable_naming,
        max_matches,
        timeout,
    )
    return r

@app.command()
@cerberus_command_wrapper
def gorille_sites_gcore(
    ctx: typer.Context,
    filepath: str,
    reduction: str  = typer.Option(None),
    sites_size: int  = typer.Option(None),
    no_tag: bool  = typer.Option(None),
    timeout: int  = typer.Option(None),
):
    """Send a gorille_sites_gcore Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.gorille_sites_gcore(
        filepath,
        reduction,
        sites_size,
        no_tag,
        timeout,
    )
    return r

@app.command()
@cerberus_command_wrapper
def extract(
    ctx: typer.Context,
    filepath: str,
    extract_tool: str,
    output_folderpath: str,
    password: str = typer.Option(None),
    timeout: int = typer.Option(None),
):
    """Send an extract Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.extract(
        filepath,
        extract_tool,
        output_folderpath,
        password,
        timeout,
    )
    return r

@app.command()
@cerberus_command_wrapper
def strings(
    ctx: typer.Context,
    filepath: str,
    timeout: int = typer.Option(None),
    limit: int = typer.Option(None),
    regex: list[str] = typer.Option(None),
):
    """Send a strings Cerberus request."""
    context: AppContext = ctx.obj
    r = context.cerberus.strings(
        filepath,
        timeout,
        limit,
        regex,
    )
    return r




def main():
    app()

if __name__ == "__main__":
    main()

