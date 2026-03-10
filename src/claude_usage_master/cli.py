from pathlib import Path

import typer

from . import __version__
from .dimension_scorer import score_dimensions
from .explain_service import assemble_result
from .fusion_service import fuse_sources
from .hooks_tracker import calc_hooks_stability
from .local_store import append_history, write_json
from .local_web import create_server
from .log_ingestor import ingest_incremental
from .questionnaire_adapter import load_questionnaire
from .rating_engine import evaluate
from .report_builder import write_report

app = typer.Typer(help="Claude usage proficiency self-rating tool")


@app.command("version")
def version() -> None:
    typer.echo(__version__)


@app.command("run")
def run_rating(
    input_path: Path = typer.Option(..., "--input", exists=True, readable=True, help="questionnaire JSON file"),
    logs_dir: Path = typer.Option(Path("data/logs"), "--logs", help="local log directory"),
    output_path: Path = typer.Option(Path("data/rating_result.json"), "--output", help="rating result JSON"),
    history_path: Path = typer.Option(Path("data/ratings_history.json"), "--history", help="rating history JSON"),
    report_path: Path = typer.Option(Path("reports/index.html"), "--report", help="local HTML report"),
    checkpoint_path: Path = typer.Option(Path("data/log_checkpoint.json"), "--checkpoint", help="log checkpoint JSON"),
) -> None:
    questionnaire = load_questionnaire(input_path)
    dim_scores = score_dimensions(questionnaire)
    result = evaluate(dim_scores)

    log_meta = ingest_incremental(logs_dir, checkpoint_path)
    hooks_stability = calc_hooks_stability(
        sample_size=int(log_meta["sample_size"]),
        coverage_days=int(log_meta["coverage_days"]),
    )

    result = fuse_sources(
        result=result,
        questionnaire_d3=dim_scores["D3"],
        sample_size=int(log_meta["sample_size"]),
        coverage_days=int(log_meta["coverage_days"]),
        hooks_stability=hooks_stability,
    )
    result = assemble_result(result)

    payload = result.model_dump()
    write_json(output_path, payload)
    append_history(history_path, payload)
    write_report(report_path, result)

    typer.echo(f"rating: {result.rating} ({result.final_score})")
    typer.echo(f"result: {output_path}")
    typer.echo(f"report: {report_path}")


@app.command("serve")
def serve_questionnaire(
    host: str = typer.Option("127.0.0.1", "--host", help="bind host"),
    port: int = typer.Option(8765, "--port", min=1, max=65535, help="bind port"),
    questionnaire_path: Path = typer.Option(
        Path("data/questionnaire.json"), "--questionnaire", help="questionnaire JSON output"
    ),
    page_path: Path = typer.Option(Path("reports/questionnaire.html"), "--page", help="questionnaire HTML page"),
) -> None:
    server = create_server(
        host=host,
        port=port,
        questionnaire_path=questionnaire_path,
        page_path=page_path,
    )
    addr, actual_port = server.server_address
    typer.echo(f"questionnaire service: http://{addr}:{actual_port}/")
    typer.echo(f"write target: {questionnaire_path}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        typer.echo("service stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    app()
