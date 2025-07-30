import time
from loguru import logger
import typer
from evalsync.manager import ExperimentManager
from evalsync.worker import ExperimentWorker

app = typer.Typer()


@app.command()
def server(
    experiment_id: str = typer.Option(),
    num_workers: int = typer.Option(1),
    duration: int = typer.Option(10),
    verbose: bool = typer.Option(False),
):
    manager = ExperimentManager(experiment_id, num_workers, verbose)
    manager.wait_for_all_workers()
    logger.info("All workers are ready")
    manager.start_all()
    time.sleep(duration)
    manager.stop_all()
    manager.cleanup()


@app.command()
def client(
    experiment_id: str = typer.Option(),
    client_id: str = typer.Option(),
    verbose: bool = typer.Option(False),
):
    worker = ExperimentWorker(experiment_id, client_id, verbose)
    worker.ready()
    worker.wait_for_start()
    worker.wait_for_stop()
    worker.cleanup()


def main():
    app()


if __name__ == "__main__":
    app()
