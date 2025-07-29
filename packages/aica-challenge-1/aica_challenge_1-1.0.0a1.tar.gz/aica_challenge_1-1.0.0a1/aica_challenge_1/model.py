import asyncio

from netaddr import IPNetwork
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass, Session, relationship
from typing import Tuple, Callable, Union, List, Coroutine, Optional

from cyst.api.environment.configuration import EnvironmentConfiguration
from cyst.api.environment.infrastructure import EnvironmentInfrastructure
from cyst.api.environment.message import Request, Response, Status, StatusOrigin, StatusValue, StatusDetail
from cyst.api.environment.messaging import EnvironmentMessaging
from cyst.api.environment.policy import EnvironmentPolicy
from cyst.api.environment.platform_specification import PlatformSpecification, PlatformType
from cyst.api.environment.resources import EnvironmentResources
from cyst.api.logic.action import ActionDescription, ActionParameterType, ActionParameter, Action, ActionType
from cyst.api.logic.behavioral_model import BehavioralModel, BehavioralModelDescription
from cyst.api.logic.composite_action import CompositeActionManager
from cyst.api.network.node import Node
from cyst.api.utils.duration import Duration, msecs


class AC1Model(BehavioralModel):
    def __init__(self, configuration: EnvironmentConfiguration, resources: EnvironmentResources,
                 policy: EnvironmentPolicy, messaging: EnvironmentMessaging, infrastructure: EnvironmentInfrastructure,
                 composite_action_manager: CompositeActionManager) -> None:

        self._configuration = configuration
        self._action_store = resources.action_store
        self._exploit_store = resources.exploit_store
        self._policy = policy
        self._messaging = messaging
        self._infrastructure = infrastructure
        self._cam = composite_action_manager

        self._action_store.add(ActionDescription(
            id="ac1:inspect",
            type=ActionType.DIRECT,
            platform=[PlatformSpecification(PlatformType.SIMULATED_TIME, "CYST"),
                      PlatformSpecification(PlatformType.REAL_TIME, "CYST")],
            description="Inspecting a machine, where you have an access to.",
            parameters=[])
        )

        self._action_store.add(ActionDescription(
            id="ac1:scan_host",
            type=ActionType.DIRECT,
            platform=[PlatformSpecification(PlatformType.SIMULATED_TIME, "CYST"),
                      PlatformSpecification(PlatformType.REAL_TIME, "CYST")],
            description="Scanning of one specific host",
            parameters=[])
        )

        self._action_store.add(ActionDescription(
            id="ac1:scan_network",
            type=ActionType.COMPOSITE,
            platform=[PlatformSpecification(PlatformType.SIMULATED_TIME, "CYST"),
                      PlatformSpecification(PlatformType.REAL_TIME, "CYST")],
            description="Scanning of a subnet",
            parameters=[ActionParameter(type=ActionParameterType.NONE, name="net",
                                        domain=configuration.action.create_action_parameter_domain_any())])
        )

    async def action_flow(self, message: Request) -> Tuple[Duration, Response]:
        if not message.action:
            raise ValueError("Action not provided")

        action_name = "_".join(message.action.fragments)
        fn: Callable[[Request], Coroutine[None, None, Tuple[Duration, Response]]] = getattr(self, "process_" + action_name, self.process_default_flow)
        duration, response = await fn(message)

        return duration, response

    async def action_effect(self, message: Request, node: Node) -> Tuple[Duration, Response]:
        if not message.action:
            raise ValueError("Action not provided")

        action_name = "_".join(message.action.fragments)
        fn: Callable[[Request, Node], Coroutine[None, None, Tuple[Duration, Response]]] = getattr(self, "process_" + action_name, self.process_default_effect)
        duration, response = await fn(message, node)

        return duration, response

    def action_components(self, message: Union[Request, Response]) -> List[Action]:
        return []

    async def process_default_effect(self, message: Request, node: Node) -> Tuple[Duration, Response]:
        error = f"A direct action with unknown semantics specified: {message.action.id}."
        return msecs(0), self._messaging.create_response(message, status=Status(StatusOrigin.SYSTEM, StatusValue.ERROR),
                                                         content=error, session=message.session)

    async def process_default_flow(self, message: Request) -> Tuple[Duration, Response]:
        error = f"A composite action with unknown semantics specified: {message.action.id}."
        return msecs(0), self._messaging.create_response(message, status=Status(StatusOrigin.SYSTEM, StatusValue.ERROR),
                                                         content=error, session=message.session)

    async def process_inspect(self, message: Request, node: Node) -> Tuple[Duration, Response]:

        if message.dst_ip != "127.0.0.1" and message.src_ip != message.dst_ip and \
                (message.session and message.session.end != message.dst_ip):

            error = f"The agent does not have an access to the following IP address {message.dst_ip}."
            return msecs(20), self._messaging.create_response(message,
                                                              status=Status(StatusOrigin.SERVICE, StatusValue.FAILURE),
                                                              content=error, session=message.session)

        services = []
        for service in node.services.values():
            if service.passive_service:
                services.append((service.name, str(service.passive_service.version)))

        result = {
            "ips": [str(x) for x in node.ips],
            "services": services
        }

        return msecs(20), self._messaging.create_response(message,
                                                          status=Status(StatusOrigin.SERVICE, StatusValue.SUCCESS),
                                                          content=result, session=message.session)


    async def process_scan_host(self, message: Request, node: Node) -> Tuple[Duration, Response]:
        host_ip = message.dst_ip
        services = []
        for service in node.services.values():
            if service.passive_service:
                services.append((service.name, str(service.passive_service.version)))

        result = {
            "ip": host_ip,
            "services": services
        }

        return msecs(40), self._messaging.create_response(message,
                                                          status=Status(StatusOrigin.SERVICE, StatusValue.SUCCESS),
                                                          session=message.session, auth=message.auth, content=result)

    async def process_scan_network(self, message: Request) -> Tuple[Duration, Response]:
        if "net" not in message.action.parameters or not message.action.parameters["net"].value:
            return msecs(0), self._messaging.create_response(message,
                                                             status=Status(StatusOrigin.SERVICE, StatusValue.FAILURE,
                                                                           StatusDetail.ACTION_PARAMETER_NOT_PROVIDED),
                                                             session=message.session, auth=message.auth)

        net = IPNetwork(message.action.parameters["net"].value)
        if not net:
            return msecs(0), self._messaging.create_response(message,
                                                             status=Status(StatusOrigin.SERVICE, StatusValue.FAILURE,
                                                                           StatusDetail.ACTION_PARAMETER_NOT_APPLICABLE),
                                                             session=message.session, auth=message.auth)

        tasks = []

        for ip in net.iter_hosts():
            action = self._action_store.get("ac1:scan_host")
            request = self._messaging.create_request(ip, "", action, original_request=message)
            tasks.append(self._cam.call_action(request, 0))

        results: List[Response] = await asyncio.gather(*tasks)
        successes = []
        failures = []
        errors = []
        for r in results:
            if r.status.value == StatusValue.SUCCESS:
                successes.append(r.content)
            elif r.status.value == StatusValue.FAILURE:
                failures.append(r.src_ip)
            elif r.status.value == StatusValue.ERROR:
                errors.append(r.src_ip)

        content = {
            "success": successes,
            "failure": failures,
            "error": errors
        }

        response = self._messaging.create_response(message,
                                                   status=Status(StatusOrigin.NETWORK, StatusValue.SUCCESS),
                                                   content=content, session=message.session, auth=message.auth)

        return msecs(0), response


def create_ac1_model(configuration: EnvironmentConfiguration, resources: EnvironmentResources,
                      policy: EnvironmentPolicy, messaging: EnvironmentMessaging,
                      infrastructure: EnvironmentInfrastructure,
                      composite_action_manager: CompositeActionManager) -> BehavioralModel:
    model = AC1Model(configuration, resources, policy, messaging, infrastructure, composite_action_manager)
    return model


behavioral_model_description = BehavioralModelDescription(
    namespace="ac1",
    description="Behavioral model for the first AICA challenge.",
    creation_fn=create_ac1_model,
    platform=[PlatformSpecification(PlatformType.SIMULATED_TIME, "CYST"), PlatformSpecification(PlatformType.REAL_TIME, "CYST")]
)
