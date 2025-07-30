from dataclasses import dataclass

from uncountable.integration.job import JobArguments, WebhookJob, register_job
from uncountable.types import base_t, entity_t, job_definition_t


@dataclass(kw_only=True)
class InstrumentPayload:
    equipment_id: base_t.ObjectId


@register_job
class InstrumentExample(WebhookJob[InstrumentPayload]):
    def run(
        self, args: JobArguments, payload: InstrumentPayload
    ) -> job_definition_t.JobResult:
        equipment_data = args.client.get_entities_data(
            entity_type=entity_t.EntityType.EQUIPMENT,
            entity_ids=[payload.equipment_id],
        ).entity_details[0]

        # Load the instrument's connection details from the entity
        instrument_id = None
        for field in equipment_data.field_values:
            if field.field_ref_name == "ins_instrument_id":
                instrument_id = field.value

        if instrument_id is None:
            args.logger.log_error("Could not find instrument ID")
            return job_definition_t.JobResult(success=False)

        args.logger.log_info(f"Instrument ID: {instrument_id}")

        return job_definition_t.JobResult(success=True)

    @property
    def webhook_payload_type(self) -> type:
        return InstrumentPayload
