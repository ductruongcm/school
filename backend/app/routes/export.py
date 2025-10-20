from flask import Blueprint, send_file
from flask_jwt_extended import jwt_required
from app.utils import required_role, with_log, validate_input
from app.schemas import AcademicShowSchemas
from app.services import ExportService
from app.extensions import db
from app.repositories import Export_Repo

export_bp = Blueprint('export_bp', __name__, url_prefix='/api')
export_service = ExportService(db, Export_Repo)

@export_bp.get('/export/class_rooms/<int:class_room_id>')
@jwt_required()
@required_role('admin')
@with_log(True)
@validate_input(AcademicShowSchemas.UserList)
def export_user_to_xml(class_room_id: int, validated_data):
    validated_data['class_room_id'] = class_room_id
    output, class_name = export_service.handle_export_user_to_xml(validated_data)

    return send_file(output, 
                    as_attachment=True, 
                    download_name=f'danh_sach_lop_{class_name}.xlsx',
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")