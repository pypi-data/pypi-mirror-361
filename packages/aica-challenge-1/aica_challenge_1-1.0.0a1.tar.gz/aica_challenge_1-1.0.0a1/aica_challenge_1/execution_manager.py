import functools
import io
import os

from concurrent.futures import ProcessPoolExecutor, Future
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from enum import Enum, auto
from random import choice
from sqlalchemy import create_engine, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass, Session, relationship
from typing import Dict, Any, Optional, List, Self

from cyst.api.environment.environment import Environment
from cyst.api.utils.counter import Counter

from aica_challenge_1.package_manager import PackageManager
from aica_challenge_1.scenario_manager import ScenarioManager, ScenarioVariant


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class RunSpecification(Base):
    __tablename__ = "challenge_run_specification"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(init=True, default="")
    description: Mapped[str] = mapped_column(init=True, default="")
    agent_name: Mapped[str] = mapped_column(init=True, default="")
    scenario: Mapped[str] = mapped_column(init=True, default="Random")
    variant: Mapped[int] = mapped_column(init=True, default=-1)
    max_time: Mapped[int] = mapped_column(init=True, default=100)
    max_actions: Mapped[int] = mapped_column(init=True, default=100)
    max_episodes: Mapped[int] = mapped_column(init=True, default=100)
    max_parallel: Mapped[int] = mapped_column(init=True, default=1)

    @staticmethod
    def copy(other: 'RunSpecification'):
        return RunSpecification(other.name + "_copy", other.description, other.agent_name, other.scenario, other.variant,
                                other.max_time, other.max_episodes, other.max_parallel)


class DBRun(Base):
    __tablename__ = "challenge_run_statistics"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    status: Mapped[str] = mapped_column(init=True)
    details: Mapped[str] = mapped_column(init=True)
    episodes: Mapped[List['DBEpisode']] = relationship(argument="DBEpisode",
                                                       back_populates="run",
                                                       cascade="all, delete")

    specification_id: Mapped[int] = mapped_column(ForeignKey("challenge_run_specification.id"), init=True)
    specification: Mapped[RunSpecification] = relationship()


class DBEpisode(Base):
    __tablename__ = "challenge_episode_statistics"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    stdout: Mapped[str] = mapped_column(init=True)
    stderr: Mapped[str] = mapped_column(init=True)
    cyst_run_id: Mapped[str] = mapped_column(init=True)
    status: Mapped[str] = mapped_column(init=True)

    run_id: Mapped[int] = mapped_column(ForeignKey("challenge_run_statistics.id"), init=True)
    run: Mapped[DBRun] = relationship(back_populates="episodes")


class RunStatus(Enum):
    INIT = auto()
    RUNNING = auto()
    FINISHED = auto()
    ERROR = auto()


@dataclass
class Episode:
    cyst_run_id: str
    stdout: str
    stderr: str
    run: int = -1
    status: RunStatus = RunStatus.RUNNING


@dataclass
class Run:
    specification: RunSpecification
    executor: Optional[ProcessPoolExecutor] = None
    status: RunStatus = RunStatus.INIT
    detail: str = ""
    # Replace with sets?
    running: Dict[int, Future] = field(default_factory=dict)
    successful: Dict[int, Future] = field(default_factory=dict)
    failed: Dict[int, Future] = field(default_factory=dict)
    error: Dict[int, Future] = field(default_factory=dict)
    episodes: Dict[int, Episode] = field(default_factory=dict)
    id: int = field(default=-1)

def launch_simulation(run_id: int, scenario: ScenarioVariant, agent: str, max_time: float, max_actions: int,
                      agent_configuration: Dict[str, str] | None = None) -> Episode:
    parameters: Dict[str, Any] = { "agent-name": agent }
    if agent_configuration:
        parameters["agent_configuration"] = agent_configuration

    os.environ["CYST_MAX_RUNNING_TIME"] = str(max_time)
    os.environ["CYST_MAX_ACTION_COUNT"] = str(max_actions)
    os.environ["CYST_DATA_BACKEND"] = "sqlite"
    os.environ["CYST_DATA_BACKEND_PARAMS"] = "path,aica_challenge.db"
    os.environ["CYST_RUN_ID_LOG_SUFFIX"] = "1"

    db = create_engine("sqlite+pysqlite:///aica_challenge.db")

    with redirect_stdout(io.StringIO()) as stdout:
        with redirect_stderr(io.StringIO()) as stderr:

            env = Environment.create()
            try:
                env.configure(*scenario.config, parameters=parameters)
            except RuntimeError as e:
                print(f"Could not configure a simulation. Reason: {str(e)}")

            env.control.init()

            episode_id = -1

            with Session(db) as session:
                stmt = select(DBRun).where(DBRun.id == run_id)
                run: DBRun = session.scalars(stmt).one()

                db_episode = DBEpisode(
                        stdout="",
                        stderr="",
                        cyst_run_id=env.infrastructure.statistics.run_id,
                        status=str(RunStatus.RUNNING),
                        run_id=run_id,
                        run=run
                    )

                session.add(db_episode)
                run.episodes.append(db_episode)

                session.add(run)
                session.flush()

                episode_id = db_episode.id

                session.commit()

            env.control.run()
            env.control.commit()

            episode = Episode(
                cyst_run_id=env.infrastructure.statistics.run_id,
                stdout=stdout.getvalue(),
                stderr=stderr.getvalue(),
                run=run_id,
                status=RunStatus.FINISHED # TODO extract error
            )

            with Session(db) as session:
                stmt = select(DBEpisode).where(DBEpisode.id == episode_id)
                db_episode: DBEpisode = session.scalars(stmt).one()

                db_episode.stdout = episode.stdout
                db_episode.stderr = episode.stderr
                db_episode.status = str(RunStatus.FINISHED)

                session.commit()

    return episode


