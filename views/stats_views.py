from flask.views import MethodView
from flask import jsonify
from decorators.auth_decorators import roles_required, active_user_required
from services.stats_service import StatsService

stats_service = StatsService()

class StatsAPI(MethodView):
    """Endpoints para /api/stats"""

    @roles_required("admin", "moderator")
    @active_user_required
    def get(self):
        """Obtiene estadísticas generales de la aplicación"""
        stats = stats_service.get_stats()
        return jsonify(stats), 200