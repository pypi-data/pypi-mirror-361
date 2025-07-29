import asyncio
import time
from threading import Thread
from collections import deque
from typing import Optional

from analytics_ingest.internal.schemas.ingest_config_schema import IngestConfigSchema
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.configuration import ConfigurationService
from analytics_ingest.internal.utils.dtc import create_dtc
from analytics_ingest.internal.utils.gps import create_gps
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.message import create_message
from analytics_ingest.internal.utils.network import create_network
from analytics_ingest.internal.utils.signal import create_signal


class AnalyticsIngestClient:
    def __init__(self, **kwargs):
        # Initializes the client with config, GraphQL executor, and configuration ID.
        # Also sets up signal buffering, semaphore, event loop, and background auto-push task.
        self.config = IngestConfigSchema(**kwargs)
        self.executor = GraphQLExecutor(
            self.config.graphql_endpoint, self.config.jwt_token
        )

        self.configuration_id = ConfigurationService(self.executor).create(
            self.config.model_dump()
        )["data"]["createConfiguration"]["id"]

        self.signal_buffer = deque()  # stores buffered signal inputs
        self.signal_semaphore = asyncio.Semaphore(1)  # ensures one request at a time
        self.last_push_time = time.time()  # tracks last flush time
        self.loop = asyncio.new_event_loop()  # separate event loop for async flush
        self._shutdown = False  # shutdown flag for background thread

        Thread(
            target=self._start_loop, daemon=True
        ).start()  # launches auto-push thread

    def _start_loop(self):
        # Starts the asyncio loop in a background thread
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._auto_push_loop())

    async def _auto_push_loop(self):
        # Runs in background, checks every second whether flush conditions are met:
        # batch size threshold or time threshold
        while not self._shutdown:
            await asyncio.sleep(1)
            now = time.time()
            if (
                len(self.signal_buffer) >= self.config.batch_size
                or now - self.last_push_time >= self.config.batch_interval_seconds
            ):
                await self._flush_buffer()

    def add_signal(self, variables: Optional[dict] = None):
        # Adds a signal to the buffer for future batched ingestion
        if not variables:
            raise ValueError("Missing 'variables' dictionary")

        self.signal_buffer.append(variables)

    async def _flush_buffer(self):
        # Flushes the current signal buffer by:
        # 1. Acquiring the semaphore (to serialize requests)
        # 2. Processing signals into messages and batched signal GraphQL calls
        # 3. Retrying failed batches by re-queuing
        if not self.signal_buffer:
            return
        async with self.signal_semaphore:
            buffer_copy = list(self.signal_buffer)
            self.signal_buffer.clear()

            try:
                for item in buffer_copy:
                    message_id = create_message(self.executor, item)
                    create_signal(
                        executor=self.executor,
                        config_id=self.configuration_id,
                        variables=item,
                        message_id=message_id,
                        batch_size=self.config.batch_size,
                    )
                self.last_push_time = time.time()
            except Exception as e:
                print(f"Flush failed, retrying next tick: {e}")
                self.signal_buffer.extendleft(
                    reversed(buffer_copy)
                )  # retry on next loop

    def add_dtc(self, variables: Optional[dict] = None):
        # Immediately sends a DTC event with associated message to GraphQL
        if not variables:
            raise ValueError("Missing 'variables' dictionary")

        try:
            message_id = create_message(self.executor, variables)
            create_dtc(
                executor=self.executor,
                config_id=self.configuration_id,
                variables=variables,
                message_id=message_id,
                batch_size=self.config.batch_size,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add DTC: {e}")

    def add_gps(self, variables: Optional[dict] = None):
        # Immediately sends a GPS update to GraphQL
        if not variables:
            raise ValueError("Missing 'variables' dictionary")

        try:
            create_gps(
                executor=self.executor,
                config_id=self.configuration_id,
                variables=variables,
                batch_size=self.config.batch_size,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add GPS: {e}")

    def add_network_stats(self, variables: Optional[dict] = None):
        # Immediately sends network stats update to GraphQL
        if not variables:
            raise ValueError("Missing 'variables' dictionary")

        try:
            create_network(
                executor=self.executor,
                config=self.config,
                variables=variables,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add network stats: {e}")

    def close(self):
        # Signals the background auto-push loop to shut down gracefully
        self._shutdown = True
        self.loop.call_soon_threadsafe(self.loop.stop)
