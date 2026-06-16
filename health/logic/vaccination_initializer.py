from health.logic.scheduler import generate_schedule
from health.logic.recommender import get_nutrition_recommendation
import logging

logger = logging.getLogger(__name__)

class VaccinationInitializer:
    @staticmethod
    def initialize_for_child(child):
        """
        Safely wraps the existing generate_schedule and get_nutrition_recommendation.
        Ensures it only runs when a child is successfully linked to a mother.
        Any exception raised here will roll back the entire transaction.
        """
        try:
            # Initialize vaccination schedule
            generate_schedule(child)
            
            # Initialize nutrition recommendation
            get_nutrition_recommendation(child)
        except Exception as e:
            logger.error(f"Failed to initialize vaccination/nutrition for child {child.id}: {e}")
            raise RuntimeError(f"Initialization failed: {str(e)}")
