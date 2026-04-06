import logging
from patents.models import PatentApplication

logger = logging.getLogger(__name__)

class SyncService:

    def trigger(self, application):
        try:
            # Flag as priority
            application.priority = True
            application.save(update_fields=["priority"])
            logger.info(f"Priority sync set for {application.application_number}")

            # Here, actual sync code would run
            logger.info(f"Sync triggered for {application.application_number}")

            # Reset priority after sync
            application.priority = False
            application.save(update_fields=["priority"])
            logger.info(f"Priority reset for {application.application_number}")

        except Exception as e:
            logger.error(f"Error syncing {application.application_number}: {str(e)}")