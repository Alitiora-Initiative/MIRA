"""
Sub-Agent Horizontal Genesis System - Triggers capital-splitting and sub-agent provisioning.
"""

import asyncio
import os
import re
from typing import Dict, Any, List, Optional
from loguru import logger
from dataclasses import dataclass

ALLOWED_IMAGES = frozenset({"alpine", "python:3.11-alpine", "python:3.12-alpine"})
AGENT_ID_RE = re.compile(r"^subagent-[0-9]{1,4}$")


@dataclass
class Subagent:
    """Sub-agent configuration."""
    agent_id: str
    strategy: str
    asset: str
    funding_usd: float
    container_id: Optional[str] = None
    status: str = "stopped"


class SubagentGenesis:
    """Sub-agent horizontal genesis system."""

    def __init__(self, config):
        self.config = config
        self.scaling_config = config.scaling
        self.subagent_config = config.subagent
        self.subagents: Dict[str, Subagent] = {}
        self.docker_client = None
        logger.info("Sub-Agent Genesis System initialized")

    async def initialize_docker(self):
        """Initialize Docker client. Refuses unless explicitly enabled."""
        if os.environ.get("MIRA_ENABLE_SUBAGENTS") != "1":
            logger.info("Sub-agent containers stay off (set MIRA_ENABLE_SUBAGENTS=1 to allow)")
            return
        image = str(self.subagent_config.base_image)
        if image not in ALLOWED_IMAGES:
            logger.error(f"Refusing sub-agent image outside the allowlist: {image}")
            return
        try:
            import docker

            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.error(f"Error initializing Docker: {e}")

    async def check_genesis_trigger(self, profit_usd: float) -> bool:
        """
        Check if sub-agent genesis milestone is reached.

        Args:
            profit_usd: Net accumulated profit in USD

        Returns:
            True if genesis triggered, False otherwise
        """
        threshold = self.scaling_config.subagent_genesis_profit_usd

        if profit_usd >= threshold:
            logger.info(f"Sub-agent genesis triggered at ${profit_usd:.2f} profit")
            return True

        return False

    async def trigger_genesis(self, total_capital_usd: float) -> List[Subagent]:
        """
        Trigger sub-agent genesis: reserve capital and provision sub-agents.

        Args:
            total_capital_usd: Total capital in USD

        Returns:
            List of created sub-agents
        """
        try:
            # Reserve $10.00 USD in core pool
            core_pool_reserve = 10.0
            remaining_capital = total_capital_usd - core_pool_reserve

            if remaining_capital < self.scaling_config.subagent_count * self.scaling_config.subagent_funding_usd:
                logger.warning("Insufficient capital for sub-agent genesis")
                return []

            logger.info(f"Reserving ${core_pool_reserve:.2f} in core pool")
            logger.info(f"Provisioning {self.scaling_config.subagent_count} sub-agents")

            # Provision sub-agents
            created_subagents = []
            for i in range(self.scaling_config.subagent_count):
                agent_id = f"subagent-{i+1}"
                subagent = Subagent(
                    agent_id=agent_id,
                    strategy="probability",
                    asset="SOL",
                    funding_usd=self.scaling_config.subagent_funding_usd
                )

                # Create Docker container
                container_id = await self._create_subagent_container(subagent)
                if container_id:
                    subagent.container_id = container_id
                    subagent.status = "running"
                    self.subagents[agent_id] = subagent
                    created_subagents.append(subagent)

            logger.info(f"Genesis complete: {len(created_subagents)} sub-agents provisioned")
            return created_subagents

        except Exception as e:
            logger.error(f"Error in sub-agent genesis: {e}")
            return []

    async def _create_subagent_container(self, subagent: Subagent) -> Optional[str]:
        """
        Create isolated Docker container for sub-agent.

        Args:
            subagent: Subagent configuration

        Returns:
            Container ID or None
        """
        try:
            if os.environ.get("MIRA_ENABLE_SUBAGENTS") != "1":
                logger.error("Refusing to create a container: sub-agents are disabled")
                return None
            if not AGENT_ID_RE.match(subagent.agent_id):
                logger.error(f"Refusing unsafe sub-agent id: {subagent.agent_id}")
                return None
            image = str(self.subagent_config.base_image)
            if image not in ALLOWED_IMAGES:
                logger.error(f"Refusing sub-agent image outside the allowlist: {image}")
                return None
            if not isinstance(subagent.funding_usd, (int, float)) or subagent.funding_usd < 0:
                logger.error("Refusing non-numeric sub-agent funding")
                return None
            if not self.docker_client:
                await self.initialize_docker()
            if not self.docker_client:
                return None

            container = self.docker_client.containers.run(
                image=image,
                command=[
                    "python",
                    "-m",
                    "subagent.main",
                    f"--agent-id={subagent.agent_id}",
                    f"--funding={subagent.funding_usd}",
                ],
                mem_limit=f"{int(self.subagent_config.memory_limit_mb)}m",
                cpu_quota=int(self.subagent_config.cpu_limit * 100000),
                detach=True,
                name=subagent.agent_id,
                network_disabled=True,
            )

            logger.info(f"Container created: {container.id}")
            return container.id

        except Exception as e:
            logger.error(f"Error creating container for {subagent.agent_id}: {e}")
            return None

    async def stop_subagent(self, agent_id: str) -> bool:
        """
        Stop a sub-agent container.

        Args:
            agent_id: Sub-agent identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            subagent = self.subagents.get(agent_id)
            if not subagent or not subagent.container_id:
                return False

            container = self.docker_client.containers.get(subagent.container_id)
            container.stop()
            container.remove()

            subagent.status = "stopped"
            subagent.container_id = None

            logger.info(f"Sub-agent {agent_id} stopped")
            return True

        except Exception as e:
            logger.error(f"Error stopping sub-agent {agent_id}: {e}")
            return False

    async def get_subagent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a sub-agent.

        Args:
            agent_id: Sub-agent identifier

        Returns:
            Status dictionary or None
        """
        subagent = self.subagents.get(agent_id)
        if not subagent:
            return None

        return {
            "agent_id": subagent.agent_id,
            "strategy": subagent.strategy,
            "asset": subagent.asset,
            "funding_usd": subagent.funding_usd,
            "status": subagent.status,
            "container_id": subagent.container_id
        }

    async def get_all_subagents(self) -> List[Dict[str, Any]]:
        """
        Get status of all sub-agents.

        Returns:
            List of sub-agent status dictionaries
        """
        return [
            await self.get_subagent_status(agent_id)
            for agent_id in self.subagents.keys()
        ]
