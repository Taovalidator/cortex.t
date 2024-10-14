from typing import Union, AsyncGenerator, Any

import bittensor as bt
from bittensor import dendrite
import traceback
import time

from cortext import StreamPrompting


class CortexDendrite(dendrite):
    async def call_stream(
            self,
            target_axon: Union[bt.AxonInfo, bt.axon],
            synapse: bt.StreamingSynapse = bt.Synapse(),  # type: ignore
            timeout: float = 12.0,
            deserialize: bool = True,
    ) -> AsyncGenerator[Any, Any]:
        start_time = time.time()
        target_axon = (
            target_axon.info()
            if isinstance(target_axon, bt.axon)
            else target_axon
        )

        # Build request endpoint from the synapse class
        request_name = synapse.__class__.__name__
        endpoint = (
            f"0.0.0.0:{str(target_axon.port)}"
            if target_axon.ip == str(self.external_ip)
            else f"{target_axon.ip}:{str(target_axon.port)}"
        )
        url = f"http://{endpoint}/{request_name}"

        # Preprocess synapse for making a request
        synapse: StreamPrompting = self.preprocess_synapse_for_request(target_axon, synapse, timeout)  # type: ignore
        try:
            async with (await self.session).post(
                    url,
                    headers=synapse.to_headers(),
                    json=synapse.dict(),
                    timeout=timeout,
            ) as response:
                # Use synapse subclass' process_streaming_response method to yield the response chunks
                try:
                    async for chunk in synapse.process_streaming_response(response):  # type: ignore
                        yield chunk  # Yield each chunk as it's processed
                except Exception as err:
                    bt.logging.error(f"{err} issue from miner {synapse.uid} {synapse.provider} {synapse.model}")
                finally:
                    yield ""

            # Set process time and log the response
            synapse.dendrite.process_time = str(time.time() - start_time)  # type: ignore

        except Exception as e:
            bt.logging.error(f"{e} {traceback.format_exc()}")
