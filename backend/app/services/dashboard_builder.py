"""
Dashboard Builder Service - Create and manage custom dashboards
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)


class DashboardBuilder:
    """Build and manage custom dashboards"""
    
    # In-memory storage (in production, use database)
    _dashboards: Dict[int, Dict[str, Any]] = {}
    _dashboard_counter = 0
    
    @classmethod
    def create_dashboard(
        cls,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        layout: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new dashboard"""
        try:
            cls._dashboard_counter += 1
            dashboard_id = cls._dashboard_counter
            
            dashboard = {
                "id": dashboard_id,
                "user_id": user_id,
                "name": name,
                "description": description or "",
                "layout": layout or {"type": "grid", "columns": 12, "rows": []},
                "widgets": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "is_public": False,
                "tags": []
            }
            
            cls._dashboards[dashboard_id] = dashboard
            
            logger.info(f"Created dashboard {dashboard_id} for user {user_id}")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            raise
    
    @classmethod
    def get_dashboard(
        cls,
        dashboard_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a dashboard by ID"""
        dashboard = cls._dashboards.get(dashboard_id)
        
        if dashboard:
            # Check permissions
            if user_id and dashboard["user_id"] != user_id and not dashboard["is_public"]:
                return None
        
        return dashboard
    
    @classmethod
    def update_dashboard(
        cls,
        dashboard_id: int,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update dashboard properties"""
        try:
            dashboard = cls._dashboards.get(dashboard_id)
            
            if not dashboard:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            if dashboard["user_id"] != user_id:
                raise PermissionError("Not authorized to update this dashboard")
            
            # Update allowed fields
            allowed_fields = ["name", "description", "layout", "is_public", "tags"]
            for field in allowed_fields:
                if field in updates:
                    dashboard[field] = updates[field]
            
            dashboard["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Updated dashboard {dashboard_id}")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            raise
    
    @classmethod
    def delete_dashboard(
        cls,
        dashboard_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Delete a dashboard"""
        try:
            dashboard = cls._dashboards.get(dashboard_id)
            
            if not dashboard:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            if dashboard["user_id"] != user_id:
                raise PermissionError("Not authorized to delete this dashboard")
            
            del cls._dashboards[dashboard_id]
            
            logger.info(f"Deleted dashboard {dashboard_id}")
            return {"success": True, "dashboard_id": dashboard_id}
            
        except Exception as e:
            logger.error(f"Error deleting dashboard: {e}")
            raise
    
    @classmethod
    def add_widget(
        cls,
        dashboard_id: int,
        user_id: int,
        widget: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a widget to a dashboard"""
        try:
            dashboard = cls._dashboards.get(dashboard_id)
            
            if not dashboard:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            if dashboard["user_id"] != user_id:
                raise PermissionError("Not authorized to modify this dashboard")
            
            # Generate widget ID
            widget_id = len(dashboard["widgets"]) + 1
            widget["id"] = widget_id
            widget["created_at"] = datetime.now(timezone.utc).isoformat()
            
            dashboard["widgets"].append(widget)
            dashboard["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Added widget {widget_id} to dashboard {dashboard_id}")
            return widget
            
        except Exception as e:
            logger.error(f"Error adding widget: {e}")
            raise
    
    @classmethod
    def update_widget(
        cls,
        dashboard_id: int,
        widget_id: int,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a widget in a dashboard"""
        try:
            dashboard = cls._dashboards.get(dashboard_id)
            
            if not dashboard:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            if dashboard["user_id"] != user_id:
                raise PermissionError("Not authorized to modify this dashboard")
            
            # Find and update widget
            widget = None
            for w in dashboard["widgets"]:
                if w["id"] == widget_id:
                    widget = w
                    break
            
            if not widget:
                raise ValueError(f"Widget {widget_id} not found")
            
            # Update widget
            for key, value in updates.items():
                widget[key] = value
            
            widget["updated_at"] = datetime.now(timezone.utc).isoformat()
            dashboard["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Updated widget {widget_id} in dashboard {dashboard_id}")
            return widget
            
        except Exception as e:
            logger.error(f"Error updating widget: {e}")
            raise
    
    @classmethod
    def remove_widget(
        cls,
        dashboard_id: int,
        widget_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Remove a widget from a dashboard"""
        try:
            dashboard = cls._dashboards.get(dashboard_id)
            
            if not dashboard:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            if dashboard["user_id"] != user_id:
                raise PermissionError("Not authorized to modify this dashboard")
            
            # Remove widget
            dashboard["widgets"] = [
                w for w in dashboard["widgets"]
                if w["id"] != widget_id
            ]
            
            dashboard["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Removed widget {widget_id} from dashboard {dashboard_id}")
            return {"success": True, "widget_id": widget_id}
            
        except Exception as e:
            logger.error(f"Error removing widget: {e}")
            raise
    
    @classmethod
    def list_dashboards(
        cls,
        user_id: int,
        include_public: bool = True
    ) -> List[Dict[str, Any]]:
        """List dashboards for a user"""
        dashboards = []
        
        for dashboard in cls._dashboards.values():
            if dashboard["user_id"] == user_id:
                dashboards.append(dashboard)
            elif include_public and dashboard["is_public"]:
                dashboards.append(dashboard)
        
        return dashboards
    
    @classmethod
    def duplicate_dashboard(
        cls,
        dashboard_id: int,
        user_id: int,
        new_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Duplicate an existing dashboard"""
        try:
            original = cls._dashboards.get(dashboard_id)
            
            if not original:
                raise ValueError(f"Dashboard {dashboard_id} not found")
            
            # Check if user can access the dashboard
            if original["user_id"] != user_id and not original["is_public"]:
                raise PermissionError("Not authorized to duplicate this dashboard")
            
            # Create duplicate
            duplicate = cls.create_dashboard(
                user_id=user_id,
                name=new_name or f"{original['name']} (Copy)",
                description=original["description"],
                layout=original["layout"].copy()
            )
            
            # Copy widgets
            for widget in original["widgets"]:
                widget_copy = widget.copy()
                widget_copy.pop("id", None)
                widget_copy.pop("created_at", None)
                cls.add_widget(duplicate["id"], user_id, widget_copy)
            
            logger.info(f"Duplicated dashboard {dashboard_id} to {duplicate['id']}")
            return duplicate
            
        except Exception as e:
            logger.error(f"Error duplicating dashboard: {e}")
            raise
    
    @classmethod
    def export_dashboard(
        cls,
        dashboard_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Export dashboard configuration as JSON"""
        try:
            dashboard = cls.get_dashboard(dashboard_id, user_id)
            
            if not dashboard:
                raise ValueError(f"Dashboard {dashboard_id} not found or not accessible")
            
            # Create export data
            export_data = {
                "name": dashboard["name"],
                "description": dashboard["description"],
                "layout": dashboard["layout"],
                "widgets": dashboard["widgets"],
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "version": "1.0"
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting dashboard: {e}")
            raise
    
    @classmethod
    def import_dashboard(
        cls,
        user_id: int,
        import_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Import dashboard from JSON configuration"""
        try:
            dashboard = cls.create_dashboard(
                user_id=user_id,
                name=import_data.get("name", "Imported Dashboard"),
                description=import_data.get("description"),
                layout=import_data.get("layout")
            )
            
            # Import widgets
            for widget in import_data.get("widgets", []):
                widget_copy = widget.copy()
                widget_copy.pop("id", None)
                widget_copy.pop("created_at", None)
                widget_copy.pop("updated_at", None)
                cls.add_widget(dashboard["id"], user_id, widget_copy)
            
            logger.info(f"Imported dashboard as {dashboard['id']}")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error importing dashboard: {e}")
            raise