class ExecutionManager:
    def __init__(self, package_manager: PackageManager, scenario_manager: ScenarioManager):
        self._package_manager = package_manager
        self._scenario_manager = scenario_manager
        self._run_specifications: Dict[str, RunSpecification] = {}

        self._db = create_engine("sqlite+pysqlite:///aica_challenge.db")
        Base.metadata.create_all(self._db)

        with Session(self._db, expire_on_commit=False) as session:
            for obj in session.execute(select(RunSpecification)).scalars():
                self._run_specifications[obj.name] = obj

        self._runs: Dict[int, Run] = {}

    def list_run_specifications(self) -> List[str]:
        return sorted(self._run_specifications.keys())

    def get_run_specification(self, name: str) -> Optional[RunSpecification]:
        return self._run_specifications.get(name, None)

    def set_run_specification(self, specification: RunSpecification, old_specification: Optional[RunSpecification] = None) -> None:
        if old_specification and old_specification.name and old_specification.name != specification.name:
            del self._run_specifications[str(old_specification.name)]
        self._run_specifications[specification.name] = specification
        with Session(self._db, expire_on_commit=False) as session:
            session.add(specification)
            session.commit()

    def execution_callback(self, episode: int, future: Future):
        e: Episode = future.result()
        self._runs[e.run].episodes[episode] = e

    def execute(self, specification: RunSpecification | str) -> None:
        with Session(self._db, expire_on_commit=False) as session:
            # Refresh run specification
            specification = session.get(RunSpecification, specification.id)

            if isinstance(specification, str):
                specification = self._run_specifications.get(specification, None)
                if not specification:
                    raise ValueError(f"Run with the name '{specification}' not available in the system.")
            run = Run(specification)

            db_run = DBRun(
                status=str(RunStatus.INIT),
                details="",
                episodes=[],
                specification_id=specification.id,
                specification=specification
            )

            session.add(db_run)
            session.flush()

            if not specification.name:
                run.status = RunStatus.ERROR
                run.detail = "Run specification must have a name."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            if specification.agent_name not in self._package_manager.list_installed_agents():
                run.status = RunStatus.ERROR
                run.detail = f"Chosen agent '{specification.agent_name}' not installed in the system."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            scenario_name = specification.scenario
            scenario = self._scenario_manager.get_scenario(scenario_name)

            if scenario_name == "Random":
                scenarios = self._scenario_manager.get_scenarios()
                if not scenarios:
                    run.status = RunStatus.ERROR
                    run.detail = "No scenarios installed in the system. Cannot choose a random one."
                    db_run.status = str(RunStatus.ERROR)
                    db_run.details = run.detail
                    session.commit()
                    return
                s = choice(scenarios)
                scenario_name = s.short_path
                scenario = s

            if not scenario:
                run.status = RunStatus.ERROR
                run.detail = f"Chosen scenario '{specification.scenario}' not available."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            variant_id = specification.variant
            variants = scenario.variants

            if variant_id == -1:
                if not variants:
                    run.status = RunStatus.ERROR
                    run.detail = f"No variants of the scenario '{scenario_name}' exist. Cannot choose a random one."
                    db_run.status = str(RunStatus.ERROR)
                    db_run.details = run.detail
                    session.commit()
                    return
                variant_id = choice(list(variants.keys()))

            elif variant_id not in variants:
                run.status = RunStatus.ERROR
                run.detail = f"Variant '{variant_id}' of the scenario '{scenario_name}' is not available in the system."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            scenario_variant = self._scenario_manager.get_scenario(scenario_name).variants[variant_id]

            run.id = db_run.id
            self._runs[run.id] = run

            run.status = RunStatus.RUNNING
            db_run.status = str(RunStatus.RUNNING)

            session.commit()

        run.executor = ProcessPoolExecutor(max_workers=specification.max_parallel)

        for e in range(specification.max_episodes):
            future: Future = run.executor.submit(launch_simulation, run.id, scenario_variant,
                                                 specification.agent_name, specification.max_time,
                                                 specification.max_actions, {})
            future.add_done_callback(functools.partial(self.execution_callback, e))
            run.running[e] = future
