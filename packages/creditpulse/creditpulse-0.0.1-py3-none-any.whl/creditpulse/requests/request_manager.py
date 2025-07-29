"""
Clase para hacer exponential back of de algun callback
"""
import time
from abc import ABC, abstractmethod
import requests




class RequestActionManager(ABC):
    """Abstract base class for handling HTTP requests with decision logic"""

    @abstractmethod
    def on_execute(self) -> requests.Response:
        """Execute the HTTP request and return the response"""

    @abstractmethod
    def success_callback(self, response: requests.Response) -> None:
        """Handle successful response"""

    @abstractmethod
    def error_callback(self, response: requests.Response) -> None:
        """Handle error response"""

    @abstractmethod
    def is_request_successful(self, response: requests.Response) -> bool:
        """Determine if the request was successful"""


class RequestManager:
    """
        Maneja los request para poder hacer un exponential backoff
    """

    def __init__(self, manager: RequestActionManager, max_retries: int = 10):
        """

        :param decision: Objeto que ayuda a tomar decisiones para el exponential backoff
        :param max_retries:
        """

        self.initial_delay = 1.0
        self.max_delay = 60.0
        self.backoff_factor = 1.5
        self.max_retries = max_retries
        self.manager = manager

        # State variables
        self.current_delay = self.initial_delay
        self.retry_count = 0
        self.running = False

    def reset_delay(self):
        """
        Re-inicia el delay
        :return:
        """
        self.current_delay = self.initial_delay
        self.retry_count = 0

    def increase_delay(self):
        """
        Aumenta el delay cada
        :return:
        """
        self.current_delay = min(self.current_delay * self.backoff_factor, self.max_delay)
        self.retry_count += 1

    def should_continue(self) -> bool:
        """
        Determina si debe seguir ejecutando la accion
        :return:
        """

        if not self.running:
            return False
        if self.max_retries is not None and self.retry_count >= self.max_retries:
            return False
        return True

    def stop(self):
        """
        Detiene la ejecusion fozosamente
        :return:
        """
        self.running = False

    def start(self):
        """
        Inicia el proceso de llamada con backoof
        :return:
        """
        self.running = True
        while self.should_continue():
            try:
                response = self.manager.on_execute()

                if self.manager.is_request_successful(response=response):
                    self.stop()
                    self.manager.success_callback(response=response)
                    self.reset_delay()
                else:
                    self.manager.error_callback(response=response)
                    self.increase_delay()

            except requests.exceptions.RequestException:
                self.increase_delay()
            except KeyboardInterrupt:
                self.stop()
            except Exception:
                self.increase_delay()
            if self.should_continue():
                time.sleep(self.current_delay)
