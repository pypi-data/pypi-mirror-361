from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter


class FilterLogsExporter(OTLPLogExporter):
    def export(self, log_records):
        filtered_log_records = []
        ignored_scopes = {"opentelemetry.attributes"}
        for record in log_records:
            if hasattr(record, "instrumentation_scope") and getattr(record.instrumentation_scope, "name", None) in ignored_scopes:
                continue
            filtered_log_records.append(record)

        return super().export(filtered_log_records)
    
    
