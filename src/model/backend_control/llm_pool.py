# -*- coding: utf-8 -*-
"""
****************************************************
*          Basic Language Model Backend            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
from uuid import uuid4
from queue import Queue
from threading import Thread, Event
from typing import Optional, Any, List
from src.configuration import configuration as cfg
from src.utility.silver.language_model_utility import spawn_language_model_instance
from src.model.backend_control.dataclasses import create_or_load_database


def run_llm(main_switch: Event, current_switch: Event, llm_configuraiton: dict, input_queue: Queue, output_queue: Queue) -> None:
    """
    Function for running LLM instance.
    :param main_switch: Pool killswitch event.
    :param current_switch: Sepecific killswitch event.
    :param llm_configuration: Configuration to instantiate LLM.
    :param input_queue: Input queue.
    :param output_queue: Output queue.
    """
    llm = spawn_language_model_instance(llm_configuraiton)
    while not main_switch.wait(0.5) or current_switch(0.5):
        output_queue.put(llm.handle_query(input_queue.get()))


class LLMPool(object):
    """
    Controller class for handling LLM instances.
    """

    def __init__(self, queue_spawns: bool = False) -> None:
        """
        Initiation method.
        :param queue_spawns: Queue up instanciation until resources are available.
            Defaults to False.
        """
        # TODO: Add prioritization and potentially interrupt concept
        self.queue_spawns = queue_spawns
        self.main_switch = Event()
        self.threads = {}

    def kill_all(self) -> None:
        """
        Method for killing threads.
        """
        self.main_switch.set()

    def kill(self, target_thread: str) -> None:
        """
        Method for killing threads.
        :param target_thread: Thread to kill.
        """
        self.threads[target_thread]["switch"].set()

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

    def prepare_llm(self, llm_configuration: dict) -> str:
        """
        Method for preparing LLM instance.
        :param llm_configuration: LLM configuration.
        :return: Thread UUID.
        """
        uuid = uuid4()
        self.threads[uuid] = {
            "input": Queue(),
            "output": Queue(),
            "config": llm_configuration
        }
        return uuid

    def load_llm(self, target_thread: str) -> None:
        """
        Method for loading LLM.
        :param target_thread: Thread to start.
        """
        self.threads[target_thread]["switch"] = Event()
        self.threads[target_thread]["thread"] = Thread(
            target=run_llm,
            args=(
                self.main_switch,
                self.threads[target_thread]["switch"],
                self.threads[target_thread]["config"],
                self.threads[target_thread]["input"],
                self.threads[target_thread]["output"],
            )
        ).start()

    def unload_llm(self, target_thread: str) -> None:
        """
        Method for unloading LLM.
        :param target_thread: Thread to stop.
        """
        self.threads[target_thread]["switch"].set()
        self.threads[target_thread]["thread"].join()

    def query(self, target_thread: str, query: str) -> Optional[Any]:
        """
        Send query to target LLM.
        :param target_thread: Target thread.
        :param query: Query to send.
        :return: Response.
        """
        self.threads[target_thread]["input"].put(query)
        return self.threads[target_thread]["output"].get()