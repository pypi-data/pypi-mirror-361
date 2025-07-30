import logging
from opentelemetry._logs import get_logger_provider
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk._logs import LoggingHandler

class LoggingInstrumentor(BaseInstrumentor):
    _original_get_logger = logging.getLogger
    
    def instrumentation_dependencies(self):
        return []
    
    def _instrument(self, **kwargs):
        logging.getLogger = self._instrumented_get_logger
        
    def _uninstrument(self, **kwargs):
        logging.getLogger = LoggingInstrumentor._original_get_logger

    def _instrumented_get_logger(self, *args, **kwargs):
        provider = get_logger_provider()
        handler = None
        logger: logging.RootLogger = LoggingInstrumentor._original_get_logger(*args, **kwargs)
        if provider is not None:
            handler = LoggingHandler(logger_provider=provider)
            logger.addHandler(handler)
        return logger
