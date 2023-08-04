# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from typing import Optional, Any, Union
from abc import ABC, abstractmethod
from uuid import uuid4
from queue import Queue as TQueue
from multiprocessing import Process, Queue as MPQueue, Event as MPEvent
from threading import Thread, Event as TEvent
from src.utility.gold.transformer_model_utility import spawn_language_model_instance
from src.utility.bronze import dictionary_utility


def run_llm(switch: Union[TEvent, MPEvent], llm_configuraiton: dict, input_queue: Union[TQueue, MPQueue], output_queue: Union[TQueue, MPQueue]) -> None:
    """
    Function for running LLM instance.
    :param switch: Pool killswitch event.
    :param llm_configuration: Configuration to instantiate LLM.
    :param input_queue: Input queue.
    :param output_queue: Output queue.
    """
    llm = spawn_language_model_instance(llm_configuraiton)
    while not switch.wait(0.5):
        output_queue.put(llm.generate(input_queue.get()))


class LLMPool(ABC):
    """
    Class for handling a pool of LLM instances.
    """

    def __init__(self, queue_spawns: bool = False) -> None:
        """
        Initiation method.
        :param queue_spawns: Queue up instanciation until resources are available.
            Defaults to False.
        """
        # TODO: Add prioritization and potentially interrupt concept
        self.queue_spawns = queue_spawns
        self.workers = {}

    def stop_all(self) -> None:
        """
        Method for stopping workers.
        """
        for worker_uuid in self.workers:
            self.unload_llm(worker_uuid)
            self.workers[worker_uuid]["running"] = False

    def stop(self, target_worker: str) -> None:
        """
        Method for stopping a worker.
        :param target_worker: Worker to stop.
        """
        self.unload_llm(target_worker)
        self.workers[target_worker]["running"] = False

    def start(self, target_worker: str) -> None:
        """
        Method for stopping a worker.
        :param target_worker: Worker to stop.
        """
        self.unload_llm(target_worker)
        self.workers[target_worker]["running"] = False

    def is_running(self, target_worker: str) -> bool:
        """
        Method for checking whether worker is running.
        :param target_worker: Worker to check.
        :return: True, if worker is running, else False.
        """
        return self.workers[target_worker]["running"]

    def validate_resources(self, llm_configuration: dict, queue_spawns: bool) -> bool:
        """
        Method for validating resources before LLM instantiation.
        :param llm_configuration: LLM configuration.
        :param queue_spawns: Queue up instanciation until resources are available.
            Defaults to False.
        :return: True, if resources are available, else False.
        """
        # TODO: Implement
        pass

    def reset_llm(self, target_worker: str, llm_configuration: dict) -> str:
        """
        Method for resetting LLM instance to a new config.
        :param target_worker: Worker of instance.
        :param llm_configuration: LLM configuration.
        :return: Worker UUID.
        """
        if not dictionary_utility.check_equality(self.workers[target_worker]["config"], llm_configuration):
            if self.workers[target_worker]["running"]:
                self.unload_llm(target_worker)
            self.workers[target_worker]["config"] = llm_configuration
        return target_worker

    def prepare_llm(self, llm_configuration: dict, given_uuid: str = None) -> str:
        """
        Method for preparing LLM instance.
        :param llm_configuration: LLM configuration.
        :param given_uuid: Given UUID to run worker under.
            Defaults to None in which case a new UUID is created.
        :return: Worker UUID.
        """
        uuid = uuid4() if given_uuid is None else given_uuid
        if uuid not in self.workers:
            self.workers[uuid] = {
                "config": llm_configuration,
                "running": False
            }
        else:
            self.reset_llm(uuid, llm_configuration)
        return uuid

    @abstractmethod
    def load_llm(self, target_worker: str) -> None:
        """
        Method for loading LLM.
        :param target_worker: Worker to start.
        """
        pass

    @abstractmethod
    def unload_llm(self, target_worker: str) -> None:
        """
        Method for unloading LLM.
        :param target_worker: Worker to stop.
        """
        pass

    @abstractmethod
    def generate(self, target_worker: str, prompt: str) -> Optional[Any]:
        """
        Request generation response for query from target LLM.
        :param target_worker: Target worker.
        :param prompt: Prompt to send.
        :return: Response.
        """
        pass


class ThreadedLLMPool(LLMPool):
    """
    Class for handling a pool of LLM instances in separated threads for leightweight non-blocking I/O.
    """

    def load_llm(self, target_worker: str) -> None:
        """
        Method for loading LLM.
        :param target_worker: Worker to start.
        """
        self.workers[target_worker]["switch"] = TEvent()
        self.workers[target_worker]["input"] = TQueue()
        self.workers[target_worker]["output"] = TQueue()
        self.workers[target_worker]["worker"] = (
            target=run_llm,
            args=(
                self.workers[target_worker]["switch"],
                self.workers[target_worker]["config"],
                self.workers[target_worker]["input"],
                self.workers[target_worker]["output"],
            )
        )
        self.workers[target_worker]["worker"].daemon = True
        self.workers[target_worker]["worker"].start()
        self.workers[target_worker]["running"] = True

    def unload_llm(self, target_worker: str) -> None:
        """
        Method for unloading LLM.
        :param target_worker: Worker to stop.
        """
        self.workers[target_worker]["switch"].set()
        self.workers[target_worker]["worker"].join(0)

    def generate(self, target_worker: str, prompt: str) -> Optional[Any]:
        """
        Request generation response for query from target LLM.
        :param target_worker: Target worker.
        :param prompt: Prompt to send.
        :return: Response.
        """
        self.workers[target_worker]["input"].put(prompt)
        return self.workers[target_worker]["output"].get()


class MulitprocessingLLMPool(LLMPool):
    """
    Class for handling a pool of LLM instances in separate processes for actual concurrency on heavy devices.
    """

    def load_llm(self, target_worker: str) -> None:
        """
        Method for loading LLM.
        :param target_worker: Worker to start.
        """
        self.workers[target_worker]["switch"] = MPQueue()
        self.workers[target_worker]["input"] = MPQueue()
        self.workers[target_worker]["output"] = MPQueue()
        self.workers[target_worker]["worker"] = Process(
            target=run_llm,
            args=(
                self.workers[target_worker]["switch"],
                self.workers[target_worker]["config"],
                self.workers[target_worker]["input"],
                self.workers[target_worker]["output"],
            )
        )
        self.workers[target_worker]["worker"].start()
        self.workers[target_worker]["running"] = True

    def unload_llm(self, target_worker: str) -> None:
        """
        Method for unloading LLM.
        :param target_worker: Worker to stop.
        """
        self.workers[target_worker]["switch"].set()
        self.workers[target_worker]["worker"].join(0)
        self.workers[target_worker]["running"] = False

    def generate(self, target_worker: str, prompt: str) -> Optional[Any]:
        """
        Request generation response for query from target LLM.
        :param target_worker: Target worker.
        :param prompt: Prompt to send.
        :return: Response.
        """
        self.workers[target_worker]["input"].put(prompt)
        return self.workers[target_worker]["output"].get()
