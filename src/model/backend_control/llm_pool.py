# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from uuid import uuid4
from queue import Queue as TQueue
from multiprocessing import Process
from multiprocessing import Queue as MPQueue
from threading import Thread, Event
from typing import Optional, Any
from src.utility.gold.transformer_model_utility import spawn_language_model_instance
from src.utility.bronze import dictionary_utility


def run_llm(switch: Event, llm_configuraiton: dict, input_queue: TQueue, output_queue: TQueue) -> None:
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


class ThreadedLLMPool(object):
    """
    Controller class for handling LLM instances in separated threads for leightweight non-blocking I/O.
    """

    def __init__(self, queue_spawns: bool = False) -> None:
        """
        Initiation method.
        :param queue_spawns: Queue up instanciation until resources are available.
            Defaults to False.
        """
        # TODO: Add prioritization and potentially interrupt concept
        self.queue_spawns = queue_spawns
        self.threads = {}

    def stop_all(self) -> None:
        """
        Method for stopping threads.
        """
        for thread_uuid in self.threads:
            self.unload_llm(thread_uuid)

    def stop(self, target_thread: str) -> None:
        """
        Method for stopping a thread.
        :param target_thread: Thread to stop.
        """
        self.unload_llm(target_thread)

    def is_running(self, target_thread: str) -> bool:
        """
        Method for checking whether thread is running.
        :param target_thread: Thread to check.
        :return: True, if thread is running, else False.
        """
        return self.threads[target_thread]["running"]

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

    def reset_llm(self, target_thread: str, llm_configuration: dict) -> str:
        """
        Method for resetting LLM instance to a new config.
        :param target_thread: Thread of instance.
        :param llm_configuration: LLM configuration.
        :return: Thread UUID.
        """
        if not dictionary_utility.check_equality(self.threads[target_thread]["config"], llm_configuration):
            if self.threads[target_thread]["running"]:
                self.unload_llm(target_thread)
            self.threads[target_thread]["config"] = llm_configuration
        return target_thread

    def prepare_llm(self, llm_configuration: dict, given_uuid: str = None) -> str:
        """
        Method for preparing LLM instance.
        :param llm_configuration: LLM configuration.
        :param given_uuid: Given UUID to run thread under.
            Defaults to None in which case a new UUID is created.
        :return: Thread UUID.
        """
        uuid = uuid4() if given_uuid is None else given_uuid
        if uuid not in self.threads:
            self.threads[uuid] = {
                "input": TQueue(),
                "output": TQueue(),
                "config": llm_configuration,
                "running": False
            }
        else:
            self.reset_llm(uuid, llm_configuration)
        return uuid

    def load_llm(self, target_thread: str) -> None:
        """
        Method for loading LLM.
        :param target_thread: Thread to start.
        """
        self.threads[target_thread]["switch"] = Event()
        self.threads[target_thread]["input"] = TQueue()
        self.threads[target_thread]["output"] = TQueue()
        self.threads[target_thread]["thread"] = Thread(
            target=run_llm,
            args=(
                self.threads[target_thread]["switch"],
                self.threads[target_thread]["config"],
                self.threads[target_thread]["input"],
                self.threads[target_thread]["output"],
            )
        )
        self.threads[target_thread]["thread"].daemon = True
        self.threads[target_thread]["thread"].start()
        self.threads[target_thread]["running"] = True

    def unload_llm(self, target_thread: str) -> None:
        """
        Method for unloading LLM.
        :param target_thread: Thread to stop.
        """
        self.threads[target_thread]["switch"].set()
        self.threads[target_thread]["thread"].join(0)
        self.threads[target_thread]["running"] = False

    def generate(self, target_thread: str, prompt: str) -> Optional[Any]:
        """
        Request generation response for query from target LLM.
        :param target_thread: Target thread.
        :param prompt: Prompt to send.
        :return: Response.
        """
        self.threads[target_thread]["input"].put(prompt)
        return self.threads[target_thread]["output"].get()


class MulitprocessingLLMPool(object):
    """
    Controller class for handling LLM instances in separate processes for actual concurrency on heavy devices.
    """

    def __init__(self, queue_spawns: bool = False) -> None:
        """
        Initiation method.
        :param queue_spawns: Queue up instanciation until resources are available.
            Defaults to False.
        """
        # TODO: Add prioritization and potentially interrupt concept
        self.queue_spawns = queue_spawns
        self.threads = {}

    def stop_all(self) -> None:
        """
        Method for stopping threads.
        """
        for thread_uuid in self.threads:
            self.unload_llm(thread_uuid)

    def stop(self, target_thread: str) -> None:
        """
        Method for stopping a thread.
        :param target_thread: Thread to stop.
        """
        self.unload_llm(target_thread)

    def is_running(self, target_thread: str) -> bool:
        """
        Method for checking whether thread is running.
        :param target_thread: Thread to check.
        :return: True, if thread is running, else False.
        """
        return self.threads[target_thread]["running"]

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

    def reset_llm(self, target_thread: str, llm_configuration: dict) -> str:
        """
        Method for resetting LLM instance to a new config.
        :param target_thread: Thread of instance.
        :param llm_configuration: LLM configuration.
        :return: Thread UUID.
        """
        if not dictionary_utility.check_equality(self.threads[target_thread]["config"], llm_configuration):
            if self.threads[target_thread]["running"]:
                self.unload_llm(target_thread)
            self.threads[target_thread]["config"] = llm_configuration
        return target_thread

    def prepare_llm(self, llm_configuration: dict, given_uuid: str = None) -> str:
        """
        Method for preparing LLM instance.
        :param llm_configuration: LLM configuration.
        :param given_uuid: Given UUID to run thread under.
            Defaults to None in which case a new UUID is created.
        :return: Thread UUID.
        """
        uuid = uuid4() if given_uuid is None else given_uuid
        if uuid not in self.threads:
            self.threads[uuid] = {
                "input": TQueue(),
                "output": TQueue(),
                "config": llm_configuration,
                "running": False
            }
        else:
            self.reset_llm(uuid, llm_configuration)
        return uuid

    def load_llm(self, target_thread: str) -> None:
        """
        Method for loading LLM.
        :param target_thread: Thread to start.
        """
        self.threads[target_thread]["switch"] = Event()
        self.threads[target_thread]["input"] = TQueue()
        self.threads[target_thread]["output"] = TQueue()
        self.threads[target_thread]["thread"] = Thread(
            target=run_llm,
            args=(
                self.threads[target_thread]["switch"],
                self.threads[target_thread]["config"],
                self.threads[target_thread]["input"],
                self.threads[target_thread]["output"],
            )
        )
        self.threads[target_thread]["thread"].daemon = True
        self.threads[target_thread]["thread"].start()
        self.threads[target_thread]["running"] = True

    def unload_llm(self, target_thread: str) -> None:
        """
        Method for unloading LLM.
        :param target_thread: Thread to stop.
        """
        self.threads[target_thread]["switch"].set()
        self.threads[target_thread]["thread"].join(0)
        self.threads[target_thread]["running"] = False

    def generate(self, target_thread: str, prompt: str) -> Optional[Any]:
        """
        Request generation response for query from target LLM.
        :param target_thread: Target thread.
        :param prompt: Prompt to send.
        :return: Response.
        """
        self.threads[target_thread]["input"].put(prompt)
        return self.threads[target_thread]["output"].get()
